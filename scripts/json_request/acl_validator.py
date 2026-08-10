#!/usr/bin/env python3
"""ACL JSON request validation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from json_request.common import load_existing_json, parse_list_property, validate_delete_keys


def validate_acl(data: Any, mode: str, target_dir: Path, properties: dict[str, str]) -> list[str]:
	"""Validate acl.json for UPSERT or DELETE mode."""
	if mode == "DELETE":
		generated_file = target_dir / properties.get("GENERATED_ACL_FILE", "files/elc-acl.json")
		return validate_delete_keys(data, load_existing_json(generated_file), "acl.json")

	if not isinstance(data, dict) or not data:
		return ["acl.json: UPSERT payload must be a non-empty JSON object keyed by ACL name."]

	errors: list[str] = []
	valid_resource_types = parse_list_property(properties, "VALID_RESOURCE_TYPES")
	valid_pattern_types = parse_list_property(properties, "VALID_PATTERN_TYPES")
	valid_operations = parse_list_property(properties, "VALID_OPERATIONS")
	valid_permissions = parse_list_property(properties, "VALID_PERMISSIONS")
	acl_key_prefix = properties.get("ACL_KEY_PREFIX", "").strip()
	if not acl_key_prefix:
		platform_environment = properties.get("VALID_PLATFORM_ENVIRONMENT", "").strip().lower()
		acl_key_prefix = f"acl-elc-{platform_environment}" if platform_environment else "acl-"

	for acl_key, acl in data.items():
		item_label = f"acl.json[{acl_key}]"
		if not isinstance(acl_key, str) or not acl_key.strip():
			errors.append("acl.json: ACL keys must be non-empty strings.")
		elif not acl_key.startswith(f"{acl_key_prefix}-"):
			errors.append(f"{item_label}: ACL key must start with '{acl_key_prefix}-'.")

		if not isinstance(acl, dict):
			errors.append(f"{item_label}: value must be an object.")
			continue

		if "identity_pool_id" in acl:
			errors.append(f"{item_label}: identity_pool_id is not used for ACLs. Provide the Kafka principal field instead, for example 'User:<principal-id>'.")

		for required_field in ("resource_type", "resource_name", "pattern_type", "principal", "operation", "permission"):
			if not isinstance(acl.get(required_field), str) or not acl.get(required_field, "").strip():
				errors.append(f"{item_label}: {required_field} is mandatory.")

		resource_type = acl.get("resource_type", "")
		pattern_type = acl.get("pattern_type", "")
		operation = acl.get("operation", "")
		permission = acl.get("permission", "")
		host = acl.get("host", "*")

		if resource_type and resource_type not in valid_resource_types:
			errors.append(f"{item_label}: resource_type '{resource_type}' is not valid.")

		if pattern_type and pattern_type not in valid_pattern_types:
			errors.append(f"{item_label}: pattern_type '{pattern_type}' is not valid.")

		if operation and operation not in valid_operations:
			errors.append(f"{item_label}: operation '{operation}' is not valid.")

		if permission and permission not in valid_permissions:
			errors.append(f"{item_label}: permission '{permission}' is not valid.")

		if resource_type == "CLUSTER" and acl.get("resource_name") != "kafka-cluster":
			errors.append(f"{item_label}: resource_name must be kafka-cluster when resource_type is CLUSTER.")

		if not isinstance(host, str) or not host.strip():
			errors.append(f"{item_label}: host must be a non-empty string when provided.")

	return errors