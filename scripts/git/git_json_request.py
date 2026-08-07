#!/usr/bin/env python3
"""Git helpers for JSON request processing."""

from __future__ import annotations

import logging
import os
import json
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from argparse import Namespace
from datetime import datetime
from pathlib import Path


def parse_bool_property(properties: dict[str, str], key: str, default: bool = False) -> bool:
	"""Parse a yes/no process-level config property."""
	value = properties.get(key)

	if value is None:
		return default

	return value.strip().lower() in {"1", "true", "yes", "y"}


def run_git_command(repo_root: Path, command: list[str]) -> tuple[str, list[str]]:
	"""Run a Git command in the repository root and return stdout or errors."""
	try:
		completed_process = subprocess.run(
			["git", *command],
			cwd=repo_root,
			capture_output=True,
			text=True,
			timeout=300,
			env={
				**os.environ,
				"GCM_INTERACTIVE": "never",
				"GIT_TERMINAL_PROMPT": "0",
			},
		)
	except subprocess.TimeoutExpired as error:
		return "", [f"git {' '.join(command)} timed out after 300 seconds: {error}"]
	except OSError as error:
		return "", [f"Unable to run git {' '.join(command)}: {error}"]

	if completed_process.returncode != 0:
		stderr = completed_process.stderr.strip()
		stdout = completed_process.stdout.strip()
		details = stderr or stdout or "No output"
		return "", [f"git {' '.join(command)} failed: {details}"]

	return completed_process.stdout.strip(), []


def build_git_branch_name(args: Namespace, process_config: dict[str, str]) -> str:
	"""Build a unique branch name for one JSON request run."""
	timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
	branch_prefix = process_config.get("GIT_BRANCH_PREFIX", "release").strip().strip("/") or "release"
	cluster_hint = args.cluster.rsplit("-", 1)[-1]
	branch_suffix = f"{timestamp}-{args.mode.lower()}-{args.platform_environment}-{args.environment}-{cluster_hint}"
	return f"{branch_prefix}/{branch_suffix}"


def normalize_repo_url(repo_url: str) -> str:
	"""Normalize common GitHub remote URL forms for comparison."""
	normalized = repo_url.strip().removesuffix(".git")
	if normalized.startswith("git@github.com:"):
		return "https://github.com/" + normalized.removeprefix("git@github.com:")
	return normalized


def validate_configured_remote(repo_root: Path, process_config: dict[str, str]) -> list[str]:
	"""Validate configured Git remote points to the expected repository URL."""
	remote_name = process_config["GIT_REMOTE_NAME"].strip()
	expected_repo_url = process_config["GIT_REPO_URL"].strip()
	remote_url, errors = run_git_command(repo_root, ["remote", "get-url", remote_name])

	if errors:
		return errors

	if normalize_repo_url(remote_url) != normalize_repo_url(expected_repo_url):
		return [
			f"Git remote '{remote_name}' points to '{remote_url}', expected '{expected_repo_url}'."
		]

	return []


def validate_clean_tracked_worktree(repo_root: Path) -> list[str]:
	"""Ensure tracked local changes will not be overwritten by branch checkout."""
	changed_files: set[str] = set()

	for command in (["diff", "--name-only"], ["diff", "--cached", "--name-only"]):
		output, errors = run_git_command(repo_root, command)
		if errors:
			return errors
		changed_files.update(line.strip() for line in output.splitlines() if line.strip())

	if not changed_files:
		return []

	changed_file_list = ", ".join(sorted(changed_files))
	return [
		"Tracked local changes exist before Git branch creation. Commit, stash, or reset them first. "
		f"Changed tracked file(s): {changed_file_list}"
	]


def prepare_git_branch(
	repo_root: Path,
	args: Namespace,
	process_config: dict[str, str],
) -> tuple[str | None, list[str]]:
	"""Fetch base branch and create a request branch when Git integration is enabled."""
	if not parse_bool_property(process_config, "GIT_ENABLED"):
		return None, []

	remote_name = process_config["GIT_REMOTE_NAME"].strip()
	base_branch = process_config["GIT_BASE_BRANCH"].strip()
	branch_name = build_git_branch_name(args, process_config)

	remote_errors = validate_configured_remote(repo_root, process_config)
	if remote_errors:
		return None, remote_errors

	worktree_errors = validate_clean_tracked_worktree(repo_root)
	if worktree_errors:
		return None, worktree_errors

	logging.info("Preparing Git branch '%s' from %s/%s.", branch_name, remote_name, base_branch)
	_, errors = run_git_command(repo_root, ["fetch", remote_name, base_branch])
	if errors:
		return None, errors

	_, errors = run_git_command(repo_root, ["checkout", "-B", branch_name, f"{remote_name}/{base_branch}"])
	if errors:
		return None, errors

	return branch_name, []


def relative_git_paths(repo_root: Path, paths: list[Path]) -> list[str]:
	"""Convert existing or deleted repo paths to Git-friendly relative paths."""
	relative_paths: list[str] = []
	for path in paths:
		try:
			relative_paths.append(path.relative_to(repo_root).as_posix())
		except ValueError:
			continue
	return relative_paths


def tracked_git_paths(repo_root: Path, paths: list[str]) -> tuple[list[str], list[str]]:
	"""Return the subset of paths that Git already tracks."""
	if not paths:
		return [], []

	output, errors = run_git_command(repo_root, ["ls-files", "--", *paths])
	if errors:
		return [], errors

	return [line.strip() for line in output.splitlines() if line.strip()], []


