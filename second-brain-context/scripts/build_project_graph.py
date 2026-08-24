#!/usr/bin/env python3
"""Build a safe Obsidian project graph that routes to real local source folders."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path


EXCLUDED_DIRS = {
    ".cache", ".git", ".gradle", ".next", ".pnpm-store", ".swiftpm",
    ".turbo", ".venv", "DerivedData", "Pods", "__pycache__", "build",
    "coverage", "dist", "node_modules", "target", "vendor",
}
PROJECT_MARKERS = {
    "Cargo.toml", "Package.swift", "go.mod", "package.json", "pyproject.toml",
    "requirements.txt",
}
EXTENSION_TECH = {
    ".dart": "Dart", ".go": "Go", ".js": "JavaScript", ".jsx": "React",
    ".kt": "Kotlin", ".php": "PHP", ".py": "Python", ".rb": "Ruby",
    ".rs": "Rust", ".sql": "SQL", ".swift": "Swift", ".ts": "TypeScript", ".tsx": "React",
}
SAFE_DEP_TECH = {
    "@supabase/supabase-js": "Supabase", "@vercel/analytics": "Vercel",
    "expo": "Expo", "next": "Next.js", "react": "React",
    "react-native": "React Native", "svelte": "Svelte", "vue": "Vue",
}


def run_git(project: Path, *args: str) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(project), *args], check=False, capture_output=True,
            text=True, timeout=4,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return result.stdout.strip() if result.returncode == 0 else ""


def is_excluded(path: Path) -> bool:
    return any(part in EXCLUDED_DIRS for part in path.parts)


def keep_directory(name: str) -> bool:
    return name not in EXCLUDED_DIRS and not name.endswith((".app", ".dSYM"))


def discover_projects(roots: list[Path], vault: Path) -> list[Path]:
    candidates: set[Path] = set()
    for root in roots:
        if not root.is_dir():
            continue
        for current, dirs, files in os.walk(root):
            current_path = Path(current)
            dirs[:] = [
                item for item in dirs
                if keep_directory(item)
                and (current_path / item).resolve() != vault.resolve()
            ]
            depth = len(current_path.relative_to(root).parts)
            has_marker = bool(PROJECT_MARKERS.intersection(files))
            has_xcode = any(item.endswith((".xcodeproj", ".xcworkspace")) for item in dirs)
            has_git = ".git" in os.listdir(current_path)
            if has_git or has_marker or has_xcode:
                candidates.add(current_path.resolve())
                if has_git:
                    dirs[:] = [item for item in dirs if item != ".git"]
            if depth >= 6:
                dirs[:] = []

    git_roots = sorted(path for path in candidates if (path / ".git").exists())
    result: list[Path] = []
    for candidate in sorted(candidates):
        containing = [root for root in git_roots if root != candidate and root in candidate.parents]
        if containing and not (candidate / ".git").exists():
            continue
        result.append(candidate)
    return result


def safe_slug(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._ -]+", "-", value).strip(" .-")
    return cleaned or "project"


def project_label(project: Path, roots: list[Path], used: Counter) -> str:
    base = safe_slug(project.name)
    used[base] += 1
    if used[base] == 1:
        return base
    parent = safe_slug(project.parent.name)
    return f"{base} — {parent}"


def inspect_project(project: Path) -> dict:
    extensions: Counter[str] = Counter()
    manifests: list[str] = []
    technologies: set[str] = set()
    file_count = 0
    for current, dirs, files in os.walk(project):
        current_path = Path(current)
        if current_path != project and (current_path / ".git").exists():
            dirs[:] = []
            continue
        dirs[:] = [item for item in dirs if keep_directory(item)]
        if current_path.name.lower() == "supabase" or any(item.lower() == "supabase" for item in dirs):
            technologies.add("Supabase")
        if "vercel.json" in files:
            technologies.add("Vercel")
        if "Dockerfile" in files or "docker-compose.yml" in files or "docker-compose.yaml" in files:
            technologies.add("Docker")
        for dirname in dirs:
            if dirname.endswith((".xcodeproj", ".xcworkspace")) and len(manifests) < 30:
                manifests.append(str((current_path / dirname).relative_to(project)))
        for filename in files:
            file_count += 1
            path = current_path / filename
            rel = path.relative_to(project)
            if filename in PROJECT_MARKERS or filename.endswith((".xcodeproj", ".xcworkspace")):
                if len(manifests) < 30:
                    manifests.append(str(rel))
            if filename == "package.json":
                try:
                    package = json.loads(path.read_text(encoding="utf-8"))
                    deps = set(package.get("dependencies", {})) | set(package.get("devDependencies", {}))
                    for dependency, technology in SAFE_DEP_TECH.items():
                        if dependency in deps:
                            technologies.add(technology)
                except (OSError, UnicodeDecodeError, json.JSONDecodeError):
                    pass
            suffix = path.suffix.lower()
            if suffix in EXTENSION_TECH:
                extensions[suffix] += 1
            if file_count >= 100_000:
                break
        if file_count >= 100_000:
            break

    for suffix, count in extensions.items():
        if count:
            technologies.add(EXTENSION_TECH[suffix])
    if any(item.endswith("package.json") for item in manifests):
        technologies.add("Node.js")
    if any(item.suffix == ".xcodeproj" for item in project.iterdir()):
        technologies.update({"iOS", "Xcode"})

    remote = run_git(project, "remote", "get-url", "origin")
    if remote and re.search(r"https?://[^/]+@", remote):
        remote = re.sub(r"(https?://)[^/]+@", r"\1", remote)
    return {
        "branch": run_git(project, "branch", "--show-current"),
        "commit": run_git(project, "log", "-1", "--format=%h %s"),
        "file_count": file_count,
        "manifests": sorted(manifests),
        "remote": remote,
        "technologies": sorted(technologies),
    }


def write_if_changed(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return
    path.write_text(content, encoding="utf-8")


def remove_stale_generated(folder: Path, expected_names: set[str], generated_type: str) -> None:
    if not folder.is_dir():
        return
    marker = f"type: {generated_type}"
    for path in folder.glob("*.md"):
        if path.name in expected_names:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if content.startswith("---\n") and marker in content.split("---", 2)[1]:
            path.unlink()


def root_for(project: Path, roots: list[Path]) -> Path:
    matches = [root for root in roots if root == project or root in project.parents]
    return max(matches, key=lambda item: len(item.parts))


def build_graph(vault: Path, roots: list[Path]) -> int:
    projects = discover_projects(roots, vault)
    labels: dict[Path, str] = {}
    used: Counter[str] = Counter()
    for project in projects:
        labels[project] = project_label(project, roots, used)

    metadata = {project: inspect_project(project) for project in projects}
    remote_groups: defaultdict[str, list[Path]] = defaultdict(list)
    for project, info in metadata.items():
        if info["remote"]:
            remote_groups[info["remote"]].append(project)

    active_roots = [root for root in roots if any(root_for(project, roots) == root for project in projects)]
    root_nodes: dict[Path, str] = {}
    for root in active_roots:
        root_nodes[root] = f"Root — {safe_slug(root.name)}"
        linked = [project for project in projects if root_for(project, roots) == root]
        body = [
            "---", "type: project-root", f'path: "{root}"', "---", "",
            f"# {root.name}", "", f"Source root: `{root}`", "", "## Projects", "",
        ]
        body.extend(f"- [[{labels[project]}]]" for project in linked)
        body.append("")
        write_if_changed(vault / "20 Areas" / "Project Roots" / f"{root_nodes[root]}.md", "\n".join(body))
    remove_stale_generated(
        vault / "20 Areas" / "Project Roots",
        {f"{label}.md" for label in root_nodes.values()},
        "project-root",
    )

    technology_projects: defaultdict[str, list[str]] = defaultdict(list)
    for project, info in metadata.items():
        for technology in info["technologies"]:
            technology_projects[technology].append(labels[project])

    for technology, project_labels in technology_projects.items():
        content = ["---", "type: technology", "---", "", f"# {technology}", "", "## Projects", ""]
        content.extend(f"- [[{label}]]" for label in sorted(project_labels))
        content.append("")
        write_if_changed(vault / "30 Resources" / "Technologies" / f"{safe_slug(technology)}.md", "\n".join(content))
    remove_stale_generated(
        vault / "30 Resources" / "Technologies",
        {f"{safe_slug(technology)}.md" for technology in technology_projects},
        "technology",
    )

    for project in projects:
        info = metadata[project]
        containing_root = root_for(project, roots)
        related = set()
        if info["remote"]:
            related.update(labels[item] for item in remote_groups[info["remote"]] if item != project)
        source_uri = project.as_uri()
        lines = [
            "---", "type: project", "status: indexed", f'path: "{project}"',
            f"last_indexed: {date.today().isoformat()}", "---", "", f"# {labels[project]}", "",
            f"- Root: [[{root_nodes[containing_root]}]]",
            f"- Source: [{project}]({source_uri})",
            f"- Path: `{project}`",
        ]
        if info["branch"]:
            lines.append(f"- Git branch: `{info['branch']}`")
        if info["commit"]:
            lines.append(f"- Latest commit: `{info['commit']}`")
        if info["remote"]:
            lines.append(f"- Remote: `{info['remote']}`")
        lines.append(f"- Indexed source files: approximately {info['file_count']}")
        lines.extend(["", "## Technologies", ""])
        lines.extend(f"- [[{technology}]]" for technology in info["technologies"])
        if info["manifests"]:
            lines.extend(["", "## Entry points and manifests", ""])
            lines.extend(f"- `{manifest}`" for manifest in info["manifests"])
        if related:
            lines.extend(["", "## Related projects", ""])
            lines.extend(f"- [[{label}]] — shares the same Git remote" for label in sorted(related))
        lines.extend([
            "", "## Retrieval rule", "",
            "Search the real source path with `rg` and read only files relevant to the current task.", "",
        ])
        write_if_changed(vault / "10 Projects" / "Graph" / f"{labels[project]}.md", "\n".join(lines))
    remove_stale_generated(
        vault / "10 Projects" / "Graph",
        {f"{label}.md" for label in labels.values()},
        "project",
    )

    index = [
        "---", "type: project-graph", f"last_indexed: {date.today().isoformat()}", "---", "",
        "# Project Graph", "",
        "This graph routes to the real source folders. Open Obsidian's Graph view to see projects connected to roots, technologies, and related copies.",
        "", "## Project roots", "",
    ]
    index.extend(f"- [[{root_nodes[root]}]]" for root in active_roots)
    index.extend(["", "## All projects", ""])
    index.extend(f"- [[{labels[project]}]] — `{project}`" for project in projects)
    index.extend(["", f"Indexed projects: **{len(projects)}**", ""])
    write_if_changed(vault / "10 Projects" / "Project Graph.md", "\n".join(index))
    print(f"Indexed {len(projects)} projects into {vault}")
    return 0


def main() -> int:
    home = Path.home()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", type=Path, default=home / "Documents" / "Second Brain")
    parser.add_argument("--root", action="append", type=Path, dest="roots")
    args = parser.parse_args()
    default_roots = [
        home / "Documents", home / "Desktop", home / "Downloads",
        home / "Developer", home / "Projects", home / "Code",
    ]
    roots = [path.expanduser().resolve() for path in (args.roots or default_roots) if path.expanduser().is_dir()]
    return build_graph(args.vault.expanduser().resolve(), roots)


if __name__ == "__main__":
    raise SystemExit(main())
