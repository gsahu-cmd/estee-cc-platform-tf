#!/usr/bin/env python3
"""Common helpers for JSON request validation."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ALLOWED_INPUT_FILES = {
	"topics.json": "topic",
	"rbac.json": "rbac",
	"acl.json": "acl",
	"identity-pool.json": "identity_pool",
	"group-mapping.json": "group_mapping",
	"group-mapping-rbac.json": "group_mapping_rbac",
}

RELEASE_INPUT_FILE_TYPES = {
	"topics": "topics.json",
	"rbac": "rbac.json",
	"acl": "acl.json",
	"identity-pool": "identity-pool.json",
	"group-mapping": "group-mapping.json",
	"group-mapping-rbac": "group-mapping-rbac.json",
}

DEFAULT_INPUT_FILE_NAME_REGEX = (
	r"^(?P<mode>UPSERT|DELETE)-(?P<environment>[A-Za-z0-9-]+)-project-(?P<project>[A-Za-z0-9-]+)-"
	r"release-(?P<number>[0-9]+)-elc-(?P<request_type>topics|rbac|acl|identity-pool|group-mapping|group-mapping-rbac)\.json$"
)
DEFAULT_INPUT_FILE_NAME_PATTERN = "<UPSERT|DELETE>-<ENV>-project-<XYZ>-release-<number>-elc-<topics|rbac|acl|identity-pool|group-mapping|group-mapping-rbac>.json"
REQUIRED_INPUT_FILE_NAME_GROUPS = {"mode", "environment", "request_type"}


def load_properties(property_file: Path) -> dict[str, str]:
	"""Load key=value settings from a property file."""
	properties: dict[str, str] = {}

	if not property_file.exists():
		raise FileNotFoundError(f"Property file not found: {property_file}")

	with property_file.open("r", encoding="utf-8") as file_handle:
		for line_number, raw_line in enumerate(file_handle, start=1):
			line = raw_line.strip()

			if not line or line.startswith("#"):
				continue

			if "=" not in line:
				raise ValueError(
					f"Invalid property format in {property_file} at line {line_number}: {raw_line.rstrip()}"
				)

			key, value = line.split("=", 1)
			properties[key.strip()] = value.strip()

	return properties


def parse_list_property(properties: dict[str, str], key: str) -> set[str]:
	"""Parse a comma-separated property value into a set."""
	return {item.strip() for item in properties.get(key, "").split(",") if item.strip()}


def parse_int_property(properties: dict[str, str], key: str, errors: list[str]) -> int | None:
	"""Parse an integer property and append any validation error."""
	raw_value = properties.get(key, "").strip()

	if not raw_value:
		errors.append(f"Property '{key}' is missing or empty.")
		return None

	try:
		return int(raw_value)
	except ValueError:
		errors.append(f"Property '{key}' must be a number. Current value: '{raw_value}'.")
		return None


def input_file_name_settings(properties: dict[str, str]) -> tuple[re.Pattern[str] | None, str, list[str]]:
	"""Compile filename validation settings from process config."""
	raw_regex = properties.get("INPUT_FILE_NAME_REGEX", DEFAULT_INPUT_FILE_NAME_REGEX).strip()
	expected_pattern = properties.get("INPUT_FILE_NAME_PATTERN", DEFAULT_INPUT_FILE_NAME_PATTERN).strip()
	errors: list[str] = []

	if not raw_regex:
		errors.append("INPUT_FILE_NAME_REGEX is mandatory in process config.")
		return None, expected_pattern or DEFAULT_INPUT_FILE_NAME_PATTERN, errors

	if not expected_pattern:
		expected_pattern = DEFAULT_INPUT_FILE_NAME_PATTERN

	try:
		compiled_regex = re.compile(raw_regex)
	except re.error as error:
		return None, expected_pattern, [f"INPUT_FILE_NAME_REGEX is invalid: {error}"]

	missing_groups = REQUIRED_INPUT_FILE_NAME_GROUPS - set(compiled_regex.groupindex)
	if missing_groups:
		errors.append("INPUT_FILE_NAME_REGEX must define named group(s): " + ", ".join(sorted(missing_groups)))

	return compiled_regex, expected_pattern, errors


def load_json_file(file_path: Path) -> Any:
	"""Load one JSON file and raise a useful error on invalid JSON."""
	try:
		with file_path.open("r", encoding="utf-8-sig") as file_handle:
			return json.load(file_handle)
	except json.JSONDecodeError as error:
		raise ValueError(f"{file_path.name} is not valid JSON: {error}") from error


def load_existing_json(file_path: Path) -> dict[str, Any]:
	"""Load an existing generated JSON object, or return an empty object when absent."""
	if not file_path.exists():
		return {}

	data = load_json_file(file_path)
	if not isinstance(data, dict):
		raise ValueError(f"Existing generated file must contain a JSON object: {file_path}")

	return data


def write_json_file(file_path: Path, data: Any) -> None:
	"""Write generated JSON with stable formatting."""
	file_path.parent.mkdir(parents=True, exist_ok=True)

	with file_path.open("w", encoding="utf-8") as file_handle:
		json.dump(data, file_handle, indent=2, sort_keys=True)
		file_handle.write("\n")


def discover_input_files(
	input_dir: Path,
	input_file_name_regex: re.Pattern[str],
	expected_input_file_pattern: str,
) -> tuple[dict[str, Path], str | None, str | None, list[str]]:
	"""Find release-style JSON request files in the input directory and derive mode from their names."""
	errors: list[str] = []

	if not input_dir.exists():
		return {}, None, None, [f"Input directory does not exist: {input_dir}"]

	if not input_dir.is_dir():
		return {}, None, None, [f"Input path is not a directory: {input_dir}"]

	json_files = sorted(path for path in input_dir.iterdir() if path.is_file() and path.suffix.lower() == ".json")
	allowed_files: dict[str, Path] = {}
	unsupported_files: list[str] = []
	discovered_modes: set[str] = set()
	discovered_environments: set[str] = set()

	for path in json_files:
		match = input_file_name_regex.fullmatch(path.name)
		if not match:
			unsupported_files.append(path.name)
			continue

		discovered_modes.add(match.group("mode"))
		discovered_environments.add(match.group("environment"))
		request_type = match.group("request_type")
		canonical_file_name = RELEASE_INPUT_FILE_TYPES[request_type]
		if canonical_file_name in allowed_files:
			errors.append(
				f"Duplicate input request type '{request_type}'. Only one {request_type} JSON file is allowed per run."
			)
			continue

		allowed_files[canonical_file_name] = path

	if unsupported_files:
		errors.append(
			"Unsupported input JSON file name(s): "
			+ ", ".join(unsupported_files)
			+ f". Expected pattern: {expected_input_file_pattern}"
		)

	if len(allowed_files) < 1:
		errors.append("Input directory must contain at least one supported release-style JSON file.")

	if len(allowed_files) > len(ALLOWED_INPUT_FILES):
		errors.append(f"Input directory can contain a maximum of {len(ALLOWED_INPUT_FILES)} supported JSON files.")

	if len(discovered_modes) > 1:
		errors.append("Input directory must not mix UPSERT and DELETE request files in the same run.")

	if len(discovered_environments) > 1:
		errors.append("Input directory must not mix environment values in the same run.")

	inferred_mode = next(iter(discovered_modes)) if len(discovered_modes) == 1 else None
	inferred_environment = next(iter(discovered_environments)) if len(discovered_environments) == 1 else None
	return allowed_files, inferred_mode, inferred_environment, errors


def require_object(data: Any, file_name: str) -> dict[str, Any] | None:
	"""Return data as a JSON object or None when invalid."""
	if not isinstance(data, dict):
		return None

	return data


def validate_delete_keys(request_data: Any, existing_data: dict[str, Any], file_name: str) -> list[str]:
	"""Validate DELETE payload keys exist in current generated JSON."""
	errors: list[str] = []

	if not isinstance(request_data, list):
		return [f"{file_name}: DELETE payload must be a non-empty JSON array of names."]

	if not request_data:
		return [f"{file_name}: DELETE payload must contain at least one key."]

	for key in request_data:
		if not isinstance(key, str) or not key.strip():
			errors.append(f"{file_name}: DELETE keys must be non-empty strings.")
			continue

		if key not in existing_data:
			errors.append(f"{file_name}: DELETE key '{key}' does not exist in generated JSON.")

	return errors


def target_topic_stack_dir(repo_root: Path, platform_environment: str, environment: str, cluster: str) -> Path:
	"""Return the Terraform topic stack directory for the selected environment and cluster."""
	return repo_root / "main" / "topics" / platform_environment / environment / cluster