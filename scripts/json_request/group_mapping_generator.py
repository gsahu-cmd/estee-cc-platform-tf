#!/usr/bin/env python3
"""Generate Terraform JSON files from group-mapping.json requests."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from json_request.common import load_existing_json, write_json_file


def group_mapping_stack_dir(repo_root: Path, platform_environment: str) -> Path:
	"""Return the SSO Terraform stack directory for the platform environment."""
	return repo_root / "main" / "org" / "sso-ip" / platform_environment


def group_mapping_file_path(target_dir: Path, properties: dict[str, str]) -> Path:
	"""Resolve the generated group-mapping file path."""
	return target_dir / properties.get("GENERATED_GROUP_MAPPING_FILE", "files/elc-group-mappings.json")


def upsert_group_mappings(request_data: dict[str, Any], target_dir: Path, properties: dict[str, str]) -> list[Path]:
	"""Apply UPSERT group-mapping requests to generated Terraform JSON."""
	group_mapping_file = group_mapping_file_path(target_dir, properties)
	group_mappings = load_existing_json(group_mapping_file)

	for group_mapping_name, group_mapping in request_data.items():
		if not isinstance(group_mapping, dict):
			continue

		generated_group_mapping = {
			"display_name": group_mapping.get("display_name"),
			"filter": group_mapping.get("filter"),
		}
		if group_mapping.get("description") is not None:
			generated_group_mapping["description"] = group_mapping.get("description")

		group_mappings[group_mapping_name] = generated_group_mapping

	write_json_file(group_mapping_file, group_mappings)
	return [group_mapping_file]


def delete_group_mappings(request_data: list[Any], target_dir: Path, properties: dict[str, str]) -> list[Path]:
	"""Apply DELETE group-mapping requests to generated Terraform JSON."""
	group_mapping_file = group_mapping_file_path(target_dir, properties)
	group_mappings = load_existing_json(group_mapping_file)

	for group_mapping_name in request_data:
		if isinstance(group_mapping_name, str):
			group_mappings.pop(group_mapping_name, None)

	write_json_file(group_mapping_file, group_mappings)
	return [group_mapping_file]


def update_group_mapping_generated_files(
	request_data: Any,
	mode: str,
	target_dir: Path,
	properties: dict[str, str],
) -> list[Path]:
	"""Update generated Terraform JSON files for group-mapping.json."""
	if mode == "DELETE":
		if not isinstance(request_data, list):
			raise ValueError("group-mapping.json DELETE generation requires a JSON array.")
		return delete_group_mappings(request_data, target_dir, properties)

	if not isinstance(request_data, dict):
		raise ValueError("group-mapping.json UPSERT generation requires a JSON object.")

	return upsert_group_mappings(request_data, target_dir, properties)
