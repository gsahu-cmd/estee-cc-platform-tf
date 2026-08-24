#!/usr/bin/env python3
"""Generate Terraform JSON files from rbac.json requests."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from json_request.common import load_existing_json, write_json_file


RBAC_REQUIRED_FIELDS = ("role_name", "resource_kind")
RBAC_OPTIONAL_FIELDS = (
	"identity_pool_name",
	"resource_name",
	"resource_name_prefix",
	"identity_pool_id",
	"organization_crn",
	"crn_pattern_override",
	"disable_wait_for_ready",
)


def rbac_file_path(target_dir: Path, properties: dict[str, str]) -> Path:
	"""Resolve the generated RBAC file path under the selected Terraform stack."""
	return target_dir / properties.get("GENERATED_RBAC_FILE", "files/elc-rbac.json")


def normalized_rbac_binding(binding: dict[str, Any]) -> dict[str, Any]:
	"""Return the Terraform JSON shape for one RBAC binding request."""
	normalized: dict[str, Any] = {}

	for field_name in RBAC_REQUIRED_FIELDS:
		normalized[field_name] = binding.get(field_name)

	for field_name in RBAC_OPTIONAL_FIELDS:
		if field_name in binding and binding.get(field_name) is not None:
			normalized[field_name] = binding.get(field_name)

	return normalized


def upsert_rbac_bindings(request_data: dict[str, Any], target_dir: Path, properties: dict[str, str]) -> list[Path]:
	"""Apply UPSERT RBAC requests to generated Terraform JSON."""
	rbac_file = rbac_file_path(target_dir, properties)
	rbac_bindings = load_existing_json(rbac_file)

	for binding_key, binding in request_data.items():
		if isinstance(binding, dict):
			rbac_bindings[binding_key] = normalized_rbac_binding(binding)

	write_json_file(rbac_file, rbac_bindings)
	return [rbac_file]


def delete_rbac_bindings(request_data: list[Any], target_dir: Path, properties: dict[str, str]) -> list[Path]:
	"""Apply DELETE RBAC requests to generated Terraform JSON."""
	rbac_file = rbac_file_path(target_dir, properties)
	rbac_bindings = load_existing_json(rbac_file)

	for binding_key in request_data:
		if isinstance(binding_key, str):
			rbac_bindings.pop(binding_key, None)

	write_json_file(rbac_file, rbac_bindings)
	return [rbac_file]


def update_rbac_generated_files(
	request_data: Any,
	mode: str,
	target_dir: Path,
	properties: dict[str, str],
) -> list[Path]:
	"""Update generated Terraform JSON files for rbac.json."""
	if mode == "DELETE":
		if not isinstance(request_data, list):
			raise ValueError("rbac.json DELETE generation requires a JSON array.")
		return delete_rbac_bindings(request_data, target_dir, properties)

	if not isinstance(request_data, dict):
		raise ValueError("rbac.json UPSERT generation requires a JSON object.")

	return upsert_rbac_bindings(request_data, target_dir, properties)