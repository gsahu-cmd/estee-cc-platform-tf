#!/usr/bin/env python3
"""Group mapping JSON request validation."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from json_request.common import load_existing_json, validate_delete_keys


def validate_group_mapping_name(
	group_mapping_name: Any,
	item_label: str,
	name_pattern: re.Pattern[str],
	name_regex: str,
	required_prefix: str,
) -> list[str]:
	"""Validate one group mapping key."""
	errors: list[str] = []

	if not isinstance(group_mapping_name, str) or not name_pattern.fullmatch(group_mapping_name):
		errors.append(f"{item_label}: group mapping key does not match '{name_regex}'.")
		return errors

	if required_prefix and not group_mapping_name.startswith(required_prefix):
		errors.append(f"{item_label}: group mapping key must start with '{required_prefix}'.")

	return errors


def validate_group_mapping_delete(
	data: Any,
	target_dir: Path,
	properties: dict[str, str],
	name_pattern: re.Pattern[str],
	name_regex: str,
	required_prefix: str,
) -> list[str]:
	"""Validate DELETE group-mapping payload shape."""
	errors: list[str] = []

	if not isinstance(data, list):
		return ["group-mapping.json: DELETE payload must be a non-empty JSON array of group mapping keys."]

	if not data:
		return ["group-mapping.json: DELETE payload must contain at least one group mapping key."]

	for group_mapping_name in data:
		errors.extend(
			validate_group_mapping_name(
				group_mapping_name,
				f"group-mapping.json DELETE key '{group_mapping_name}'",
				name_pattern,
				name_regex,
				required_prefix,
			)
		)

	if not errors:
		generated_file = target_dir / properties.get("GENERATED_GROUP_MAPPING_FILE", "files/elc-group-mappings.json")
		errors.extend(validate_delete_keys(data, load_existing_json(generated_file), "group-mapping.json"))

	return errors


def validate_group_mapping(data: Any, mode: str, target_dir: Path, properties: dict[str, str]) -> list[str]:
	"""Validate group-mapping.json at a basic structural level."""
	_ = target_dir
	name_regex = properties.get("GROUP_MAPPING_NAME_REGEX", "^[A-Za-z][A-Za-z0-9_-]{2,127}$")
	required_prefix = properties.get("GROUP_MAPPING_NAME_PREFIX", "").strip()

	try:
		name_pattern = re.compile(name_regex)
	except re.error as error:
		return [f"Property 'GROUP_MAPPING_NAME_REGEX' is invalid: {error}."]

	if mode == "DELETE":
		return validate_group_mapping_delete(data, target_dir, properties, name_pattern, name_regex, required_prefix)

	if not isinstance(data, dict) or not data:
		return ["group-mapping.json: UPSERT payload must be a non-empty JSON object keyed by group mapping name."]

	errors: list[str] = []

	for group_mapping_name, group_mapping in data.items():
		item_label = f"group-mapping.json[{group_mapping_name}]"
		errors.extend(validate_group_mapping_name(group_mapping_name, item_label, name_pattern, name_regex, required_prefix))

		if not isinstance(group_mapping, dict):
			errors.append(f"{item_label}: UPSERT value must be an object.")
			continue

		display_name = group_mapping.get("display_name")
		if isinstance(display_name, str) and display_name.strip() and display_name.strip() != group_mapping_name:
			errors.append(f"{item_label}: display_name must match the group mapping key '{group_mapping_name}'.")

		for required_field in ("display_name", "filter"):
			if not isinstance(group_mapping.get(required_field), str) or not group_mapping.get(required_field, "").strip():
				errors.append(f"{item_label}: {required_field} is mandatory.")

		description = group_mapping.get("description")
		if description is not None and not isinstance(description, str):
			errors.append(f"{item_label}: description must be a string when provided.")

	return errors