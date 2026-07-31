#!/usr/bin/env python3
"""Topic-specific CSV validation rules."""

from __future__ import annotations

import re


def parse_int_property(properties: dict[str, str], property_name: str) -> tuple[int | None, list[str]]:
    """Read a numeric property value.

    Input example:
    properties={"MAX_PARTITIONS": "20"}, property_name="MAX_PARTITIONS"

    Output example:
    (20, []) means the property is present and valid.
    """
    raw_value = properties.get(property_name, "").strip()

    if not raw_value:
        return None, [f"Property '{property_name}' is missing or empty."]

    try:
        return int(raw_value), []
    except ValueError:
        return None, [f"Property '{property_name}' must be a number. Current value: '{raw_value}'."]


def parse_list_property(properties: dict[str, str], property_name: str) -> tuple[set[str], list[str]]:
    """Read a comma-separated property value into a lowercase set.

    Input example:
    properties={"VALID_EVENTS": "delta,snapshot"}, property_name="VALID_EVENTS"

    Output example:
    ({"delta", "snapshot"}, []) means the property is present and valid.
    """
    raw_value = properties.get(property_name, "").strip()

    if not raw_value:
        return set(), [f"Property '{property_name}' is missing or empty."]

    values = {item.strip().lower() for item in raw_value.split(",") if item.strip()}

    if not values:
        return set(), [f"Property '{property_name}' is missing or empty."]

    return values, []


def parse_topic_config(row: dict[str, str], properties: dict[str, str], row_number: int) -> tuple[dict[str, str], list[str]]:
    """Parse the topic config CSV column into key/value pairs.

    Input example:
    cleanup.policy=delete|retention.ms=86400000

    Output example:
    ({"cleanup.policy": "delete", "retention.ms": "86400000"}, [])
    """
    config_value = row.get("config", "").strip()
    pair_separator = properties.get("TOPIC_CONFIG_PAIR_SEPARATOR", "|")
    key_value_separator = properties.get("TOPIC_CONFIG_KEY_VALUE_SEPARATOR", "=")
    config: dict[str, str] = {}
    errors: list[str] = []

    if not config_value:
        return config, errors

    for pair in config_value.split(pair_separator):
        pair = pair.strip()

        if not pair:
            continue

        if key_value_separator not in pair:
            errors.append(
                f"Row {row_number}: invalid config entry '{pair}'. Expected format is key{key_value_separator}value."
            )
            continue

        key, value = pair.split(key_value_separator, 1)
        key = key.strip()
        value = value.strip()

        if not key:
            errors.append(f"Row {row_number}: config entry '{pair}' has an empty key.")
            continue

        if not value:
            errors.append(f"Row {row_number}: config entry '{pair}' has an empty value.")
            continue

        config[key] = value

    return config, errors


def validate_partitions(row: dict[str, str], properties: dict[str, str], row_number: int) -> list[str]:
    """Validate topic partitions against MAX_PARTITIONS.

    Input example:
    row={"partitions": "6"}, properties={"MAX_PARTITIONS": "20"}

    Output example:
    [] means partitions is numeric and less than or equal to MAX_PARTITIONS.
    """
    max_partitions, property_errors = parse_int_property(properties, "MAX_PARTITIONS")

    if property_errors:
        return property_errors

    partitions_value = row.get("partitions", "").strip()

    if not partitions_value:
        return [f"Row {row_number}: partitions is mandatory."]

    try:
        partitions = int(partitions_value)
    except ValueError:
        return [f"Row {row_number}: partitions must be a number. Current value: '{partitions_value}'."]

    if partitions < 1:
        return [f"Row {row_number}: partitions must be greater than 0."]

    if max_partitions is not None and partitions > max_partitions:
        return [
            f"Row {row_number}: partitions '{partitions}' exceeds maximum allowed '{max_partitions}'."
        ]

    return []


def validate_retention_ms(row: dict[str, str], properties: dict[str, str], row_number: int) -> list[str]:
    """Validate retention.ms from the topic config column against MAX_RETENTION_MS.

    Input example:
    row={"config": "cleanup.policy=delete|retention.ms=86400000"}
    properties={"MAX_RETENTION_MS": "604800000"}

    Output example:
    [] means retention.ms is numeric and less than or equal to MAX_RETENTION_MS.
    """
    max_retention_ms, property_errors = parse_int_property(properties, "MAX_RETENTION_MS")

    if property_errors:
        return property_errors

    config, config_errors = parse_topic_config(row, properties, row_number)

    if config_errors:
        return config_errors

    retention_value = config.get("retention.ms", "").strip()

    if not retention_value:
        return []

    try:
        retention_ms = int(retention_value)
    except ValueError:
        return [f"Row {row_number}: retention.ms must be a number. Current value: '{retention_value}'."]

    if retention_ms < 1:
        return [f"Row {row_number}: retention.ms must be greater than 0."]

    if max_retention_ms is not None and retention_ms > max_retention_ms:
        return [
            f"Row {row_number}: retention.ms '{retention_ms}' exceeds maximum allowed '{max_retention_ms}'."
        ]

    return []