def commit_and_push_git_changes(
	repo_root: Path,
	args: Namespace,
	process_config: dict[str, str],
	branch_name: str | None,
	updated_files: list[Path],
	archived_files: list[Path],
	input_files: dict[str, Path],
) -> list[str]:
	"""Stage generated/archive changes, commit them, and push the request branch."""
	if not branch_name:
		return []

	paths_to_stage = sorted(set(relative_git_paths(repo_root, [*updated_files, *archived_files])))
	if not paths_to_stage:
		return ["Git integration found no files to stage."]

	_, errors = run_git_command(repo_root, ["add", "--", *paths_to_stage])
	if errors:
		return errors

	input_paths = sorted(set(relative_git_paths(repo_root, list(input_files.values()))))
	tracked_input_paths, errors = tracked_git_paths(repo_root, input_paths)
	if errors:
		return errors

	if tracked_input_paths:
		_, errors = run_git_command(repo_root, ["add", "-u", "--", *tracked_input_paths])
		if errors:
			return errors

	status_paths = sorted(set(paths_to_stage + tracked_input_paths))
	status_output, errors = run_git_command(repo_root, ["status", "--porcelain", "--", *status_paths])
	if errors:
		return errors

	if not status_output:
		return ["No Git changes detected after generation/archive. Commit was not created."]

	commit_prefix = process_config["GIT_COMMIT_MESSAGE_PREFIX"].strip()
	commit_message = f"{commit_prefix}: {args.mode} {args.platform_environment} {args.environment} {args.cluster}"
	_, errors = run_git_command(repo_root, ["commit", "-m", commit_message])
	if errors:
		return errors

	remote_name = process_config["GIT_REMOTE_NAME"].strip()
	logging.info("Pushing Git branch '%s' to remote '%s'.", branch_name, remote_name)
	_, errors = run_git_command(repo_root, ["push", "-u", remote_name, branch_name])
	return errors


def parse_github_repo(repo_url: str) -> tuple[str, str]:
	"""Return GitHub owner and repository name from the configured repo URL."""
	parsed_url = urllib.parse.urlparse(normalize_repo_url(repo_url))
	path_parts = parsed_url.path.strip("/").split("/")

	if parsed_url.netloc != "github.com" or len(path_parts) != 2:
		raise ValueError("GIT_REPO_URL must point to a GitHub repository like https://github.com/org/repo.git")

	return path_parts[0], path_parts[1]


def github_token_from_environment() -> str:
	"""Read GitHub token used for PR creation."""
	token = os.environ.get("GITHUB_TOKEN", "").strip()

	if not token:
		raise ValueError("GITHUB_TOKEN environment variable is required when GIT_PR_ENABLED=true.")

	return token


def build_pull_request_body(args: Namespace, updated_files: list[Path], archived_files: list[Path], repo_root: Path) -> str:
	"""Build a concise pull request body listing generated and archived files."""
	updated_file_names = relative_git_paths(repo_root, updated_files)
	archived_file_names = relative_git_paths(repo_root, archived_files)
	lines = [
		"Automated JSON request update.",
		"",
		f"Mode: {args.mode}",
		f"Platform environment: {args.platform_environment}",
		f"Environment: {args.environment}",
		f"Cluster: {args.cluster}",
	]

	if updated_file_names:
		lines.extend(["", "Updated generated files:"])
		lines.extend(f"- {file_name}" for file_name in sorted(updated_file_names))

	if archived_file_names:
		lines.extend(["", "Archived input files:"])
		lines.extend(f"- {file_name}" for file_name in sorted(archived_file_names))

	return "\n".join(lines)


def create_pull_request(
	repo_root: Path,
	args: Namespace,
	process_config: dict[str, str],
	branch_name: str | None,
	updated_files: list[Path],
	archived_files: list[Path],
) -> tuple[str | None, list[str]]:
	"""Create a GitHub pull request for the pushed JSON request branch."""
	if not branch_name or not parse_bool_property(process_config, "GIT_PR_ENABLED"):
		return None, []

	try:
		github_token = github_token_from_environment()
		owner, repo_name = parse_github_repo(process_config["GIT_REPO_URL"].strip())
	except ValueError as error:
		return None, [str(error)]

	title = f"{process_config['GIT_COMMIT_MESSAGE_PREFIX'].strip()}: {args.mode} {args.platform_environment} {args.environment}"
	body = build_pull_request_body(args, updated_files, archived_files, repo_root)
	payload = json.dumps(
		{
			"title": title,
			"head": branch_name,
			"base": process_config["GIT_BASE_BRANCH"].strip(),
			"body": body,
		}
	).encode("utf-8")
	request = urllib.request.Request(
		f"https://api.github.com/repos/{owner}/{repo_name}/pulls",
		data=payload,
		headers={
			"Accept": "application/vnd.github+json",
			"Authorization": f"Bearer {github_token}",
			"Content-Type": "application/json",
			"User-Agent": "estee-cc-json-request-script",
			"X-GitHub-Api-Version": "2022-11-28",
		},
		method="POST",
	)

	try:
		with urllib.request.urlopen(request) as response:
			response_data = json.loads(response.read().decode("utf-8"))
	except urllib.error.HTTPError as error:
		error_body = error.read().decode("utf-8")
		return None, [f"GitHub PR creation failed with status {error.code}: {error_body}"]
	except urllib.error.URLError as error:
		return None, [f"GitHub PR creation failed: {error}"]

	return response_data.get("html_url"), []