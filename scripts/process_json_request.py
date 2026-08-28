#!/usr/bin/env python3
"""Validate JSON request files before catalog JSON generation."""

from __future__ import annotations

import argparse
import logging
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Callable


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
CONFIG_DIR = SCRIPT_DIR / "config"
PROCESS_CONFIG_FILE = CONFIG_DIR / "process_json_request.properties"
GIT_SCRIPT_DIR = SCRIPT_DIR / "git"

if str(SCRIPT_DIR) not in sys.path:
	sys.path.insert(0, str(SCRIPT_DIR))

if str(GIT_SCRIPT_DIR) not in sys.path:
	sys.path.insert(0, str(GIT_SCRIPT_DIR))

from json_request.acl_validator import validate_acl
from json_request.common import (
	ALLOWED_INPUT_FILES,
	discover_input_files,
	input_file_name_settings,
	load_json_file,
	load_properties,
	parse_list_property,
	target_operation_stack_dir,
)
from json_request.identity_pool_validator import validate_identity_pool
from json_request.identity_pool_generator import identity_pool_stack_dir, update_identity_pool_generated_files
from json_request.group_mapping_validator import validate_group_mapping
from json_request.group_mapping_generator import group_mapping_stack_dir, update_group_mapping_generated_files
from json_request.group_mapping_rbac_validator import validate_group_mapping_rbac
from json_request.group_mapping_rbac_generator import update_group_mapping_rbac_generated_files
from json_request.acl_generator import update_acl_generated_files
from json_request.rbac_generator import update_rbac_generated_files
from json_request.rbac_validator import validate_rbac
from json_request.topic_generator import update_topic_generated_files
from json_request.topic_validator import validate_topics
from git_json_request import commit_and_push_git_changes, create_pull_request, prepare_git_branch


Validator = Callable[[Any, str, Path, dict[str, str]], list[str]]

VALIDATORS: dict[str, Validator] = {
	"topic": validate_topics,
	"rbac": validate_rbac,
	"acl": validate_acl,
	"identity_pool": validate_identity_pool,
	"group_mapping": validate_group_mapping,
	"group_mapping_rbac": validate_group_mapping_rbac,
}


def setup_logging() -> None:
	"""Configure human-readable logs."""
	logging.basicConfig(
		level=logging.INFO,
		format="%(asctime)s | %(levelname)s | %(message)s",
		datefmt="%Y-%m-%d %H:%M:%S",
	)


def parse_args() -> argparse.Namespace:
	"""Parse command-line arguments for one request validation run."""
	parser = argparse.ArgumentParser(description="Validate Confluent Cloud JSON request input files.")
	parser.add_argument("--platform-environment", required=True, choices=["nonprod", "prod"])
	parser.add_argument("--environment", required=True, help="Confluent environment folder name, for example elc-sandbox.")
	parser.add_argument("--cluster", required=True, help="Confluent Kafka cluster folder name.")
	parser.add_argument("--mode", choices=["UPSERT", "DELETE"], help="Optional consistency check; mode is derived from input file names.")
	parser.add_argument("--input-dir", type=Path, default=SCRIPT_DIR / "input")
	return parser.parse_args()


def config_file_for(request_type: str, platform_environment: str) -> Path:
	"""Resolve the per-type config file."""
	return CONFIG_DIR / platform_environment / f"{request_type}_json_config.properties"


def parse_bool_property(properties: dict[str, str], key: str, default: bool = False) -> bool:
	"""Parse a yes/no process-level config property."""
	value = properties.get(key)

	if value is None:
		return default

	return value.strip().lower() in {"1", "true", "yes", "y"}


def load_process_config() -> tuple[dict[str, str], list[str]]:
	"""Load root-level process configuration used by the main script."""
	try:
		return load_properties(PROCESS_CONFIG_FILE), []
	except (FileNotFoundError, ValueError) as error:
		return {}, [str(error)]


