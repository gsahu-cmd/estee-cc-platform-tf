#!/usr/bin/env python3
"""Generate topic catalog JSON files and optionally raise a GitHub PR."""

from __future__ import annotations

import argparse
import csv
import json
import logging
import os
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
	sys.path.insert(0, str(SCRIPTS_DIR))

from topic.topic_validator import parse_topic_config
from validate_csv_request import (
	get_platform_environment,
	get_request_type,
	load_properties,
	normalize_row,
	resolve_property_file,
	setup_logging,
)


def parse_bool(value: str) -> bool:
	"""Parse a property value into a boolean."""
	return value.strip().lower() in {"1", "true", "yes", "y"}


def load_csv_properties(csv_file: Path) -> tuple[str, str, Path, dict[str, str]]:
	"""Load the property file selected by the first CSV row."""
	rows = read_csv_rows(csv_file)
	request_type = get_request_type(rows[0][1], rows[0][0])
	platform_environment = get_platform_environment(rows[0][1], rows[0][0])
	property_file = resolve_property_file(request_type, platform_environment)
	properties = load_properties(property_file)
	return request_type, platform_environment, property_file, properties


def read_csv_rows(csv_file: Path) -> list[tuple[int, dict[str, str]]]:
	"""Read CSV rows after the main validator has already checked the file.

	Input example:
	main/scripts/sample_topic_request.csv

	Output example:
	[(2, {"type": "topic", "action": "create", ...})]
	"""
	with csv_file.open("r", encoding="utf-8-sig", newline="") as file_handle:
		reader = csv.DictReader(file_handle)
		return [
			(row_number, normalize_row(raw_row))
			for row_number, raw_row in enumerate(reader, start=2)
		]


def parse_tags(row: dict[str, str]) -> list[str]:
	"""Parse the tags column into a list for the tag catalog file.

	Input example:
	PII|Domain=orders

	Output example:
	["PII", "Domain=orders"]
	"""
	tags_value = row.get("tags", "").strip()

	if not tags_value or tags_value.upper() == "NONE":
		return []

	return [tag.strip() for tag in tags_value.split("|") if tag.strip()]


def load_json_file(file_path: Path, default_data: dict) -> dict:
	"""Load an existing JSON catalog file or return a default structure.

	Input example:
	topics/nonprod/elc-sandbox/elc-sandbox-core-enterprise/topics-elc-sandbox-elc-sandbox-core-enterprise.json

	Output example:
	Existing JSON content, or the supplied default data when the file is missing.
	"""
	if not file_path.exists():
		return default_data

	with file_path.open("r", encoding="utf-8") as file_handle:
		return json.load(file_handle)


def write_json_file(file_path: Path, data: dict) -> None:
	"""Write JSON with stable formatting so PR diffs are readable."""
	file_path.parent.mkdir(parents=True, exist_ok=True)

	with file_path.open("w", encoding="utf-8") as file_handle:
		json.dump(data, file_handle, indent=2, sort_keys=True)
		file_handle.write("\n")


def load_github_environment() -> tuple[str, str]:
	"""Read GitHub credentials from environment variables."""
	github_token = os.environ.get("GITHUB_TOKEN", "").strip()
	github_user = os.environ.get("GITHUB_USER", "").strip()
	missing_variables = []

	if not github_token:
		missing_variables.append("GITHUB_TOKEN")

	if not github_user:
		missing_variables.append("GITHUB_USER")

	if missing_variables:
		raise ValueError("Missing required environment variable(s): " + ", ".join(missing_variables))

	return github_user, github_token


def redact_text(value: str, secret_values: list[str]) -> str:
	"""Remove secret values from command output before logging errors."""
	redacted_value = value

	for secret_value in secret_values:
		if secret_value:
			redacted_value = redacted_value.replace(secret_value, "***")

	return redacted_value


