#!/usr/bin/env python3
"""Generate Terraform JSON files from group-mapping-rbac.json requests."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from json_request.common import load_existing_json, write_json_file


GROUP_MAPPING_RBAC_REQUIRED_FIELDS = ("role_name", "resource_kind")
GROUP_MAPPING_RBAC_OPTIONAL_FIELDS = (
	"group_mapping_name",
	"group_mapping_id",
	"resource_name",
	"resource_name_prefix",
	"organization_crn",
	"crn_pattern_override",
	"disable_wait_for_ready",
)


def group_mapping_rbac_file_path(target_dir: Path, properties: dict[str, str]) -> Path:
	"""Resolve the generated group-mapping RBAC file path."""
	return target_dir / properties.get("GENERATED_GROUP_MAPPING_RBAC_FILE", "files/elc-group-mapping-rbac.json")


def normalized_group_mapping_rbac_binding(binding: dict[str, Any]) -> dict[str, Any]:
	"""Return the Terraform JSON shape for one group-mapping RBAC request."""
	normalized: dict[str, Any] = {}

	for field_name in GROUP_MAPPING_RBAC_REQUIRED_FIELDS:
		normalized[field_name] = binding.get(field_name)

	for field_name in GROUP_MAPPING_RBAC_OPTIONAL_FIELDS:
		if field_name in binding and binding.get(field_name) is not None:
			normalized[field_name] = binding.get(field_name)

	return normalized


def upsert_group_mapping_rbac_bindings(request_data: dict[str, Any], target_dir: Path, properties: dict[str, str]) -> list[Path]:
	"""Apply UPSERT group-mapping RBAC requests to generated Terraform JSON."""
	group_mapping_rbac_file = group_mapping_rbac_file_path(target_dir, properties)
	group_mapping_rbac_bindings = load_existing_json(group_mapping_rbac_file)

	for binding_key, binding in request_data.items():
		if isinstance(binding, dict):
			group_mapping_rbac_bindings[binding_key] = normalized_group_mapping_rbac_binding(binding)

	write_json_file(group_mapping_rbac_file, group_mapping_rbac_bindings)
	return [group_mapping_rbac_file]


def delete_group_mapping_rbac_bindings(request_data: list[Any], target_dir: Path, properties: dict[str, str]) -> list[Path]:
	"""Apply DELETE group-mapping RBAC requests to generated Terraform JSON."""
	group_mapping_rbac_file = group_mapping_rbac_file_path(target_dir, properties)
	group_mapping_rbac_bindings = load_existing_json(group_mapping_rbac_file)

	for binding_key in request_data:
		if isinstance(binding_key, str):
			group_mapping_rbac_bindings.pop(binding_key, None)

	write_json_file(group_mapping_rbac_file, group_mapping_rbac_bindings)
	return [group_mapping_rbac_file]


def update_group_mapping_rbac_generated_files(
	request_data: Any,
	mode: str,
	target_dir: Path,
	properties: dict[str, str],
) -> list[Path]:
	"""Update generated Terraform JSON files for group-mapping-rbac.json."""
	if mode == "DELETE":
		if not isinstance(request_data, list):
			raise ValueError("group-mapping-rbac.json DELETE generation requires a JSON array.")
		return delete_group_mapping_rbac_bindings(request_data, target_dir, properties)

	if not isinstance(request_data, dict):
		raise ValueError("group-mapping-rbac.json UPSERT generation requires a JSON object.")

	return upsert_group_mapping_rbac_bindings(request_data, target_dir, properties)