def validate_process_config(process_config: dict[str, str]) -> list[str]:
	"""Validate supported root-level process settings."""
	errors: list[str] = []
	git_enabled = parse_bool_property(process_config, "GIT_ENABLED")
	git_pr_enabled = parse_bool_property(process_config, "GIT_PR_ENABLED")
	archive_root = process_config.get("ARCHIVE_ROOT", "").strip()

	if git_enabled:
		for required_key in ("GIT_REPO_URL", "GIT_REMOTE_NAME", "GIT_BASE_BRANCH", "GIT_BRANCH_PREFIX", "GIT_COMMIT_MESSAGE_PREFIX"):
			if not process_config.get(required_key, "").strip():
				errors.append(f"{required_key} is mandatory when GIT_ENABLED=true.")

	if git_pr_enabled and not git_enabled:
		errors.append("GIT_ENABLED=true is mandatory when GIT_PR_ENABLED=true.")

	if parse_bool_property(process_config, "ARCHIVE_ENABLED", default=True) and not archive_root:
		errors.append("ARCHIVE_ROOT is mandatory when ARCHIVE_ENABLED=true.")

	if not process_config.get("OPERATION_CATALOG_ROOT", "").strip():
		errors.append("OPERATION_CATALOG_ROOT is mandatory in process config.")

	return errors


def resolve_process_path(raw_path: str) -> Path:
	"""Resolve a process config path relative to the repo root unless it is absolute."""
	path = Path(raw_path)
	if path.is_absolute():
		return path
	return REPO_ROOT / path


def timestamped_archive_dir(archive_root: Path, args: argparse.Namespace) -> Path:
	"""Build a unique timestamped archive directory for one processed request."""
	timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
	base_name = f"{timestamp}_{args.mode}_{args.platform_environment}_{args.environment}_{args.cluster}"
	archive_dir = archive_root / base_name
	suffix = 1

	while archive_dir.exists():
		archive_dir = archive_root / f"{base_name}_{suffix:02d}"
		suffix += 1

	return archive_dir


def archive_input_files(
	args: argparse.Namespace,
	process_config: dict[str, str],
	input_files: dict[str, Path],
) -> tuple[Path | None, list[Path], list[str]]:
	"""Move processed input files to a timestamped archive directory."""
	if not parse_bool_property(process_config, "ARCHIVE_ENABLED", default=True):
		logging.info("Input archive is disabled by process config.")
		return None, [], []

	archive_root = resolve_process_path(process_config.get("ARCHIVE_ROOT", "scripts/archive"))
	archive_dir = timestamped_archive_dir(archive_root, args)
	archived_files: list[Path] = []

	try:
		archive_dir.mkdir(parents=True, exist_ok=False)
		for file_name, file_path in sorted(input_files.items()):
			archived_file = archive_dir / file_path.name
			shutil.move(str(file_path), str(archived_file))
			archived_files.append(archived_file)
	except OSError as error:
		return None, [], [f"Failed to archive input files to {archive_dir}: {error}"]

	return archive_dir, archived_files, []


def validate_run_scope(args: argparse.Namespace, process_config: dict[str, str]) -> tuple[Path, list[str]]:
	"""Validate run-level target arguments and return the target Terraform folder."""
	errors: list[str] = []
	target_dir = target_operation_stack_dir(
		REPO_ROOT,
		args.platform_environment,
		args.environment,
		args.cluster,
		process_config.get("OPERATION_CATALOG_ROOT", ""),
	)

	if not target_dir.exists():
		errors.append(f"Target Terraform folder does not exist: {target_dir}")
	elif not target_dir.is_dir():
		errors.append(f"Target Terraform path is not a folder: {target_dir}")

	return target_dir, errors


def request_target_dir(
	args: argparse.Namespace,
	request_type: str,
	properties: dict[str, str],
) -> Path:
	"""Resolve the Terraform stack directory for one request type from its config."""
	if request_type == "identity_pool":
		return identity_pool_stack_dir(REPO_ROOT, args.platform_environment, properties)

	if request_type == "group_mapping":
		return group_mapping_stack_dir(REPO_ROOT, args.platform_environment, properties)

	catalog_root = properties["CATALOG_ROOT"]
	return target_operation_stack_dir(REPO_ROOT, args.platform_environment, args.environment, args.cluster, catalog_root)


def validate_request_target_dir(request_type: str, target_dir: Path) -> list[str]:
	"""Validate that a configured request target folder exists."""
	if not target_dir.exists():
		return [f"{request_type}: configured Terraform folder does not exist: {target_dir}"]

	if not target_dir.is_dir():
		return [f"{request_type}: configured Terraform path is not a folder: {target_dir}"]

	return []


def apply_filename_scope(args: argparse.Namespace, inferred_mode: str | None, inferred_environment: str | None) -> list[str]:
	"""Apply mode/environment metadata inferred from the input file names."""
	errors: list[str] = []

	if inferred_mode is None:
		return errors

	if args.mode and args.mode != inferred_mode:
		errors.append(f"Command-line mode '{args.mode}' does not match input filename mode '{inferred_mode}'.")

	if inferred_environment and inferred_environment != args.platform_environment:
		errors.append(
			f"Input filename environment '{inferred_environment}' does not match --platform-environment '{args.platform_environment}'."
		)

	args.mode = inferred_mode
	return errors


