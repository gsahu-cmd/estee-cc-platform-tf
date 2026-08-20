#!/usr/bin/env python3
"""RBAC JSON request validation."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from json_request.common import load_existing_json, parse_list_property, validate_delete_keys


def rbac_key_segment(value: str) -> str:
	"""Return one stable lowercase segment for an RBAC binding key."""
	return re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")


def expected_rbac_binding_key_suffix(binding: dict[str, Any]) -> str | None:
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


def validate_rbac(data: Any, mode: str, target_dir: Path, properties: dict[str, str]) -> list[str]:
	"""Validate rbac.json for UPSERT or DELETE mode."""
	if mode == "DELETE":
		generated_file = target_dir / properties.get("GENERATED_RBAC_FILE", "files/elc-rbac.json")
		return validate_delete_keys(data, load_existing_json(generated_file), "rbac.json")

	if not isinstance(data, dict) or not data:
		return ["rbac.json: UPSERT payload must be a non-empty JSON object keyed by RBAC binding name."]

	errors: list[str] = []
	valid_resource_kinds = parse_list_property(properties, "VALID_RESOURCE_KINDS")
	rbac_key_prefix = properties.get("RBAC_KEY_PREFIX", "").strip()
	if not rbac_key_prefix:
		platform_environment = properties.get("VALID_PLATFORM_ENVIRONMENT", "").strip().lower()
		rbac_key_prefix = f"rbac-elc-ip-{platform_environment}" if platform_environment else "rbac-"

	for binding_key, binding in data.items():
		item_label = f"rbac.json[{binding_key}]"
		if not isinstance(binding_key, str) or not binding_key.strip():
			errors.append("rbac.json: binding keys must be non-empty strings.")
		elif not binding_key.startswith(f"{rbac_key_prefix}-"):
			errors.append(f"{item_label}: binding key must start with '{rbac_key_prefix}-'.")

		if not isinstance(binding, dict):
			errors.append(f"{item_label}: value must be an object.")
			continue

		for required_field in ("identity_pool_id", "role_name", "resource_kind"):
			if not isinstance(binding.get(required_field), str) or not binding.get(required_field, "").strip():
				errors.append(f"{item_label}: {required_field} is mandatory.")

		expected_binding_key_suffix = expected_rbac_binding_key_suffix(binding)
		if expected_binding_key_suffix and isinstance(binding_key, str):
			expected_suffix = f"-{expected_binding_key_suffix}"
			expected_key_start = f"{rbac_key_prefix}-"
			free_text = binding_key[len(expected_key_start):-len(expected_suffix)] if binding_key.startswith(expected_key_start) else ""
			if not binding_key.endswith(expected_suffix) or not free_text.strip("-"):
				errors.append(
					f"{item_label}: binding key must use '{expected_key_start}<identity-pool-name-or-free-text>{expected_suffix}' "
					"derived from role_name, resource_kind, and resource_name/resource_name_prefix."
				)

		for optional_field in ("resource_name", "resource_name_prefix", "organization_crn", "crn_pattern_override"):
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