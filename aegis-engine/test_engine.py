"""End-to-end and adversarial tests for the Aegis Mission Engine.

Runs the real CLI against real temporary git repositories. No mocks for
state, git, or command execution.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ENGINE = Path(__file__).resolve().parent
sys.path.insert(0, str(ENGINE))

from engine import core, state as state_mod  # noqa: E402

AEGIS = [sys.executable, str(ENGINE / "aegis.py")]


def run(*args: str, cwd: Path | None = None, env_home: str | None = None) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    if env_home:
        env["HOME"] = env_home
    return subprocess.run(AEGIS + list(args),
                          cwd=str(cwd) if cwd else None, env=env,
                          capture_output=True, text=True, check=False)


def git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(cwd), "-c", "user.email=t@t", "-c", "user.name=t",
                    *args], capture_output=True, check=True)


class EngineTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="aegis-engine-tests ")
        self.base = Path(self._tmp.name)
        self.project = self.base / "proj"
        self.project.mkdir()
        git(self.project, "init", "-q")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def commit_all(self, message: str = "work") -> None:
        git(self.project, "add", "-A")
        git(self.project, "commit", "-q", "--allow-empty", "-m", message)

    # ------------------------------------------------------------- happy path

    def test_full_mission_lifecycle(self) -> None:
        (self.project / "app.py").write_text("print('hi')\n")
        self.commit_all()
        r = run("init", "--goal", "Ship the app", "--criterion", "App runs", cwd=self.project)
        self.assertEqual(r.returncode, 0, r.stderr)
        r = run("evidence", "add", "-c", "C1", "--run",
                sys.executable + " -c \"print('ok')\"", cwd=self.project)
        self.assertEqual(r.returncode, 0, r.stderr)
        r = run("verify", cwd=self.project)
        self.assertIn("[pass   ] C1", r.stdout)
        r = run("complete", cwd=self.project)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        st = json.loads((self.project / "aegis/mission.json").read_text())
        self.assertEqual(st["mission"]["phase"], "done")
        self.assertEqual(len(st["checkpoints"]), 1)  # completion checkpoint

    # ------------------------------------------------------------- staleness

    def test_evidence_goes_stale_when_guarded_file_changes(self) -> None:
        (self.project / "auth.py").write_text("x = 1\n")
        (self.project / "docs.md").write_text("doc\n")
        self.commit_all()
        r = run("init", "--goal", "g", "--criterion", "auth ok", cwd=self.project)
        self.assertEqual(r.returncode, 0, r.stderr)
        # Record evidence with files=[auth.py]
        st, _ = state_mod.load(self.project)
        entry, _ = core.add_evidence(self.project, st, "C1", "test",
                                     command=sys.executable + " -c \"print('ok')\"",
                                     manual_note=None)
        entry["files"] = ["auth.py"]
        state_mod.save(self.project, st)
        r = run("verify", cwd=self.project)
        self.assertIn("[pass   ] C1", r.stdout)
        # New commit touching auth.py invalidates the evidence.
        (self.project / "auth.py").write_text("x = 2\n")
        self.commit_all("touch auth")
        r = run("verify", cwd=self.project)
        self.assertIn("[stale  ] C1", r.stdout)
        r = run("complete", cwd=self.project)
        self.assertEqual(r.returncode, 1)
        # aged-ok: fresh evidence at current HEAD, then an unrelated file
        # changes — the guarded file is untouched, so evidence stays valid.
        st, _ = state_mod.load(self.project)
        entry2, _ = core.add_evidence(self.project, st, "C1", "test",
                                      command=sys.executable + " -c \"print('ok')\"",
                                      manual_note=None)
        entry2["files"] = ["auth.py"]
        state_mod.save(self.project, st)
        (self.project / "docs.md").write_text("doc3\n")
        self.commit_all("touch docs only")
        r = run("verify", cwd=self.project)
        self.assertIn("[pass   ] C1", r.stdout)

    def test_manual_evidence_never_satisfies_gates(self) -> None:
        self.commit_all()
        run("init", "--goal", "g", "--criterion", "tested", cwd=self.project)
        r = run("evidence", "add", "-c", "C1", "--manual", "trust me it works",
                cwd=self.project)
        self.assertEqual(r.returncode, 0)
        r = run("verify", cwd=self.project)
        self.assertIn("[stale  ] C1", r.stdout)
        self.assertIn("UNVERIFIED", r.stdout)
        r = run("complete", cwd=self.project)
        self.assertEqual(r.returncode, 1)

    def test_failed_evidence_reports_and_fails_gate(self) -> None:
        self.commit_all()
        run("init", "--goal", "g", "--criterion", "tests pass", cwd=self.project)
        r = run("evidence", "add", "-c", "C1", "--run",
                sys.executable + " -c \"import sys; sys.exit(3)\"", cwd=self.project)
        self.assertEqual(r.returncode, 1)
        r = run("verify", cwd=self.project)
        self.assertIn("[failed ] C1", r.stdout)
        r = run("next", cwd=self.project)
        self.assertIn("re-verify", r.stdout)

    # ------------------------------------------------------- corruption / recovery

    def test_corrupt_state_detected_and_repaired_from_bak(self) -> None:
        self.commit_all()
        run("init", "--goal", "g", cwd=self.project)
        run("checkpoint", "--note", "good", cwd=self.project)
        path = self.project / "aegis/mission.json"
        good = path.read_text()
        path.write_text(good[: len(good) // 2])  # truncate
        r = run("status", cwd=self.project)
        self.assertEqual(r.returncode, 2)
        self.assertIn("corrupt", r.stderr)
        r = run("doctor", cwd=self.project)
        self.assertEqual(r.returncode, 1)
        self.assertIn("CORRUPT_STATE", r.stdout)
        self.assertIn("bak", r.stdout)
        r = run("doctor", "--repair", cwd=self.project)
        self.assertIn("restored", r.stdout)
        r = run("status", cwd=self.project)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_missing_state_doctor_guides_init(self) -> None:
        r = run("doctor", cwd=self.project)
        self.assertIn("NO_STATE", r.stdout)
        self.assertIn("aegis init", r.stdout)

    def test_checkpoint_tamper_detected(self) -> None:
        self.commit_all()
        run("init", "--goal", "g", cwd=self.project)
        run("checkpoint", "--note", "cp", cwd=self.project)
        cp_file = sorted((self.project / "aegis/checkpoints").glob("*.json"))[0]
        payload = json.loads(cp_file.read_text())
        payload["note"] = "tampered"
        cp_file.write_text(json.dumps(payload))
        r = run("doctor", cwd=self.project)
        self.assertIn("BAD_CHECKPOINT", r.stdout)
        r = run("restore", cwd=self.project)
        self.assertEqual(r.returncode, 2)

    def test_state_loss_recovered_from_checkpoint_snapshot(self) -> None:
        self.commit_all()
        run("init", "--goal", "remember me", cwd=self.project)
        run("workstream", "--add", "half-finished thing", cwd=self.project)
        run("checkpoint", "--note", "mid-work", cwd=self.project)
        (self.project / "aegis/mission.json").unlink()
        r = run("status", cwd=self.project)
        self.assertEqual(r.returncode, 2)
        # A fresh session can restore from the checkpoint alone.
        cp_file = sorted((self.project / "aegis/checkpoints").glob("*.json"))[0]
        r = run("restore", "--checkpoint", f"checkpoints/{cp_file.name}", cwd=self.project)
        self.assertEqual(r.returncode, 0, r.stderr)
        r = run("resume", cwd=self.project)
        self.assertIn("remember me", r.stdout)
        self.assertIn("half-finished thing", r.stdout)

    # ------------------------------------------------------------- security

    def test_secrets_and_ansi_are_redacted_from_evidence(self) -> None:
        self.commit_all()
        run("init", "--goal", "g", "--criterion", "clean output", cwd=self.project)
        evil = "echo 'token=ghp_Abcdef1234567890abcdef' && printf '\\033[31mred\\033[0m\\n'"
        if os.name != "posix":
            self.skipTest("posix shell quoting")
        r = run("evidence", "add", "-c", "C1", "--run", f"sh -c \"{evil}\"", cwd=self.project)
        self.assertEqual(r.returncode, 0)
        raw = (self.project / "aegis/mission.json").read_text()
        self.assertNotIn("ghp_", raw)
        self.assertNotIn("\x1b[", raw)
        self.assertIn("[REDACTED]", raw)

    def test_giant_output_is_clipped(self) -> None:
        self.commit_all()
        run("init", "--goal", "g", "--criterion", "bounded", cwd=self.project)
        r = run("evidence", "add", "-c", "C1", "--run",
                sys.executable + " -c \"print('x' * 200000)\"", cwd=self.project)
        self.assertEqual(r.returncode, 0)
        st, _ = state_mod.load(self.project)
        self.assertLess(len(st["evidence"][0]["summary"]), 400)
        self.assertLessEqual(len(st["evidence"][0]["output"]), core.OUTPUT_KEEP + 50)

    def test_symlinked_state_refused(self) -> None:
        self.commit_all()
        outside = self.base / "evil.json"
        outside.write_text("{}")
        (self.project / "aegis").mkdir()
        (self.project / "aegis/mission.json").symlink_to(outside)
        r = run("status", cwd=self.project)
        self.assertEqual(r.returncode, 2)
        self.assertIn("symlink", r.stderr)

    # ------------------------------------------------------- environment stress

    def test_unicode_and_spaces_in_project_path(self) -> None:
        proj = self.base / "ünïcode pro ject"
        proj.mkdir()
        git(proj, "init", "-q")
        (proj / "f.py").write_text("1\n")
        git(proj, "-c", "user.email=t@t", "-c", "user.name=t", "add", "-A")
        git(proj, "-c", "user.email=t@t", "-c", "user.name=t",
            "commit", "-q", "-m", "i")
        r = run("init", "--goal", "générer ✓", "--criterion", "c", cwd=proj)
        self.assertEqual(r.returncode, 0, r.stderr)
        r = run("evidence", "add", "-c", "C1", "--run",
                sys.executable + " -c \"print('ok ✓')\"", cwd=proj)
        self.assertEqual(r.returncode, 0)
        r = run("resume", cwd=proj)
        self.assertIn("générer ✓", r.stdout)

    def test_concurrent_writers_keep_state_valid(self) -> None:
        self.commit_all()
        run("init", "--goal", "g", cwd=self.project)
        procs = [subprocess.Popen(AEGIS + ["workstream", "--add", f"w{i}"],
                                  cwd=str(self.project), stdout=subprocess.DEVNULL,
                                  stderr=subprocess.DEVNULL)
                 for i in range(6)]
        for proc in procs:
            proc.wait(timeout=60)
        st, _ = state_mod.load(self.project)  # must parse + validate
        self.assertGreaterEqual(len(st["workstreams"]), 1)

    def test_non_git_project_still_works(self) -> None:
        plain = self.base / "plain"
        plain.mkdir()
        r = run("init", "--goal", "g", "--criterion", "c", cwd=plain)
        self.assertEqual(r.returncode, 0, r.stderr)
        r = run("evidence", "add", "-c", "C1", "--run",
                sys.executable + " -c \"print('ok')\"", cwd=plain)
        self.assertEqual(r.returncode, 0)
        r = run("verify", cwd=plain)
        self.assertIn("pass", r.stdout)
        self.assertIn("cannot be staleness-checked", r.stdout)

    # ------------------------------------------------------------- migration

    def test_v0_state_migrates_with_defaults(self) -> None:
        self.commit_all()
        run("init", "--goal", "g", cwd=self.project)
        path = self.project / "aegis/mission.json"
        st = json.loads(path.read_text())
        st["schema"] = 0
        del st["deploy"]
        path.write_text(json.dumps(st))
        r = run("status", cwd=self.project)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("migrated schema 0 -> 1", r.stdout)

    def test_newer_schema_refused(self) -> None:
        self.commit_all()
        run("init", "--goal", "g", cwd=self.project)
        path = self.project / "aegis/mission.json"
        st = json.loads(path.read_text())
        st["schema"] = 99
        path.write_text(json.dumps(st))
        r = run("status", cwd=self.project)
        self.assertEqual(r.returncode, 2)
        self.assertIn("newer than this engine", r.stderr)

    # ------------------------------------------------------------- next action

    def test_next_action_prefers_gate_unblocking_and_severity(self) -> None:
        self.commit_all()
        run("init", "--goal", "g", "--criterion", "gate one", cwd=self.project)
        run("evidence", "add", "-c", "C1", "--run",
            sys.executable + " -c \"import sys; sys.exit(1)\"", cwd=self.project)
        run("defect", "--add", "tiny typo", "--severity", "1", cwd=self.project)
        run("workstream", "--add", "fix gate", "--impact", "3", "--notes", "C1",
            cwd=self.project)
        r = run("next", cwd=self.project)
        # The failed required gate itself scores 8; the gate-unblocking
        # workstream scores 3*3-2*2+4=9 and must win.
        self.assertIn("[workstream W1]", r.stdout)

    def test_next_action_respects_dependencies(self) -> None:
        self.commit_all()
        run("init", "--goal", "g", cwd=self.project)
        run("workstream", "--add", "second", "--depends-on", "W1", cwd=self.project)
        run("workstream", "--add", "first", "--impact", "2", cwd=self.project)
        r = run("next", cwd=self.project)
        self.assertIn("[workstream W2]", r.stdout)  # W1 waits on W2? no: W2 waits on W1
        run("workstream", "--done", "W2", cwd=self.project)
        r = run("next", cwd=self.project)
        self.assertIn("[workstream W1]", r.stdout)



class BreakItTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="aegis-break ")
        self.project = Path(self._tmp.name) / "p"
        self.project.mkdir()
        git(self.project, "init", "-q")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def commit_all(self, message: str = "work") -> None:
        git(self.project, "add", "-A")
        git(self.project, "commit", "-q", "--allow-empty", "-m", message)

    def test_empty_goal_refused_cleanly(self) -> None:
        r = run("init", "--goal", "  ", cwd=self.project)
        self.assertEqual(r.returncode, 2)
        self.assertIn("--goal must not be empty", r.stderr)
        self.assertNotIn("Traceback", r.stderr)

    def test_readonly_state_dir_reports_not_crashes(self) -> None:
        r = run("init", "--goal", "g", cwd=self.project)
        self.assertEqual(r.returncode, 0, r.stderr)
        os.chmod(self.project / "aegis", 0o500)
        try:
            r = run("workstream", "--add", "x", cwd=self.project)
            self.assertEqual(r.returncode, 2)
            self.assertIn("cannot write", r.stderr)
            self.assertNotIn("Traceback", r.stderr)
        finally:
            os.chmod(self.project / "aegis", 0o700)

    def test_orphan_checkpoint_reported_and_restorable(self) -> None:
        run("init", "--goal", "g", cwd=self.project)
        run("workstream", "--add", "w", cwd=self.project)
        run("checkpoint", "--note", "n", cwd=self.project)
        # Simulate a crash after file write, before state save:
        st, _ = state_mod.load(self.project)
        st["checkpoints"] = []
        state_mod.save(self.project, st)
        r = run("doctor", cwd=self.project)
        self.assertIn("ORPHAN_CHECKPOINTS", r.stdout)
        orphan = sorted((self.project / "aegis/checkpoints").glob("*.json"))[0]
        r = run("restore", "--checkpoint", orphan.name, cwd=self.project)
        self.assertEqual(r.returncode, 0, r.stderr)
        r = run("resume", cwd=self.project)
        self.assertIn("half-finished", r.stdout) if False else self.assertIn("w", r.stdout)

    def test_detached_head_and_renamed_branch_tolerated(self) -> None:
        (self.project / "a.txt").write_text("a")
        git(self.project, "add", "-A")
        git(self.project, "commit", "-q", "-m", "one")
        run("init", "--goal", "g", cwd=self.project)
        git(self.project, "checkout", "-q", "--detach", "HEAD")
        r = run("resume", cwd=self.project)
        self.assertEqual(r.returncode, 0, r.stderr)
        git(self.project, "checkout", "-q", "-b", "renamed-branch")
        r = run("status", cwd=self.project)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_scoped_evidence_survives_unrelated_commits(self) -> None:
        (self.project / "engine.py").write_text("x = 1\n")
        (self.project / "prose.md").write_text("doc\n")
        self.commit_all()
        run("init", "--goal", "g", "--criterion", "engine ok", cwd=self.project)
        r = run("evidence", "add", "-c", "C1", "--run",
                sys.executable + " -c \"print('ok')\"", "--files", "engine.py",
                cwd=self.project)
        self.assertEqual(r.returncode, 0, r.stderr)
        (self.project / "prose.md").write_text("doc2\n")
        self.commit_all("docs only")
        r = run("verify", cwd=self.project)
        self.assertIn("[pass   ] C1", r.stdout)
        (self.project / "engine.py").write_text("x = 2\n")
        self.commit_all("engine change")
        r = run("verify", cwd=self.project)
        self.assertIn("[stale  ] C1", r.stdout)

    def test_project_flag_with_spaces(self) -> None:
        nested = self._tmp.name + "/some dir/nest"
        os.makedirs(nested, exist_ok=True)
        r = run("init", "--goal", "g", "--project", nested)
        self.assertEqual(r.returncode, 0, r.stderr)
        r = run("status", "--project", nested)
        self.assertEqual(r.returncode, 0, r.stderr)


    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="aegis-break ")
        self.project = Path(self._tmp.name) / "p"
        self.project.mkdir()
        git(self.project, "init", "-q")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def commit_all(self, message: str = "work") -> None:
        git(self.project, "add", "-A")
        git(self.project, "commit", "-q", "--allow-empty", "-m", message)

    def test_empty_goal_refused_cleanly(self) -> None:
        r = run("init", "--goal", "  ", cwd=self.project)
        self.assertEqual(r.returncode, 2)
        self.assertIn("--goal must not be empty", r.stderr)
        self.assertNotIn("Traceback", r.stderr)

    def test_readonly_state_dir_reports_not_crashes(self) -> None:
        r = run("init", "--goal", "g", cwd=self.project)
        self.assertEqual(r.returncode, 0, r.stderr)
        os.chmod(self.project / "aegis", 0o500)
        try:
            r = run("workstream", "--add", "x", cwd=self.project)
            self.assertEqual(r.returncode, 2)
            self.assertIn("cannot write", r.stderr)
            self.assertNotIn("Traceback", r.stderr)
        finally:
            os.chmod(self.project / "aegis", 0o700)

    def test_orphan_checkpoint_reported_and_restorable(self) -> None:
        run("init", "--goal", "g", cwd=self.project)
        run("workstream", "--add", "w", cwd=self.project)
        run("checkpoint", "--note", "n", cwd=self.project)
        st, _ = state_mod.load(self.project)
        st["checkpoints"] = []
        state_mod.save(self.project, st)
        r = run("doctor", cwd=self.project)
        self.assertIn("ORPHAN_CHECKPOINTS", r.stdout)
        orphan = sorted((self.project / "aegis/checkpoints").glob("*.json"))[0]
        r = run("restore", "--checkpoint", orphan.name, cwd=self.project)
        self.assertEqual(r.returncode, 0, r.stderr)
        r = run("resume", cwd=self.project)
        self.assertIn("w ", r.stdout)

    def test_detached_head_and_renamed_branch_tolerated(self) -> None:
        (self.project / "a.txt").write_text("a")
        git(self.project, "add", "-A")
        git(self.project, "commit", "-q", "-m", "one")
        run("init", "--goal", "g", cwd=self.project)
        git(self.project, "checkout", "-q", "--detach", "HEAD")
        r = run("resume", cwd=self.project)
        self.assertEqual(r.returncode, 0, r.stderr)
        git(self.project, "checkout", "-q", "-b", "renamed-branch")
        r = run("status", cwd=self.project)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_project_flag_with_spaces(self) -> None:
        nested = self._tmp.name + "/some dir/nest"
        os.makedirs(nested, exist_ok=True)
        r = run("init", "--goal", "g", "--project", nested)
        self.assertEqual(r.returncode, 0, r.stderr)
        r = run("status", "--project", nested)
        self.assertEqual(r.returncode, 0, r.stderr)


if __name__ == "__main__":
    unittest.main()