def validate_properties(properties: dict[str, str], request_type: str, platform_environment: str, mode: str) -> list[str]:
	"""Validate that the selected config matches the current run."""
	errors: list[str] = []
	valid_platform_environment = properties.get("VALID_PLATFORM_ENVIRONMENT", "").strip().lower()
	valid_modes = parse_list_property(properties, "VALID_MODES")

	if valid_platform_environment != platform_environment:
		errors.append(
			f"{request_type}: config VALID_PLATFORM_ENVIRONMENT is '{valid_platform_environment}', "
			f"expected '{platform_environment}'."
		)

	if not properties.get("CATALOG_ROOT", "").strip():
		errors.append(f"{request_type}: CATALOG_ROOT is mandatory in config.")

	if mode not in valid_modes:
		errors.append(f"{request_type}: mode '{mode}' is not allowed by config.")

	return errors


def validate_input_files(args: argparse.Namespace, target_dir: Path, input_files: dict[str, Path]) -> list[str]:
	"""Validate each discovered input file."""
	errors: list[str] = []

	for file_name, file_path in sorted(input_files.items()):
		request_type = ALLOWED_INPUT_FILES[file_name]
		property_file = config_file_for(request_type, args.platform_environment)
		logging.info("Validating %s using %s", file_name, property_file.relative_to(CONFIG_DIR))

		try:
			properties = load_properties(property_file)
		except (FileNotFoundError, ValueError) as error:
			errors.append(str(error))
			continue

		property_errors = validate_properties(properties, request_type, args.platform_environment, args.mode)
		errors.extend(property_errors)
		if property_errors:
			continue

		try:
			payload = load_json_file(file_path)
		except ValueError as error:
			errors.append(str(error))
			continue

		validator = VALIDATORS[request_type]
		validator_target_dir = request_target_dir(args, request_type, properties)
		errors.extend(validate_request_target_dir(request_type, validator_target_dir))
		if errors:
			continue
		errors.extend(validator(payload, args.mode, validator_target_dir, properties))

	return errors


def update_generated_files(args: argparse.Namespace, target_dir: Path, input_files: dict[str, Path]) -> tuple[list[Path], list[str]]:
	"""Update generated Terraform JSON files for implemented request types."""
	updated_files: list[Path] = []
	errors: list[str] = []
	topics_file = input_files.get("topics.json")
	identity_pool_file = input_files.get("identity-pool.json")
	group_mapping_file = input_files.get("group-mapping.json")
	group_mapping_rbac_file = input_files.get("group-mapping-rbac.json")
	rbac_file = input_files.get("rbac.json")
	acl_file = input_files.get("acl.json")

	if topics_file:
		property_file = config_file_for("topic", args.platform_environment)
		try:
			properties = load_properties(property_file)
			payload = load_json_file(topics_file)
			topic_dir = request_target_dir(args, "topic", properties)
			updated_files.extend(update_topic_generated_files(payload, args.mode, topic_dir, properties))
		except (FileNotFoundError, ValueError) as error:
			errors.append(str(error))

	if identity_pool_file:
		property_file = config_file_for("identity_pool", args.platform_environment)
		try:
			properties = load_properties(property_file)
			payload = load_json_file(identity_pool_file)
			identity_pool_dir = request_target_dir(args, "identity_pool", properties)
			updated_files.extend(update_identity_pool_generated_files(payload, args.mode, identity_pool_dir, properties))
		except (FileNotFoundError, ValueError) as error:
			errors.append(str(error))

	if group_mapping_file:
		property_file = config_file_for("group_mapping", args.platform_environment)
		try:
			properties = load_properties(property_file)
			payload = load_json_file(group_mapping_file)
			group_mapping_dir = request_target_dir(args, "group_mapping", properties)
			updated_files.extend(update_group_mapping_generated_files(payload, args.mode, group_mapping_dir, properties))
		except (FileNotFoundError, ValueError) as error:
			errors.append(str(error))

	if group_mapping_rbac_file:
		property_file = config_file_for("group_mapping_rbac", args.platform_environment)
		try:
			properties = load_properties(property_file)
			payload = load_json_file(group_mapping_rbac_file)
			group_mapping_rbac_dir = request_target_dir(args, "group_mapping_rbac", properties)
			updated_files.extend(update_group_mapping_rbac_generated_files(payload, args.mode, group_mapping_rbac_dir, properties))
		except (FileNotFoundError, ValueError) as error:
			errors.append(str(error))

	if rbac_file:
		property_file = config_file_for("rbac", args.platform_environment)
		try:
			properties = load_properties(property_file)
			payload = load_json_file(rbac_file)
			rbac_dir = request_target_dir(args, "rbac", properties)
			updated_files.extend(update_rbac_generated_files(payload, args.mode, rbac_dir, properties))
		except (FileNotFoundError, ValueError) as error:
			errors.append(str(error))

	if acl_file:
		property_file = config_file_for("acl", args.platform_environment)
		try:
			properties = load_properties(property_file)
			payload = load_json_file(acl_file)
			acl_dir = request_target_dir(args, "acl", properties)
			updated_files.extend(update_acl_generated_files(payload, args.mode, acl_dir, properties))
		except (FileNotFoundError, ValueError) as error:
			errors.append(str(error))

	return updated_files, errors


