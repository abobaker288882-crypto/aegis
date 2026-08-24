import tempfile
import unittest
from pathlib import Path

from build_project_graph import (
    discover_projects,
    inspect_project,
    project_label,
    remove_stale_generated,
    safe_slug,
    write_if_changed,
)


class SafeSlugTests(unittest.TestCase):
    def test_sanitises_unsafe_characters(self) -> None:
        self.assertEqual(safe_slug("my app: v2?"), "my app- v2")

    def test_empty_value_falls_back(self) -> None:
        self.assertEqual(safe_slug("///"), "project")


class ProjectLabelTests(unittest.TestCase):
    def test_duplicate_base_names_get_parent_suffix(self) -> None:
        from collections import Counter

        used: Counter = Counter()
        roots = [Path("/tmp")]
        first = project_label(Path("/tmp/site"), roots, used)
        second = project_label(Path("/other/site"), roots, used)
        self.assertEqual(first, "site")
        self.assertEqual(second, "site — other")


class DiscoverProjectsTests(unittest.TestCase):
    def test_discovers_git_repo_and_excludes_nested_and_vault(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            vault = root / "Second Brain"
            vault.mkdir()
            repo = root / "demo"
            (repo / ".git").mkdir(parents=True)
            (repo / "package.json").write_text("{}")
            nested = repo / "nested"
            (nested / ".git").mkdir(parents=True)
            excluded = repo / "node_modules"
            (excluded / "package.json").parent.mkdir(parents=True)
            (excluded / "package.json").write_text("{}")

            projects = discover_projects([root], vault)
            # A nested git repo is an independent project (mirrors real
            # workspaces); excluded dirs and the vault itself are not.
            self.assertIn(repo.resolve(), projects)
            self.assertIn(nested.resolve(), projects)
            self.assertNotIn(excluded.resolve(), projects)
            self.assertNotIn(vault.resolve(), projects)


class InspectProjectTests(unittest.TestCase):
    def test_reports_git_state_and_sanitises_remote_credentials(self) -> None:
        import subprocess

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            run = lambda *args: subprocess.run(
                ["git", "-C", str(repo), *args], check=True, capture_output=True
            )
            run("init", "-q")
            run("config", "user.email", "t@example.com")
            run("config", "user.name", "t")
            (repo / "package.json").write_text('{"dependencies": {"next": "1"}}')
            run("add", ".")
            run("commit", "-qm", "init")
            run("remote", "add", "origin", "https://user:secret@example.com/x.git")

            info = inspect_project(repo)

            current_branch = run("branch", "--show-current").stdout.decode().strip()
            self.assertEqual(info["branch"], current_branch)
            self.assertIn("init", info["commit"])
            self.assertNotIn("secret", info["remote"])
            self.assertIn("example.com/x.git", info["remote"])
            self.assertIn("Next.js", info["technologies"])
            self.assertIn("package.json", info["manifests"])


class WriteIfChangedTests(unittest.TestCase):
    def test_second_write_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "note.md"
            write_if_changed(path, "same")
            first = path.stat().st_mtime_ns
            write_if_changed(path, "same")
            self.assertEqual(path.stat().st_mtime_ns, first)
            write_if_changed(path, "changed")
            self.assertEqual(path.read_text(), "changed")


class RemoveStaleGeneratedTests(unittest.TestCase):
    def test_removes_only_stale_generated_notes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            keep_generated = folder / "keep.md"
            keep_generated.write_text("---\ntype: project\n---\n")
            stale_generated = folder / "stale.md"
            stale_generated.write_text("---\ntype: project\n---\n")
            manual = folder / "manual.md"
            manual.write_text("---\ntype: journal\n---\n")
            plain = folder / "plain.md"
            plain.write_text("no frontmatter")

            remove_stale_generated(folder, {"keep.md"}, "project")

            self.assertTrue(keep_generated.exists())
            self.assertFalse(stale_generated.exists())
            self.assertTrue(manual.exists())
            self.assertTrue(plain.exists())


if __name__ == "__main__":
    unittest.main()