def run_command(
	command: list[str],
	cwd: Path | None = None,
	secret_values: list[str] | None = None,
	timeout_seconds: int = 300,
) -> str:
	"""Run a command and return stdout, raising a sanitized error on failure."""
	secret_values = secret_values or []
	command_name = " ".join(command[:3])
	logging.info("Running command: %s", command_name)

	try:
		completed_process = subprocess.run(
			command,
			cwd=str(cwd) if cwd else None,
			capture_output=True,
			text=True,
			timeout=timeout_seconds,
			env={
				**os.environ,
				"GCM_INTERACTIVE": "never",
				"GIT_ASKPASS": "true",
				"GIT_TERMINAL_PROMPT": "0",
				"SSH_ASKPASS": "true",
			},
		)
	except subprocess.TimeoutExpired as error:
		stdout = redact_text((error.stdout or "").strip(), secret_values)
		stderr = redact_text((error.stderr or "").strip(), secret_values)
		raise RuntimeError(
			f"Command timed out after {timeout_seconds} seconds.\nSTDOUT: {stdout}\nSTDERR: {stderr}"
		) from error

	if completed_process.returncode != 0:
		stdout = redact_text(completed_process.stdout.strip(), secret_values)
		stderr = redact_text(completed_process.stderr.strip(), secret_values)
		raise RuntimeError(
			f"Command failed with exit code {completed_process.returncode}.\nSTDOUT: {stdout}\nSTDERR: {stderr}"
		)

	return completed_process.stdout.strip()


def normalize_https_repo_url(repo_url: str) -> str:
	"""Convert supported GitHub repo URL formats to HTTPS."""
	repo_url = repo_url.strip()

	if repo_url.startswith("git@github.com:"):
		return "https://github.com/" + repo_url.removeprefix("git@github.com:")

	return repo_url


def build_authenticated_repo_url(repo_url: str, github_user: str, github_token: str) -> str:
	"""Build an HTTPS GitHub URL containing credentials for git clone/push."""
	https_repo_url = normalize_https_repo_url(repo_url)
	parsed_url = urllib.parse.urlparse(https_repo_url)

	if parsed_url.scheme != "https" or parsed_url.netloc != "github.com":
		raise ValueError("GIT_REPO_URL must be a GitHub HTTPS URL or git@github.com SSH URL.")

	quoted_user = urllib.parse.quote(github_user, safe="")
	quoted_token = urllib.parse.quote(github_token, safe="")
	return urllib.parse.urlunparse(
		parsed_url._replace(netloc=f"{quoted_user}:{quoted_token}@{parsed_url.netloc}")
	)


def parse_github_repo(repo_url: str) -> tuple[str, str]:
	"""Return GitHub owner and repository name from GIT_REPO_URL."""
	https_repo_url = normalize_https_repo_url(repo_url)
	parsed_url = urllib.parse.urlparse(https_repo_url)
	path_parts = parsed_url.path.strip("/").split("/")

	if parsed_url.netloc != "github.com" or len(path_parts) != 2:
		raise ValueError("GIT_REPO_URL must point to a GitHub repository like https://github.com/org/repo.git")

	repo_name = path_parts[1].removesuffix(".git")
	return path_parts[0], repo_name


def build_branch_name(branch_prefix: str) -> str:
	"""Build a unique branch name for one catalog request."""
	timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
	clean_prefix = branch_prefix.strip().strip("/") or "topic-request"
	return f"{clean_prefix}-{timestamp}"


def create_pull_request(
	repo_url: str,
	github_token: str,
	head_branch: str,
	base_branch: str,
	title: str,
	body: str,
) -> str:
	"""Create a GitHub pull request and return the PR URL."""
	owner, repo_name = parse_github_repo(repo_url)
	api_url = f"https://api.github.com/repos/{owner}/{repo_name}/pulls"
	payload = json.dumps(
		{
			"title": title,
			"head": head_branch,
			"base": base_branch,
			"body": body,
		}
	).encode("utf-8")
	request = urllib.request.Request(
		api_url,
		data=payload,
		headers={
			"Accept": "application/vnd.github+json",
			"Authorization": f"Bearer {github_token}",
			"Content-Type": "application/json",
			"User-Agent": "estee-cc-topic-catalog-script",
			"X-GitHub-Api-Version": "2022-11-28",
		},
		method="POST",
	)

	try:
		with urllib.request.urlopen(request) as response:
			response_data = json.loads(response.read().decode("utf-8"))
	except urllib.error.HTTPError as error:
		error_body = error.read().decode("utf-8")
		raise RuntimeError(f"GitHub PR creation failed with status {error.code}: {error_body}") from error

	return response_data.get("html_url", "")


