#!/usr/bin/env python3
"""Generate Terraform JSON files from acl.json requests."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from json_request.common import load_existing_json, write_json_file


ACL_REQUIRED_FIELDS = ("resource_type", "resource_name", "pattern_type", "principal", "operation", "permission")


def acl_file_path(target_dir: Path, properties: dict[str, str]) -> Path:
	"""Resolve the generated ACL file path under the selected Terraform stack."""
	return target_dir / properties.get("GENERATED_ACL_FILE", "files/elc-acl.json")


def normalized_acl(acl: dict[str, Any]) -> dict[str, Any]:
	"""Return the Terraform JSON shape for one ACL request."""
	normalized = {field_name: acl.get(field_name) for field_name in ACL_REQUIRED_FIELDS}
	normalized["host"] = acl.get("host", "*")
	return normalized


def upsert_acls(request_data: dict[str, Any], target_dir: Path, properties: dict[str, str]) -> list[Path]:
	"""Apply UPSERT ACL requests to generated Terraform JSON."""
	acl_file = acl_file_path(target_dir, properties)
	acls = load_existing_json(acl_file)

	for acl_key, acl in request_data.items():
		if isinstance(acl, dict):
			acls[acl_key] = normalized_acl(acl)

	write_json_file(acl_file, acls)
	return [acl_file]


def delete_acls(request_data: list[Any], target_dir: Path, properties: dict[str, str]) -> list[Path]:
	"""Apply DELETE ACL requests to generated Terraform JSON."""
	acl_file = acl_file_path(target_dir, properties)
	acls = load_existing_json(acl_file)

	for acl_key in request_data:
		if isinstance(acl_key, str):
			acls.pop(acl_key, None)

	write_json_file(acl_file, acls)
	return [acl_file]


def update_acl_generated_files(
	request_data: Any,
	mode: str,
	target_dir: Path,
	properties: dict[str, str],
) -> list[Path]:
	"""Update generated Terraform JSON files for acl.json."""
	if mode == "DELETE":
		if not isinstance(request_data, list):
			raise ValueError("acl.json DELETE generation requires a JSON array.")
		return delete_acls(request_data, target_dir, properties)

	if not isinstance(request_data, dict):
		raise ValueError("acl.json UPSERT generation requires a JSON object.")

	return upsert_acls(request_data, target_dir, properties)