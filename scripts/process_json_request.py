#!/usr/bin/env python3
"""Validate JSON request files before catalog JSON generation."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Any, Callable


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
CONFIG_DIR = SCRIPT_DIR / "config"
PROCESS_CONFIG_FILE = CONFIG_DIR / "process_json_request.properties"

if str(SCRIPT_DIR) not in sys.path:
	sys.path.insert(0, str(SCRIPT_DIR))

from json_request.acl_validator import validate_acl
from json_request.common import (
	ALLOWED_INPUT_FILES,
	discover_input_files,
	load_json_file,
	load_properties,
	parse_list_property,
	target_topic_stack_dir,
)
from json_request.identity_pool_validator import validate_identity_pool
from json_request.rbac_validator import validate_rbac
from json_request.topic_validator import validate_topics


Validator = Callable[[Any, str, Path, dict[str, str]], list[str]]

VALIDATORS: dict[str, Validator] = {
	"topic": validate_topics,
	"rbac": validate_rbac,
	"acl": validate_acl,
	"identity_pool": validate_identity_pool,
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
	parser.add_argument("--mode", required=True, choices=["UPSERT", "DELETE"])
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

	if git_enabled:
		errors.append("GIT_ENABLED=true is not supported yet. Current script is validation-only.")

	return errors


def validate_run_scope(args: argparse.Namespace) -> tuple[Path, list[str]]:
	"""Validate run-level target arguments and return the target Terraform folder."""
	errors: list[str] = []
	target_dir = target_topic_stack_dir(REPO_ROOT, args.platform_environment, args.environment, args.cluster)

	if not target_dir.exists():
		errors.append(f"Target Terraform folder does not exist: {target_dir}")
	elif not target_dir.is_dir():
		errors.append(f"Target Terraform path is not a folder: {target_dir}")

	return target_dir, errors


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

		errors.extend(validate_properties(properties, request_type, args.platform_environment, args.mode))

		try:
			payload = load_json_file(file_path)
		except ValueError as error:
			errors.append(str(error))
			continue

		validator = VALIDATORS[request_type]
		errors.extend(validator(payload, args.mode, target_dir, properties))

	return errors


def main() -> int:
	"""Run validation for one set of JSON request files."""
	setup_logging()
	args = parse_args()

	logging.info(
		"Starting JSON request validation: platform_environment=%s environment=%s cluster=%s mode=%s input_dir=%s",
		args.platform_environment,
		args.environment,
		args.cluster,
		args.mode,
		args.input_dir,
	)

	process_config, errors = load_process_config()
	if not errors:
		errors.extend(validate_process_config(process_config))
		logging.info("Loaded process config: %s", PROCESS_CONFIG_FILE.relative_to(CONFIG_DIR))
		logging.info("Git integration enabled: %s", parse_bool_property(process_config, "GIT_ENABLED"))

	target_dir, run_scope_errors = validate_run_scope(args)
	errors.extend(run_scope_errors)
	input_files, input_errors = discover_input_files(args.input_dir)
	errors.extend(input_errors)

	if not errors:
		errors.extend(validate_input_files(args, target_dir, input_files))

	if errors:
		logging.error("Validation failed with %s error(s).", len(errors))
		for error in errors:
			logging.error(error)
		return 1

	logging.info("Validation successful. Valid input files: %s", ", ".join(sorted(input_files)))
	logging.info("No generated Terraform JSON files were changed in this validation-only step.")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())