def build_catalog_paths(
	catalog_root: Path, platform_environment: str, environment: str, cluster: str, properties: dict[str, str]
) -> tuple[Path, Path]:
	"""Build topic and tag catalog paths for one environment/cluster.

	Input example:
	platform_environment=nonprod, environment=elc-sandbox, cluster=elc-sandbox-core-enterprise

	Output example:
	topics/nonprod/elc-sandbox/elc-sandbox-core-enterprise/topics-elc-sandbox-elc-sandbox-core-enterprise.json
	topics/nonprod/elc-sandbox/elc-sandbox-core-enterprise/topic-tags-elc-sandbox-elc-sandbox-core-enterprise.json
	"""
	topic_template = properties.get("TOPIC_CATALOG_FILE_TEMPLATE", "topics-{environment}-{cluster}.json")
	tags_template = properties.get("TOPIC_TAGS_CATALOG_FILE_TEMPLATE", "topic-tags-{environment}-{cluster}.json")
	catalog_dir = catalog_root / platform_environment / environment / cluster

	topic_file = catalog_dir / topic_template.format(environment=environment, cluster=cluster)
	tags_file = catalog_dir / tags_template.format(environment=environment, cluster=cluster)
	return topic_file, tags_file


def topic_entry_from_row(row: dict[str, str], properties: dict[str, str], row_number: int) -> tuple[dict, list[str]]:
	"""Convert one CSV row into one topic catalog entry.

	Tags are intentionally excluded from this entry and written separately.
	"""
	config, config_errors = parse_topic_config(row, properties, row_number)

	if config_errors:
		return {}, config_errors

	return {
		"name": row.get("name", ""),
		"partitions": int(row.get("partitions", "0")),
		"config": config,
	}, []


def apply_topic_action(catalog_data: dict, topic_entry: dict, action: str, row_number: int) -> list[str]:
	"""Apply create/update/delete to the topic catalog data.

	create fails if the topic already exists.
	update/delete fail if the topic does not exist.
	"""
	topics = catalog_data.setdefault("topics", [])
	topic_name = topic_entry["name"]
	existing_index = next((index for index, topic in enumerate(topics) if topic.get("name") == topic_name), None)

	if action == "create":
		if existing_index is not None:
			return [f"Row {row_number}: topic '{topic_name}' already exists in catalog."]
		topics.append(topic_entry)
		return []

	if action == "update":
		if existing_index is None:
			return [f"Row {row_number}: topic '{topic_name}' does not exist in catalog for update."]
		topics[existing_index] = topic_entry
		return []

	if action == "delete":
		if existing_index is None:
			return [f"Row {row_number}: topic '{topic_name}' does not exist in catalog for delete."]
		del topics[existing_index]
		return []

	return [f"Row {row_number}: unsupported action '{action}'."]


def apply_tag_action(tags_data: dict, topic_name: str, tags: list[str], action: str) -> None:
	"""Apply create/update/delete to the topic tags catalog data."""
	topic_tags = tags_data.setdefault("topic_tags", [])
	existing_index = next((index for index, item in enumerate(topic_tags) if item.get("name") == topic_name), None)

	if action in {"create", "update"}:
		tag_entry = {"name": topic_name, "tags": tags}
		if existing_index is None:
			topic_tags.append(tag_entry)
		else:
			topic_tags[existing_index] = tag_entry

	if action == "delete" and existing_index is not None:
		del topic_tags[existing_index]


def sort_catalogs(catalog_data: dict, tags_data: dict) -> None:
	"""Sort catalog entries by topic name for stable PR diffs."""
	catalog_data["topics"] = sorted(catalog_data.get("topics", []), key=lambda item: item.get("name", ""))
	tags_data["topic_tags"] = sorted(tags_data.get("topic_tags", []), key=lambda item: item.get("name", ""))