def main() -> int:
	"""Run validation for one set of JSON request files."""
	setup_logging()
	args = parse_args()

	process_config, errors = load_process_config()
	if not errors:
		errors.extend(validate_process_config(process_config))
		logging.info("Loaded process config: %s", PROCESS_CONFIG_FILE.relative_to(CONFIG_DIR))
		logging.info("Git integration enabled: %s", parse_bool_property(process_config, "GIT_ENABLED"))

	target_dir, run_scope_errors = validate_run_scope(args, process_config)
	errors.extend(run_scope_errors)
	input_file_name_regex, expected_input_file_pattern, input_setting_errors = input_file_name_settings(process_config)
	errors.extend(input_setting_errors)
	input_files: dict[str, Path] = {}
	inferred_mode: str | None = None
	inferred_environment: str | None = None
	if input_file_name_regex is not None:
		input_files, inferred_mode, inferred_environment, input_errors = discover_input_files(
			args.input_dir,
			input_file_name_regex,
			expected_input_file_pattern,
		)
		errors.extend(input_errors)
	errors.extend(apply_filename_scope(args, inferred_mode, inferred_environment))

	logging.info(
		"Starting JSON request validation: platform_environment=%s environment=%s cluster=%s mode=%s input_dir=%s",
		args.platform_environment,
		args.environment,
		args.cluster,
		args.mode,
		args.input_dir,
	)

	if not errors:
		errors.extend(validate_input_files(args, target_dir, input_files))

	branch_name: str | None = None
	if not errors:
		branch_name, git_errors = prepare_git_branch(REPO_ROOT, args, process_config)
		errors.extend(git_errors)

	updated_files: list[Path] = []
	archive_dir: Path | None = None
	archived_files: list[Path] = []
	pull_request_url: str | None = None
	if not errors:
		updated_files, update_errors = update_generated_files(args, target_dir, input_files)
		errors.extend(update_errors)

	if not errors:
		archive_dir, archived_files, archive_errors = archive_input_files(args, process_config, input_files)
		errors.extend(archive_errors)

	if not errors:
		git_errors = commit_and_push_git_changes(
			REPO_ROOT,
			args,
			process_config,
			branch_name,
			updated_files,
			archived_files,
			input_files,
		)
		errors.extend(git_errors)

	if not errors:
		pull_request_url, pr_errors = create_pull_request(
			REPO_ROOT,
			args,
			process_config,
			branch_name,
			updated_files,
			archived_files,
		)
		errors.extend(pr_errors)

	if errors:
		logging.error("Validation failed with %s error(s).", len(errors))
		for error in errors:
			logging.error(error)
		return 1

	logging.info("Validation successful. Valid input files: %s", ", ".join(sorted(input_files)))
	if updated_files:
		for file_path in sorted(set(updated_files)):
			logging.info("Updated generated file: %s", file_path.relative_to(REPO_ROOT))
	else:
		logging.info("No generated Terraform JSON files were changed in this step.")

	if archive_dir:
		logging.info("Archived input files to: %s", archive_dir.relative_to(REPO_ROOT))
	if branch_name:
		logging.info("Git branch pushed: %s", branch_name)
	if pull_request_url:
		logging.info("Pull request created: %s", pull_request_url)
	return 0


if __name__ == "__main__":
	raise SystemExit(main())