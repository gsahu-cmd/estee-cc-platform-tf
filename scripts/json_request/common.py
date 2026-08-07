#!/usr/bin/env python3
"""Common helpers for JSON request validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ALLOWED_INPUT_FILES = {
	"topics.json": "topic",
	"rbac.json": "rbac",
	"acl.json": "acl",
	"identity-pool.json": "identity_pool",
}


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


def discover_input_files(input_dir: Path) -> tuple[dict[str, Path], list[str]]:
	"""Find allowed JSON request files in the input directory."""
	errors: list[str] = []

	if not input_dir.exists():
		return {}, [f"Input directory does not exist: {input_dir}"]

	if not input_dir.is_dir():
		return {}, [f"Input path is not a directory: {input_dir}"]

	json_files = sorted(path for path in input_dir.iterdir() if path.is_file() and path.suffix.lower() == ".json")
	unsupported_files = [path.name for path in json_files if path.name not in ALLOWED_INPUT_FILES]

	if unsupported_files:
		errors.append("Unsupported input JSON file(s): " + ", ".join(unsupported_files))

	allowed_files = {path.name: path for path in json_files if path.name in ALLOWED_INPUT_FILES}

	if len(allowed_files) < 1:
		errors.append("Input directory must contain at least one supported JSON file.")

	if len(allowed_files) > 4:
		errors.append("Input directory can contain a maximum of four supported JSON files.")

	return allowed_files, errors


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