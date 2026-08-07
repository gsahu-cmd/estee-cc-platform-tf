#!/usr/bin/env python3
"""Topic JSON request validation."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from json_request.common import load_existing_json, parse_int_property, parse_list_property, validate_delete_keys


def validate_topic_name(topic_name: str, properties: dict[str, str], item_label: str) -> list[str]:
	"""Validate topic name using the configured naming convention."""
	errors: list[str] = []
	name_regex = properties.get("TOPIC_NAME_REGEX", "").strip()
	separator = properties.get("TOPIC_NAME_SEPARATOR", "_")
	expected_prefix = properties.get("TOPIC_NAME_PREFIX", "elc").strip().lower()
	topic_name = topic_name.strip().lower()

	if not topic_name:
		return [f"{item_label}: topic name must not be empty."]

	if not name_regex:
		return ["Property 'TOPIC_NAME_REGEX' is missing or empty."]

	try:
		pattern = re.compile(name_regex)
	except re.error as error:
		return [f"Property 'TOPIC_NAME_REGEX' is invalid: {error}."]

	if not pattern.fullmatch(topic_name):
		errors.append(f"{item_label}: topic name '{topic_name}' does not match '{name_regex}'.")

	tokens = [token.strip().lower() for token in topic_name.split(separator) if token.strip()]
	if len(tokens) < 8:
		errors.append(f"{item_label}: topic name '{topic_name}' does not have enough naming parts.")
		return errors

	if tokens[0] != expected_prefix:
		errors.append(f"{item_label}: topic name must start with '{expected_prefix}{separator}'.")

	valid_visibilities = {value.lower() for value in parse_list_property(properties, "VALID_VISIBILITIES")}
	valid_data_classes = {value.lower() for value in parse_list_property(properties, "VALID_DATA_CLASSES")}
	valid_events = {value.lower() for value in parse_list_property(properties, "VALID_EVENTS")}
	valid_processing_stages = {value.lower() for value in parse_list_property(properties, "VALID_PROCESSING_STAGES")}
	valid_data_formats = {value.lower() for value in parse_list_property(properties, "VALID_DATA_FORMATS")}
	free_text_part_regex = properties.get("TOPIC_FREE_TEXT_PART_REGEX", r"^[a-z0-9][a-z0-9-]*$").strip()

	version = tokens[-1]

	if not re.fullmatch(r"v[0-9]+", version):
		errors.append(f"{item_label}: version '{version}' must be v followed by a number.")

	visibility_index = next((index for index in range(2, len(tokens) - 5) if tokens[index] in valid_visibilities), None)
	if visibility_index is None:
		errors.append(f"{item_label}: topic name must contain a valid visibility after org/source.")
		return errors

	for data_class in tokens[2:visibility_index]:
		if data_class not in valid_data_classes:
			errors.append(f"{item_label}: data class '{data_class}' is not valid.")

	remaining_parts = tokens[visibility_index + 1 : -1]
	if len(remaining_parts) < 4:
		errors.append(f"{item_label}: topic name must include object, event, processing stage, and data format before version.")
		return errors

	event = remaining_parts[1]
	processing_stage = remaining_parts[2]
	data_format = remaining_parts[3]
	optional_free_text_parts = remaining_parts[4:]

	if event not in valid_events:
		errors.append(f"{item_label}: event '{event}' is not valid.")

	if processing_stage not in valid_processing_stages:
		errors.append(f"{item_label}: processing stage '{processing_stage}' is not valid.")

	if data_format not in valid_data_formats:
		errors.append(f"{item_label}: data format '{data_format}' is not valid.")

	try:
		free_text_pattern = re.compile(free_text_part_regex)
	except re.error as error:
		errors.append(f"Property 'TOPIC_FREE_TEXT_PART_REGEX' is invalid: {error}.")
		return errors

	for free_text_part in optional_free_text_parts:
		if not free_text_pattern.fullmatch(free_text_part):
			errors.append(f"{item_label}: optional free text part '{free_text_part}' does not match '{free_text_part_regex}'.")

	return errors


def validate_topic_upsert(data: Any, properties: dict[str, str]) -> list[str]:
	"""Validate UPSERT topic payload."""
	errors: list[str] = []

	if not isinstance(data, dict) or not data:
		return ["topics.json: UPSERT payload must be a non-empty JSON object keyed by topic name."]

	max_partitions = parse_int_property(properties, "MAX_PARTITIONS", errors)
	max_retention_ms = parse_int_property(properties, "MAX_RETENTION_MS", errors)

	for topic_name, topic in data.items():
		item_label = f"topics.json[{topic_name}]"
		errors.extend(validate_topic_name(str(topic_name), properties, item_label))

		if not isinstance(topic, dict):
			errors.append(f"{item_label}: value must be an object.")
			continue

		partitions_count = topic.get("partitions_count")
		if not isinstance(partitions_count, int):
			errors.append(f"{item_label}: partitions_count must be a number.")
		elif partitions_count < 1:
			errors.append(f"{item_label}: partitions_count must be greater than 0.")
		elif max_partitions is not None and partitions_count > max_partitions:
			errors.append(f"{item_label}: partitions_count '{partitions_count}' exceeds '{max_partitions}'.")

		config = topic.get("config")
		if not isinstance(config, dict):
			errors.append(f"{item_label}: config must be an object.")
		else:
			for config_key, config_value in config.items():
				if not isinstance(config_key, str) or not config_key.strip():
					errors.append(f"{item_label}: config keys must be non-empty strings.")
				if not isinstance(config_value, str) or not config_value.strip():
					errors.append(f"{item_label}: config value for '{config_key}' must be a non-empty string.")

			retention_value = config.get("retention.ms")
			if retention_value is not None:
				try:
					retention_ms = int(str(retention_value))
				except ValueError:
					errors.append(f"{item_label}: retention.ms must be numeric.")
				else:
					if retention_ms < 1:
						errors.append(f"{item_label}: retention.ms must be greater than 0.")
					elif max_retention_ms is not None and retention_ms > max_retention_ms:
						errors.append(f"{item_label}: retention.ms '{retention_ms}' exceeds '{max_retention_ms}'.")

		tags = topic.get("tags", [])
		if tags is None:
			tags = []
		if not isinstance(tags, list) or not all(isinstance(tag, str) and tag.strip() for tag in tags):
			errors.append(f"{item_label}: tags must be a list of non-empty strings or null.")

		for attribute_name in ("owner", "ownerEmail", "description"):
			attribute_value = topic.get(attribute_name, "")
			if attribute_value is not None and not isinstance(attribute_value, str):
				errors.append(f"{item_label}: {attribute_name} must be a string or null.")

	return errors


def validate_topics(data: Any, mode: str, target_dir: Path, properties: dict[str, str]) -> list[str]:
	"""Validate topics.json for UPSERT or DELETE mode."""
	if mode == "DELETE":
		generated_file = target_dir / properties.get("GENERATED_TOPIC_FILE", "files/elc-topics.json")
		return validate_delete_keys(data, load_existing_json(generated_file), "topics.json")

	return validate_topic_upsert(data, properties)