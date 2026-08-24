#!/usr/bin/env python3
"""Group mapping RBAC JSON request validation."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from json_request.common import load_existing_json, parse_list_property, validate_delete_keys


def rbac_key_segment(value: str) -> str:
	"""Return one stable lowercase segment for an RBAC binding key."""
	return re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")


def expected_group_mapping_rbac_key_suffix(binding: dict[str, Any]) -> str | None:
	"""Build the required RBAC key suffix from binding fields."""
	resource_identifier = binding.get("resource_name") or binding.get("resource_name_prefix")
	raw_segments = [
		binding.get("group_mapping_id"),
		binding.get("role_name"),
		binding.get("resource_kind"),
	]

	if resource_identifier:
		raw_segments.append(resource_identifier)

	if not all(isinstance(segment, str) and segment.strip() for segment in raw_segments):
		return None

	segments = [rbac_key_segment(segment) for segment in raw_segments]
	if not all(segments):
		return None

	return "-".join(segments)


def validate_group_mapping_rbac(data: Any, mode: str, target_dir: Path, properties: dict[str, str]) -> list[str]:
	"""Validate group-mapping-rbac.json for UPSERT or DELETE mode."""
	if mode == "DELETE":
		generated_file = target_dir / properties.get("GENERATED_GROUP_MAPPING_RBAC_FILE", "files/elc-group-mapping-rbac.json")
		return validate_delete_keys(data, load_existing_json(generated_file), "group-mapping-rbac.json")

	if not isinstance(data, dict) or not data:
		return ["group-mapping-rbac.json: UPSERT payload must be a non-empty JSON object keyed by RBAC binding name."]

	errors: list[str] = []
	valid_resource_kinds = parse_list_property(properties, "VALID_RESOURCE_KINDS")
	rbac_key_prefix = properties.get("GROUP_MAPPING_RBAC_KEY_PREFIX", "").strip()

	for binding_key, binding in data.items():
		item_label = f"group-mapping-rbac.json[{binding_key}]"
		if not isinstance(binding_key, str) or not binding_key.strip():
			errors.append("group-mapping-rbac.json: binding keys must be non-empty strings.")
		elif rbac_key_prefix and not binding_key.startswith(f"{rbac_key_prefix}-"):
			errors.append(f"{item_label}: binding key must start with '{rbac_key_prefix}-'.")

		if not isinstance(binding, dict):
			errors.append(f"{item_label}: value must be an object.")
			continue

		group_mapping_id = binding.get("group_mapping_id")
		if not isinstance(group_mapping_id, str) or not group_mapping_id.strip():
			errors.append(f"{item_label}: group_mapping_id must be a non-empty string when provided.")

		for required_field in ("role_name", "resource_kind"):
			if not isinstance(binding.get(required_field), str) or not binding.get(required_field, "").strip():
				errors.append(f"{item_label}: {required_field} is mandatory.")

		expected_binding_key_suffix = expected_group_mapping_rbac_key_suffix(binding)
		if expected_binding_key_suffix and isinstance(binding_key, str) and rbac_key_prefix:
			expected_key = f"{rbac_key_prefix}-{expected_binding_key_suffix}"
			if binding_key != expected_key:
				errors.append(f"{item_label}: binding key must be '{expected_key}'.")

		for optional_field in ("organization_crn", "crn_pattern_override"):
			if optional_field in binding and binding.get(optional_field) is not None:
				if not isinstance(binding.get(optional_field), str) or not binding.get(optional_field, "").strip():
					errors.append(f"{item_label}: {optional_field} must be a non-empty string when provided.")

		if "disable_wait_for_ready" in binding and not isinstance(binding.get("disable_wait_for_ready"), bool):
			errors.append(f"{item_label}: disable_wait_for_ready must be true or false when provided.")

		resource_kind = binding.get("resource_kind", "")
		if resource_kind and resource_kind not in valid_resource_kinds:
			errors.append(f"{item_label}: resource_kind '{resource_kind}' is not valid.")

	return errors
