#!/usr/bin/env python3
"""Identity pool JSON request validation."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any


def validate_identity_pool_name(
	pool_name: Any,
	item_label: str,
	name_pattern: re.Pattern[str],
	name_regex: str,
	required_prefix: str,
) -> list[str]:
	"""Validate one identity pool name."""
	errors: list[str] = []

	if not isinstance(pool_name, str) or not name_pattern.fullmatch(pool_name):
		errors.append(f"{item_label}: identity pool name does not match '{name_regex}'.")
		return errors

	if required_prefix and not pool_name.startswith(required_prefix):
		errors.append(f"{item_label}: identity pool name must start with '{required_prefix}'.")

	return errors


def validate_identity_pool_delete(
	data: Any,
	name_pattern: re.Pattern[str],
	name_regex: str,
	required_prefix: str,
) -> list[str]:
	"""Validate DELETE identity-pool payload shape."""
	errors: list[str] = []

	if not isinstance(data, list):
		return ["identity-pool.json: DELETE payload must be a non-empty JSON array of identity pool names."]

	if not data:
		return ["identity-pool.json: DELETE payload must contain at least one identity pool name."]

	for pool_name in data:
		errors.extend(
			validate_identity_pool_name(
				pool_name,
				f"identity-pool.json DELETE key '{pool_name}'",
				name_pattern,
				name_regex,
				required_prefix,
			)
		)

	return errors


def validate_identity_pool(data: Any, mode: str, target_dir: Path, properties: dict[str, str]) -> list[str]:
	"""Validate identity-pool.json at a basic structural level."""
	_ = target_dir
	name_regex = properties.get("IDENTITY_POOL_NAME_REGEX", "^[A-Za-z][A-Za-z0-9_-]{2,127}$")
	required_prefix = properties.get("IDENTITY_POOL_NAME_PREFIX", "").strip()

	try:
		name_pattern = re.compile(name_regex)
	except re.error as error:
		return [f"Property 'IDENTITY_POOL_NAME_REGEX' is invalid: {error}."]

	if mode == "DELETE":
		return validate_identity_pool_delete(data, name_pattern, name_regex, required_prefix)

	if not isinstance(data, dict) or not data:
		return ["identity-pool.json: UPSERT payload must be a non-empty JSON object keyed by identity pool name."]

	errors: list[str] = []

	for pool_name, pool in data.items():
		item_label = f"identity-pool.json[{pool_name}]"
		errors.extend(validate_identity_pool_name(pool_name, item_label, name_pattern, name_regex, required_prefix))

		if not isinstance(pool, dict):
			errors.append(f"{item_label}: UPSERT value must be an object.")

	return errors