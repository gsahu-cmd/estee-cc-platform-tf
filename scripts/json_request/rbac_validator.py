#!/usr/bin/env python3
"""RBAC JSON request validation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from json_request.common import load_existing_json, parse_list_property, validate_delete_keys


def validate_rbac(data: Any, mode: str, target_dir: Path, properties: dict[str, str]) -> list[str]:
	"""Validate rbac.json for UPSERT or DELETE mode."""
	if mode == "DELETE":
		generated_file = target_dir / properties.get("GENERATED_RBAC_FILE", "files/elc-rbac.json")
		return validate_delete_keys(data, load_existing_json(generated_file), "rbac.json")

	if not isinstance(data, dict) or not data:
		return ["rbac.json: UPSERT payload must be a non-empty JSON object keyed by RBAC binding name."]

	errors: list[str] = []
	valid_resource_kinds = parse_list_property(properties, "VALID_RESOURCE_KINDS")

	for binding_key, binding in data.items():
		item_label = f"rbac.json[{binding_key}]"
		if not isinstance(binding_key, str) or not binding_key.strip():
			errors.append("rbac.json: binding keys must be non-empty strings.")

		if not isinstance(binding, dict):
			errors.append(f"{item_label}: value must be an object.")
			continue

		for required_field in ("identity_pool_id", "role_name", "resource_kind"):
			if not isinstance(binding.get(required_field), str) or not binding.get(required_field, "").strip():
				errors.append(f"{item_label}: {required_field} is mandatory.")

		resource_kind = binding.get("resource_kind", "")
		if resource_kind and resource_kind not in valid_resource_kinds:
			errors.append(f"{item_label}: resource_kind '{resource_kind}' is not valid.")

		if resource_kind in {"topic", "consumer_group", "transactional_id", "connector", "service_account"}:
			if not isinstance(binding.get("resource_name"), str) or not binding.get("resource_name", "").strip():
				errors.append(f"{item_label}: resource_name is mandatory for resource_kind '{resource_kind}'.")

	return errors