def validate_topic_name(row: dict[str, str], properties: dict[str, str], row_number: int) -> list[str]:
    """Validate the topic name column using TOPIC_NAME_REGEX and naming sheet rules.

    Input example:
    row={"name": "elc_sap_public_purchaseorder_transaction_raw_json_v1"}
    properties={"TOPIC_NAME_REGEX": "^elc_.*_v[0-9]+$"}

    Output example:
    [] means the topic name matches the configured regex and allowed segment values.
    """
    errors: list[str] = []
    topic_name_regex = properties.get("TOPIC_NAME_REGEX", "").strip()

    if not topic_name_regex:
        return ["Property 'TOPIC_NAME_REGEX' is missing or empty."]

    topic_name = row.get("name", "").strip().lower()

    if not topic_name:
        return [f"Row {row_number}: name is mandatory."]

    try:
        name_pattern = re.compile(topic_name_regex)
    except re.error as error:
        return [f"Property 'TOPIC_NAME_REGEX' is invalid: {error}."]

    if not name_pattern.fullmatch(topic_name):
        errors.append(
            f"Row {row_number}: topic name '{topic_name}' does not match required pattern '{topic_name_regex}'."
        )

    errors.extend(validate_topic_name_segments(topic_name, properties, row_number))

    return errors


def validate_topic_name_segments(topic_name: str, properties: dict[str, str], row_number: int) -> list[str]:
    """Validate parsed topic name fields from the naming convention sheet.

    Expected format:
    org_source_optionalDataClass_visibility_object_event_processingStage_optionalFreeText_dataFormat_v1

    Input example:
    elc_sap_restricted_public_payroll_transaction_raw_json_v1

    Parsed example:
    org=elc, source=sap, dataClass=restricted, visibility=public,
    object=payroll, event=transaction, processingStage=raw, dataFormat=json, version=v1
    """
    errors: list[str] = []
    separator = properties.get("TOPIC_NAME_SEPARATOR", "_")
    expected_prefix = properties.get("TOPIC_NAME_PREFIX", "elc").strip().lower()
    tokens = [token.strip().lower() for token in topic_name.split(separator) if token.strip()]

    if len(tokens) < 8:
        return [
            f"Row {row_number}: topic name '{topic_name}' does not have enough parts. "
            "Expected at least org, source, visibility, object, event, processingStage, dataFormat, version."
        ]

    if tokens[0] != expected_prefix:
        errors.append(f"Row {row_number}: topic name must start with '{expected_prefix}{separator}'.")

    version = tokens[-1]
    data_format = tokens[-2]

    if not re.fullmatch(r"v[0-9]+", version):
        errors.append(f"Row {row_number}: topic name version '{version}' must be v followed by a number.")

    valid_visibilities, visibility_property_errors = parse_list_property(properties, "VALID_VISIBILITIES")
    valid_data_classes, data_class_property_errors = parse_list_property(properties, "VALID_DATA_CLASSES")
    valid_events, event_property_errors = parse_list_property(properties, "VALID_EVENTS")
    valid_processing_stages, processing_stage_property_errors = parse_list_property(properties, "VALID_PROCESSING_STAGES")
    valid_data_formats, data_format_property_errors = parse_list_property(properties, "VALID_DATA_FORMATS")
    errors.extend(visibility_property_errors)
    errors.extend(data_class_property_errors)
    errors.extend(event_property_errors)
    errors.extend(processing_stage_property_errors)
    errors.extend(data_format_property_errors)

    if data_format not in valid_data_formats:
        errors.append(
            f"Row {row_number}: dataFormat '{data_format}' is invalid. "
            f"Valid data formats: {', '.join(sorted(valid_data_formats))}"
        )

    visibility_index = next(
        (index for index in range(2, len(tokens) - 5) if tokens[index] in valid_visibilities),
        None,
    )

    if visibility_index is None:
        errors.append(
            f"Row {row_number}: topic name must contain a valid visibility after org/source. "
            f"Valid visibilities: {', '.join(sorted(valid_visibilities))}"
        )
        return errors

    source = tokens[1]
    data_classes = tokens[2:visibility_index]
    visibility = tokens[visibility_index]
    remaining_parts = tokens[visibility_index + 1 : -2]

    if not source:
        errors.append(f"Row {row_number}: topic name source is mandatory.")

    for data_class in data_classes:
        if data_class not in valid_data_classes:
            errors.append(
                f"Row {row_number}: dataClass '{data_class}' is invalid. "
                f"Valid data classes: {', '.join(sorted(valid_data_classes))}"
            )

    if visibility not in valid_visibilities:
        errors.append(
            f"Row {row_number}: visibility '{visibility}' is invalid. "
            f"Valid visibilities: {', '.join(sorted(valid_visibilities))}"
        )

    if len(remaining_parts) < 3:
        errors.append(
            f"Row {row_number}: topic name must include object, event, and processingStage after visibility."
        )
        return errors

    object_name = remaining_parts[0]
    event = remaining_parts[1]
    processing_stage = remaining_parts[2]

    if not object_name:
        errors.append(f"Row {row_number}: topic name object is mandatory.")

    if event not in valid_events:
        errors.append(
            f"Row {row_number}: event '{event}' is invalid. Valid events: {', '.join(sorted(valid_events))}"
        )

    if processing_stage not in valid_processing_stages:
        errors.append(
            f"Row {row_number}: processingStage '{processing_stage}' is invalid. "
            f"Valid processing stages: {', '.join(sorted(valid_processing_stages))}"
        )

    return errors


def validate_topic_row(row: dict[str, str], properties: dict[str, str], row_number: int) -> list[str]:
    """Run all topic-specific validations for one CSV row.

    Current topic-specific validations:
    1. partitions must be numeric and <= MAX_PARTITIONS.
    2. retention.ms in config must be numeric and <= MAX_RETENTION_MS.
    """
    errors: list[str] = []
    errors.extend(validate_topic_name(row, properties, row_number))
    errors.extend(validate_partitions(row, properties, row_number))
    errors.extend(validate_retention_ms(row, properties, row_number))
    return errors
