#!/usr/bin/env python3
"""Generate Terraform JSON files from topics.json requests."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from json_request.common import load_existing_json, write_json_file


TOPIC_ATTRIBUTE_FIELDS = ("owner", "ownerEmail", "description")


def topic_file_path(target_dir: Path, properties: dict[str, str], property_name: str, default_path: str) -> Path:
	"""Resolve a generated topic file path under the selected Terraform stack."""
	return target_dir / properties.get(property_name, default_path)


def load_topic_tags(file_path: Path) -> list[dict[str, Any]]:
	"""Load the existing topic tag list from generated JSON."""
	if not file_path.exists():
		return []

	data = load_existing_json(file_path)
	topic_tags = data.get("topic_tags", [])

	if not isinstance(topic_tags, list):
		raise ValueError(f"Existing generated topic tags file must contain a topic_tags list: {file_path}")

	return [item for item in topic_tags if isinstance(item, dict)]


def topic_tags_to_map(topic_tags: list[dict[str, Any]]) -> dict[str, list[str]]:
	"""Convert generated topic_tags list into a map keyed by topic name."""
	tags_by_topic: dict[str, list[str]] = {}

	for item in topic_tags:
		name = item.get("name")
		tags = item.get("tags", [])

		if isinstance(name, str) and isinstance(tags, list):
			tags_by_topic[name] = [tag for tag in tags if isinstance(tag, str) and tag.strip()]

	return tags_by_topic


def topic_tags_to_list(tags_by_topic: dict[str, list[str]]) -> list[dict[str, Any]]:
	"""Convert topic tag map back into the Terraform JSON list shape."""
	return [
		{"name": topic_name, "tags": sorted(set(tags))}
		for topic_name, tags in sorted(tags_by_topic.items())
		if tags
	]


def attributes_from_topic(topic: dict[str, Any]) -> dict[str, str]:
	"""Extract non-empty catalog attributes from one topic request."""
	attributes: dict[str, str] = {}

	for field_name in TOPIC_ATTRIBUTE_FIELDS:
		value = topic.get(field_name)
		if isinstance(value, str) and value.strip():
			attributes[field_name] = value.strip()

	return attributes


def topic_mentions_attributes(topic: dict[str, Any]) -> bool:
	"""Return whether the request explicitly mentions catalog attributes."""
	return any(field_name in topic for field_name in TOPIC_ATTRIBUTE_FIELDS)


def apply_topic_attributes(topic_name: str, topic: dict[str, Any], attributes_by_topic: dict[str, Any]) -> None:
	"""Apply explicitly mentioned catalog attribute changes for one topic."""
	existing_attributes = attributes_by_topic.get(topic_name, {})
	if not isinstance(existing_attributes, dict):
		existing_attributes = {}

	updated_attributes = dict(existing_attributes)

	for field_name in TOPIC_ATTRIBUTE_FIELDS:
		if field_name not in topic:
			continue

		value = topic.get(field_name)
		if isinstance(value, str) and value.strip():
			updated_attributes[field_name] = value.strip()
		else:
			updated_attributes.pop(field_name, None)

	if updated_attributes:
		attributes_by_topic[topic_name] = updated_attributes
	else:
		attributes_by_topic.pop(topic_name, None)


def upsert_topics(request_data: dict[str, Any], target_dir: Path, properties: dict[str, str]) -> list[Path]:
	"""Apply UPSERT topic requests to generated Terraform JSON files."""
	topic_file = topic_file_path(target_dir, properties, "GENERATED_TOPIC_FILE", "files/elc-topics.json")
	tags_file = topic_file_path(target_dir, properties, "GENERATED_TOPIC_TAGS_FILE", "files/elc-topics-tags.json")
	attributes_file = topic_file_path(
		target_dir,
		properties,
		"GENERATED_TOPIC_ATTRIBUTES_FILE",
		"files/elc-topic-attributes.json",
	)

	topics = load_existing_json(topic_file)
	should_update_tags = any(isinstance(topic, dict) and "tags" in topic for topic in request_data.values())
	should_update_attributes = any(
		isinstance(topic, dict) and topic_mentions_attributes(topic)
		for topic in request_data.values()
	)
	tags_by_topic = topic_tags_to_map(load_topic_tags(tags_file)) if should_update_tags else {}
	attributes_by_topic = load_existing_json(attributes_file) if should_update_attributes else {}
	updated_files = [topic_file]

	for topic_name, topic in request_data.items():
		if not isinstance(topic, dict):
			continue

		topics[topic_name] = {
			"config": topic.get("config", {}),
			"partitions_count": topic.get("partitions_count"),
		}

		if should_update_tags and "tags" in topic:
			tags = topic.get("tags") or []
			if tags:
				tags_by_topic[topic_name] = [tag.strip() for tag in tags if isinstance(tag, str) and tag.strip()]
			else:
				tags_by_topic.pop(topic_name, None)

		if should_update_attributes and topic_mentions_attributes(topic):
			apply_topic_attributes(topic_name, topic, attributes_by_topic)

	write_json_file(topic_file, topics)
	if should_update_tags:
		write_json_file(tags_file, {"topic_tags": topic_tags_to_list(tags_by_topic)})
		updated_files.append(tags_file)
	if should_update_attributes:
		write_json_file(attributes_file, attributes_by_topic)
		updated_files.append(attributes_file)

	return updated_files


def delete_topics(request_data: list[Any], target_dir: Path, properties: dict[str, str]) -> list[Path]:
	"""Apply DELETE topic requests to generated Terraform JSON files."""
	topic_file = topic_file_path(target_dir, properties, "GENERATED_TOPIC_FILE", "files/elc-topics.json")
	tags_file = topic_file_path(target_dir, properties, "GENERATED_TOPIC_TAGS_FILE", "files/elc-topics-tags.json")
	attributes_file = topic_file_path(
		target_dir,
		properties,
		"GENERATED_TOPIC_ATTRIBUTES_FILE",
		"files/elc-topic-attributes.json",
	)

	topics = load_existing_json(topic_file)
	tags_by_topic = topic_tags_to_map(load_topic_tags(tags_file)) if tags_file.exists() else {}
	attributes_by_topic = load_existing_json(attributes_file) if attributes_file.exists() else {}
	updated_files = [topic_file]

	for topic_name in request_data:
		if not isinstance(topic_name, str):
			continue

		topics.pop(topic_name, None)
		tags_by_topic.pop(topic_name, None)
		attributes_by_topic.pop(topic_name, None)

	write_json_file(topic_file, topics)
	if tags_file.exists():
		write_json_file(tags_file, {"topic_tags": topic_tags_to_list(tags_by_topic)})
		updated_files.append(tags_file)
	if attributes_file.exists():
		write_json_file(attributes_file, attributes_by_topic)
		updated_files.append(attributes_file)

	return updated_files


def update_topic_generated_files(
	request_data: Any,
	mode: str,
	target_dir: Path,
	properties: dict[str, str],
) -> list[Path]:
	"""Update generated Terraform JSON files for topics.json."""
	if mode == "DELETE":
		if not isinstance(request_data, list):
			raise ValueError("topics.json DELETE generation requires a JSON array.")
		return delete_topics(request_data, target_dir, properties)

	if not isinstance(request_data, dict):
		raise ValueError("topics.json UPSERT generation requires a JSON object.")

	return upsert_topics(request_data, target_dir, properties)