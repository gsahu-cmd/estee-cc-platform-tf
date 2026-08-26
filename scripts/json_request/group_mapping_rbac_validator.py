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


def expected_group_mapping_key_segment(binding: dict[str, Any], rbac_key_prefix: str) -> str | None:
	"""Return the required group-mapping segment for an RBAC binding key."""
	group_mapping_name = binding.get("group_mapping_name")
	if not isinstance(group_mapping_name, str) or not group_mapping_name.strip():
		return None

	group_mapping_prefix = rbac_key_prefix.removeprefix("rbac-") + "-"
	name = group_mapping_name.strip()
	if name.startswith(group_mapping_prefix):
		name = name[len(group_mapping_prefix):]

	return rbac_key_segment(name) or None


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
	if not rbac_key_prefix:
		platform_environment = properties.get("VALID_PLATFORM_ENVIRONMENT", "").strip().lower()
		rbac_key_prefix = f"rbac-elc-gm-{platform_environment}" if platform_environment else "rbac-"

	for binding_key, binding in data.items():
		item_label = f"group-mapping-rbac.json[{binding_key}]"
		if not isinstance(binding_key, str) or not binding_key.strip():
			errors.append("group-mapping-rbac.json: binding keys must be non-empty strings.")
		elif not binding_key.startswith(f"{rbac_key_prefix}-"):
			errors.append(f"{item_label}: binding key must start with '{rbac_key_prefix}-'.")

		if not isinstance(binding, dict):
			errors.append(f"{item_label}: value must be an object.")
			continue


		group_mapping_id = binding.get("group_mapping_id")
		group_mapping_name = binding.get("group_mapping_name")
		if bool(group_mapping_id) == bool(group_mapping_name):
			errors.append(f"{item_label}: provide exactly one of group_mapping_name or group_mapping_id.")

		for required_field in ("role_name", "resource_kind"):
			if not isinstance(binding.get(required_field), str) or not binding.get(required_field, "").strip():
				errors.append(f"{item_label}: {required_field} is mandatory.")

		expected_binding_key_suffix = expected_group_mapping_rbac_key_suffix(binding)
		if expected_binding_key_suffix and isinstance(binding_key, str):
			expected_suffix = f"-{expected_binding_key_suffix}"
			expected_key_start = f"{rbac_key_prefix}-"
			free_text = binding_key[len(expected_key_start):-len(expected_suffix)] if binding_key.startswith(expected_key_start) else ""
			if not binding_key.endswith(expected_suffix) or not free_text.strip("-"):
				errors.append(
					f"{item_label}: binding key must use '{expected_key_start}<group-mapping-name-or-free-text>{expected_suffix}' "
					"derived from role_name, resource_kind, and resource_name/resource_name_prefix."
				)
			else:
				expected_group_mapping_segment = expected_group_mapping_key_segment(binding, rbac_key_prefix)
				if expected_group_mapping_segment and free_text != expected_group_mapping_segment:
					errors.append(
						f"{item_label}: binding key group-mapping segment must be '{expected_group_mapping_segment}' "
						f"when group_mapping_name is '{binding.get('group_mapping_name')}'."
					)

		for optional_field in ("group_mapping_name", "group_mapping_id", "resource_name", "resource_name_prefix", "organization_crn", "crn_pattern_override"):
			if optional_field in binding and binding.get(optional_field) is not None:
				if not isinstance(binding.get(optional_field), str) or not binding.get(optional_field, "").strip():
					errors.append(f"{item_label}: {optional_field} must be a non-empty string when provided.")

		if "disable_wait_for_ready" in binding and not isinstance(binding.get("disable_wait_for_ready"), bool):
			errors.append(f"{item_label}: disable_wait_for_ready must be true or false when provided.")

		resource_kind = binding.get("resource_kind", "")
		if resource_kind and resource_kind not in valid_resource_kinds:
			errors.append(f"{item_label}: resource_kind '{resource_kind}' is not valid.")

		if binding.get("resource_name") and binding.get("resource_name_prefix"):
			errors.append(f"{item_label}: provide either resource_name or resource_name_prefix, not both.")

		if resource_kind == "topic":
			if not binding.get("resource_name") and not binding.get("resource_name_prefix"):
				errors.append(f"{item_label}: resource_name or resource_name_prefix is mandatory for resource_kind 'topic'.")

		if binding.get("resource_name_prefix") and resource_kind != "topic":
			errors.append(f"{item_label}: resource_name_prefix is currently supported only for resource_kind 'topic'.")

		if resource_kind in {"consumer_group", "transactional_id", "connector", "service_account"}:
			if not isinstance(binding.get("resource_name"), str) or not binding.get("resource_name", "").strip():
				errors.append(f"{item_label}: resource_name is mandatory for resource_kind '{resource_kind}'.")

	return errors