def update_catalogs(csv_file: Path, catalog_root: Path) -> tuple[list[Path], list[str]]:
	"""Update local topic/tag catalog files from an already validated CSV.

	Input example:
	csv_file=main/scripts/sample_topic_request.csv
	catalog_root=topics

	Output example:
	([topics/nonprod/.../topics-...json, topics/nonprod/.../topic-tags-...json], [])
	"""
	rows = read_csv_rows(csv_file)
	request_type = get_request_type(rows[0][1], rows[0][0])
	platform_environment = get_platform_environment(rows[0][1], rows[0][0])

	if request_type != "topic":
		return [], [f"Git topic catalog update supports only type 'topic'. Current type: '{request_type}'."]

	property_file = resolve_property_file(request_type, platform_environment)
	properties = load_properties(property_file)
	changed_files: list[Path] = []
	errors: list[str] = []
	pending_writes: list[tuple[Path, dict]] = []

	grouped_rows: dict[tuple[str, str], list[tuple[int, dict[str, str]]]] = {}
	for row_number, row in rows:
		grouped_rows.setdefault((row["environment"], row["cluster"]), []).append((row_number, row))

	for (environment, cluster), group_rows in grouped_rows.items():
		topic_file, tags_file = build_catalog_paths(catalog_root, platform_environment, environment, cluster, properties)
		catalog_data = load_json_file(
			topic_file,
			{"environment": environment, "cluster": cluster, "topics": []},
		)
		tags_data = load_json_file(
			tags_file,
			{"environment": environment, "cluster": cluster, "topic_tags": []},
		)

		for row_number, row in group_rows:
			action = row.get("action", "").lower()
			topic_entry, topic_entry_errors = topic_entry_from_row(row, properties, row_number)

			if topic_entry_errors:
				errors.extend(topic_entry_errors)
				continue

			topic_errors = apply_topic_action(catalog_data, topic_entry, action, row_number)
			errors.extend(topic_errors)

			if not topic_errors:
				apply_tag_action(tags_data, topic_entry["name"], parse_tags(row), action)

		sort_catalogs(catalog_data, tags_data)

		pending_writes.extend([(topic_file, catalog_data), (tags_file, tags_data)])

	if errors:
		return [], errors

	for file_path, data in pending_writes:
		write_json_file(file_path, data)
		changed_files.append(file_path)

	return changed_files, errors


def update_catalogs_in_github(
	csv_file: Path,
	properties: dict[str, str],
	catalog_root: Path,
	repo_url: str,
	base_branch: str,
	branch_prefix: str,
	pr_title: str | None,
	pr_body: str | None,
) -> tuple[str, str, list[str], list[str]]:
	"""Clone the catalog repo, update JSON files, push a branch, and create a PR."""
	if not repo_url:
		return "", "", [], ["GIT_REPO_URL is required for GitHub catalog update."]

	if catalog_root.is_absolute():
		return "", "", [], ["Catalog root must be a relative path when using GitHub catalog update."]

	github_user, github_token = load_github_environment()
	clean_repo_url = normalize_https_repo_url(repo_url)
	authenticated_repo_url = build_authenticated_repo_url(clean_repo_url, github_user, github_token)
	branch_name = build_branch_name(branch_prefix)
	commit_title = pr_title or f"Update topic catalog {branch_name}"
	pull_request_body = pr_body or "Automated topic catalog update from CSV request."
	secret_values = [github_token, authenticated_repo_url]

	with tempfile.TemporaryDirectory(prefix="topic-catalog-git-") as temporary_directory:
		work_dir = Path(temporary_directory)
		repo_dir = work_dir / "catalog-repo"
		logging.info("Cloning GitHub catalog repo branch '%s'.", base_branch)
		run_command(
			["git", "clone", "--branch", base_branch, "--single-branch", authenticated_repo_url, str(repo_dir)],
			secret_values=secret_values,
		)
		run_command(["git", "remote", "set-url", "origin", clean_repo_url], cwd=repo_dir)
		run_command(["git", "checkout", "-b", branch_name], cwd=repo_dir)
		run_command(["git", "config", "user.name", github_user], cwd=repo_dir)
		run_command(["git", "config", "user.email", f"{github_user}@users.noreply.github.com"], cwd=repo_dir)

		changed_files, errors = update_catalogs(csv_file, repo_dir / catalog_root)

		if errors:
			return "", branch_name, [], errors

		status_output = run_command(["git", "status", "--porcelain"], cwd=repo_dir)

		if not status_output:
			return "", branch_name, [], ["No catalog changes detected. GitHub PR was not created."]

		run_command(["git", "add", str(catalog_root)], cwd=repo_dir)
		run_command(["git", "commit", "-m", commit_title], cwd=repo_dir)
		logging.info("Pushing branch '%s' to GitHub.", branch_name)
		run_command(
			["git", "push", authenticated_repo_url, f"{branch_name}:{branch_name}"],
			cwd=repo_dir,
			secret_values=secret_values,
		)
		changed_file_names = [str(file_path.relative_to(repo_dir)) for file_path in changed_files]
		body_with_files = pull_request_body + "\n\nUpdated files:\n" + "\n".join(
			f"- {file_name}" for file_name in changed_file_names
		)
		pull_request_url = create_pull_request(
			clean_repo_url,
			github_token,
			branch_name,
			base_branch,
			commit_title,
			body_with_files,
		)

		return pull_request_url, branch_name, changed_file_names, []


