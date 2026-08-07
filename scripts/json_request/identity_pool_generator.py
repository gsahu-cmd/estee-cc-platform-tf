#!/usr/bin/env python3
"""Generate Terraform JSON files from identity-pool.json requests."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from json_request.common import load_existing_json, write_json_file


def identity_pool_stack_dir(repo_root: Path, platform_environment: str) -> Path:
	"""Return the identity-pool Terraform stack directory for the platform environment."""
	return repo_root / "main" / "org" / "identity-pool" / platform_environment


def identity_pool_file_path(target_dir: Path, properties: dict[str, str]) -> Path:
	"""Resolve the generated identity-pool file path."""
	return target_dir / properties.get("GENERATED_IDENTITY_POOL_FILE", "files/elc-identity-pools.json")


def upsert_identity_pools(request_data: dict[str, Any], target_dir: Path, properties: dict[str, str]) -> list[Path]:
	"""Apply UPSERT identity-pool requests to generated Terraform JSON."""
	identity_pool_file = identity_pool_file_path(target_dir, properties)
	identity_pools = load_existing_json(identity_pool_file)

	for pool_name, pool in request_data.items():
		if not isinstance(pool, dict):
			continue

		identity_pools[pool_name] = {
			"description": pool.get("description"),
			"display_name": pool.get("display_name"),
			"filter": pool.get("filter"),
			"identity_claim": pool.get("identity_claim"),
		}

	write_json_file(identity_pool_file, identity_pools)
	return [identity_pool_file]


def delete_identity_pools(request_data: list[Any], target_dir: Path, properties: dict[str, str]) -> list[Path]:
	"""Apply DELETE identity-pool requests to generated Terraform JSON."""
	identity_pool_file = identity_pool_file_path(target_dir, properties)
	identity_pools = load_existing_json(identity_pool_file)

	for pool_name in request_data:
		if isinstance(pool_name, str):
			identity_pools.pop(pool_name, None)

	write_json_file(identity_pool_file, identity_pools)
	return [identity_pool_file]


def update_identity_pool_generated_files(
	request_data: Any,
	mode: str,
	target_dir: Path,
	properties: dict[str, str],
) -> list[Path]:
	"""Update generated Terraform JSON files for identity-pool.json."""
	if mode == "DELETE":
		if not isinstance(request_data, list):
			raise ValueError("identity-pool.json DELETE generation requires a JSON array.")
		return delete_identity_pools(request_data, target_dir, properties)

	if not isinstance(request_data, dict):
		raise ValueError("identity-pool.json UPSERT generation requires a JSON object.")

	return upsert_identity_pools(request_data, target_dir, properties)