def parse_args() -> argparse.Namespace:
	"""Read command-line arguments.

	Command example:
	python main/scripts/git/git_topic_catalog.py main/scripts/sample_topic_request.csv --catalog-root topics
	"""
	parser = argparse.ArgumentParser(description="Generate topic catalog JSON files from a validated topic CSV.")
	parser.add_argument("csv_file", help="Path to the validated topic CSV request file.")
	parser.add_argument(
		"--catalog-root",
		default=None,
		help="Catalog root folder. Defaults to GIT_CATALOG_ROOT from the selected property file.",
	)
	parser.add_argument(
		"--push-to-github",
		action="store_true",
		help="Clone the configured GitHub repo, commit catalog changes, push a branch, and create a PR.",
	)
	parser.add_argument(
		"--repo-url",
		default=None,
		help="GitHub repo URL. Defaults to GIT_REPO_URL from the selected property file.",
	)
	parser.add_argument(
		"--base-branch",
		default=None,
		help="Base branch for the catalog PR. Defaults to GIT_BASE_BRANCH from the selected property file.",
	)
	parser.add_argument(
		"--branch-prefix",
		default=None,
		help="Prefix for the generated branch name. Defaults to GIT_BRANCH_PREFIX from the selected property file.",
	)
	parser.add_argument("--pr-title", default=None, help="Pull request title. Defaults to an generated title.")
	parser.add_argument("--pr-body", default=None, help="Pull request body. Defaults to a generated body.")
	return parser.parse_args()


def main() -> int:
	"""Script entry point."""
	setup_logging()
	args = parse_args()
	csv_file = Path(args.csv_file).resolve()

	try:
		request_type, platform_environment, property_file, properties = load_csv_properties(csv_file)
	except (FileNotFoundError, IndexError, ValueError) as error:
		logging.error("Unable to load CSV properties: %s", error)
		return 1

	if request_type != "topic":
		logging.error("Git topic catalog update supports only type 'topic'. Current type: '%s'.", request_type)
		return 1

	logging.info("CSV request type: %s", request_type)
	logging.info("CSV platform environment: %s", platform_environment)
	logging.info("Loaded catalog properties from: %s", property_file)
	catalog_root = Path(args.catalog_root or properties.get("GIT_CATALOG_ROOT", "topics"))
	property_git_enabled = parse_bool(properties.get("ENABLE_GIT_CATALOG_UPDATE", "false"))
	git_enabled = args.push_to_github or property_git_enabled
	logging.info("Catalog root: %s", catalog_root)
	logging.info("ENABLE_GIT_CATALOG_UPDATE property: %s", properties.get("ENABLE_GIT_CATALOG_UPDATE", "false"))
	logging.info("--push-to-github argument: %s", args.push_to_github)
	logging.info("GitHub catalog update mode: %s", "enabled" if git_enabled else "disabled")

	if git_enabled:
		repo_url = args.repo_url or properties.get("GIT_REPO_URL", "")
		base_branch = args.base_branch or properties.get("GIT_BASE_BRANCH", "main")
		branch_prefix = args.branch_prefix or properties.get("GIT_BRANCH_PREFIX", "topic-request")
		logging.info("GitHub repo URL configured: %s", "yes" if repo_url else "no")
		logging.info("GitHub base branch: %s", base_branch)
		logging.info("GitHub branch prefix: %s", branch_prefix)

		try:
			pull_request_url, branch_name, changed_files, errors = update_catalogs_in_github(
				csv_file,
				properties,
				catalog_root,
				repo_url,
				base_branch,
				branch_prefix,
				args.pr_title,
				args.pr_body,
			)
		except (RuntimeError, ValueError) as error:
			logging.error("GitHub catalog update failed: %s", error)
			return 1

		if errors:
			logging.error("GitHub catalog update failed with %s error(s).", len(errors))
			for error in errors:
				logging.error(error)
			return 1

		logging.info("GitHub catalog update completed. Branch: %s", branch_name)
		logging.info("Pull request: %s", pull_request_url)
		for file_path in changed_files:
			logging.info("Updated catalog file: %s", file_path)
		return 0

	changed_files, errors = update_catalogs(csv_file, catalog_root)

	if errors:
		logging.error("Topic catalog update failed with %s error(s).", len(errors))
		for error in errors:
			logging.error(error)
		return 1

	logging.info("Topic catalog update completed. Updated file count: %s", len(changed_files))
	for file_path in changed_files:
		logging.info("Updated catalog file: %s", file_path)

	return 0


if __name__ == "__main__":
	sys.exit(main())
