#!/usr/bin/env python3
"""Generic CSV request validator for Confluent Cloud onboarding."""

from __future__ import annotations

import argparse
import csv
import logging
import sys
from pathlib import Path

from topic.topic_validator import validate_topic_row


SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_DIR = SCRIPT_DIR / "config"

TYPE_CONFIG_FILES = {
    "topic": {
        "nonprod": CONFIG_DIR / "topic_nonprod_config.properties",
        "prod": CONFIG_DIR / "topic_prod_config.properties",
    },
    "rbac": {},
    "service_account": {},
    "identity_pool": {},
}

BASE_REQUIRED_COLUMNS = {"type", "platform_environment", "action"}


# Configure script logging so every validation step prints readable messages.
def setup_logging() -> None:
    """Set the log format used by this script.

    Example log line:
    2026-07-31 13:30:00 | INFO | Starting CSV validation: request.csv
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


# Read a Java-style .properties file into a Python dictionary.
def load_properties(property_file: Path) -> dict[str, str]:
    """Load key=value settings from a property file.

    Input example:
    TOPIC_REQUIRED_COLUMNS=type,action,environment,cluster

    Output example:
    {"TOPIC_REQUIRED_COLUMNS": "type,action,environment,cluster"}
    """
    properties: dict[str, str] = {}

    if not property_file.exists():
        raise FileNotFoundError(f"Property file not found: {property_file}")

    with property_file.open("r", encoding="utf-8") as file_handle:
        for line_number, raw_line in enumerate(file_handle, start=1):
            line = raw_line.strip()

            if not line or line.startswith("#"):
                continue

            if "=" not in line:
                raise ValueError(
                    f"Invalid property format in {property_file} at line {line_number}: {raw_line.rstrip()}"
                )

            key, value = line.split("=", 1)
            properties[key.strip()] = value.strip()

    return properties


# Standardize one CSV row so column names and values are easier to validate.
def normalize_row(row: dict[str, str | None]) -> dict[str, str]:
    """Trim values and make CSV column names lowercase.

    Input example:
    {" Type ": " Topic ", "ACTION": " create "}

    Output example:
    {"type": "Topic", "action": "create"}
    """
    return {
        (key or "").strip().lower(): (value or "").strip()
        for key, value in row.items()
    }


# Convert a comma-separated property value into a lowercase set for validation.
def parse_csv_property(value: str) -> set[str]:
    """Parse comma-separated property values.

    Input example:
    "type,action,environment,cluster"

    Output example:
    {"type", "action", "environment", "cluster"}
    """
    return {item.strip().lower() for item in value.split(",") if item.strip()}


# Validate only the generic columns needed before type-specific routing can happen.
def validate_csv_headers(headers: list[str] | None) -> list[str]:
    """Check that the CSV has the base columns required for all request types.

    Input example:
    ["type", "action", "environment", "cluster"]

    Output example:
    [] means no errors. A non-empty list contains validation error messages.
    """
    if not headers:
        return ["CSV file is empty or missing a header row."]

    normalized_headers = {header.strip().lower() for header in headers}
    missing_columns = sorted(BASE_REQUIRED_COLUMNS - normalized_headers)

    if missing_columns:
        return [f"CSV is missing mandatory base column(s): {', '.join(missing_columns)}"]

    return []


# Read the request type from a row and confirm this script knows how to route it.
def get_request_type(row: dict[str, str], row_number: int) -> str:
    """Return the normalized request type from one CSV row.

    Input example:
    row={"type": "topic", "action": "create"}, row_number=2

    Output example:
    "topic"
    """
    request_type = row.get("type", "").lower()

    if not request_type:
        raise ValueError(f"Row {row_number}: type is mandatory.")

    if request_type not in TYPE_CONFIG_FILES:
        valid_types = ", ".join(sorted(TYPE_CONFIG_FILES))
        raise ValueError(f"Row {row_number}: unsupported type '{request_type}'. Valid types: {valid_types}")

    return request_type


# Read the platform environment from a row so the script can choose nonprod or prod properties.
def get_platform_environment(row: dict[str, str], row_number: int) -> str:
    """Return the normalized platform environment from one CSV row.

    Input example:
    row={"type": "topic", "platform_environment": "nonprod"}, row_number=2

    Output example:
    "nonprod"
    """
    platform_environment = row.get("platform_environment", "").lower()

    if not platform_environment:
        raise ValueError(f"Row {row_number}: platform_environment is mandatory.")

    return platform_environment


# Confirm that one CSV file contains only one request type.
def validate_single_request_type(rows: list[tuple[int, dict[str, str]]]) -> tuple[str | None, list[str]]:
    """Validate that all CSV rows have the same type value.

    Input example:
    [(2, {"type": "topic"}), (3, {"type": "topic"})]

    Output example:
    ("topic", []) means all rows are topic rows.

    Error example:
    ("topic", ["CSV contains mixed request types. Expected all rows to be 'topic', but row 3 has 'rbac'."])
    """
    if not rows:
        return None, ["CSV file has a header row but no data rows."]

    errors: list[str] = []

    try:
        expected_type = get_request_type(rows[0][1], rows[0][0])
    except ValueError as error:
        return None, [str(error)]

    for row_number, row in rows[1:]:
        try:
            request_type = get_request_type(row, row_number)
        except ValueError as error:
            errors.append(str(error))
            continue

        if request_type != expected_type:
            errors.append(
                f"CSV contains mixed request types. Expected all rows to be '{expected_type}', "
                f"but row {row_number} has '{request_type}'."
            )

    return expected_type, errors


# Confirm that one CSV file contains only one platform environment.
def validate_single_platform_environment(rows: list[tuple[int, dict[str, str]]]) -> tuple[str | None, list[str]]:
    """Validate that all CSV rows have the same platform_environment value.

    Input example:
    [(2, {"platform_environment": "nonprod"}), (3, {"platform_environment": "nonprod"})]

    Output example:
    ("nonprod", []) means all rows are nonprod rows.
    """
    if not rows:
        return None, ["CSV file has a header row but no data rows."]

    errors: list[str] = []

    try:
        expected_platform_environment = get_platform_environment(rows[0][1], rows[0][0])
    except ValueError as error:
        return None, [str(error)]

    for row_number, row in rows[1:]:
        try:
            platform_environment = get_platform_environment(row, row_number)
        except ValueError as error:
            errors.append(str(error))
            continue

        if platform_environment != expected_platform_environment:
            errors.append(
                "CSV contains mixed platform environments. "
                f"Expected all rows to be '{expected_platform_environment}', "
                f"but row {row_number} has '{platform_environment}'."
            )

    return expected_platform_environment, errors


# Choose the correct property file using request type and platform environment.
def resolve_property_file(request_type: str, platform_environment: str) -> Path:
    """Return the property file path for a request type and platform environment.

    Input example:
    request_type="topic", platform_environment="nonprod"

    Output example:
    config/topic_nonprod_config.properties
    """
    platform_config_files = TYPE_CONFIG_FILES.get(request_type, {})
    property_file = platform_config_files.get(platform_environment)

    if property_file:
        return property_file

    valid_platform_environments = ", ".join(sorted(platform_config_files)) or "none configured"
    raise ValueError(
        f"No property file configured for type '{request_type}' and platform_environment "
        f"'{platform_environment}'. Valid platform environments for this type: {valid_platform_environments}."
    )


# Validate the row has all columns required by the matching type property file.
def validate_type_columns(
    row: dict[str, str], request_type: str, properties: dict[str, str], row_number: int
) -> list[str]:
    """Validate columns for a specific type using its property file.

    For type=topic, this reads TOPIC_REQUIRED_COLUMNS from topic_config.properties.

    Input example:
    request_type="topic"
    properties={"TOPIC_REQUIRED_COLUMNS": "type,action,environment,cluster"}
    row={"type": "topic", "action": "create", "environment": "elc-nonprod-eastus2"}

    Output example:
    ["Row 2: type 'topic' is missing required column(s): cluster"]
    """
    required_columns_property = f"{request_type.upper()}_REQUIRED_COLUMNS"
    required_columns = parse_csv_property(properties.get(required_columns_property, ""))

    if not required_columns:
        return [
            f"Row {row_number}: property '{required_columns_property}' is missing or empty for type '{request_type}'."
        ]

    missing_columns = sorted(column for column in required_columns if column not in row)

    if missing_columns:
        return [
            f"Row {row_number}: type '{request_type}' is missing required column(s): {', '.join(missing_columns)}"
        ]

    return []


# Validate the action column using VALID_ACTIONS from the selected property file.
def validate_action(row: dict[str, str], properties: dict[str, str], row_number: int) -> list[str]:
    """Validate that action is allowed by the property file.

    Input example:
    row={"action": "create"}
    properties={"VALID_ACTIONS": "create,update,delete"}

    Output example:
    [] means action is valid.

    Error example:
    ["Row 2: invalid action 'remove'. Valid actions: create, delete, update"]
    """
    valid_actions = parse_csv_property(properties.get("VALID_ACTIONS", ""))

    if not valid_actions:
        return ["Property 'VALID_ACTIONS' is missing or empty."]

    action = row.get("action", "").lower()

    if not action:
        return [f"Row {row_number}: action is mandatory."]

    if action not in valid_actions:
        return [
            f"Row {row_number}: invalid action '{action}'. Valid actions: {', '.join(sorted(valid_actions))}"
        ]

    return []


# Validate environment and cluster together using VALID_ENVIRONMENT_CLUSTERS from the selected property file.
def validate_environment_cluster(row: dict[str, str], properties: dict[str, str], row_number: int) -> list[str]:
    """Validate that the environment and cluster combination is allowed.

    Input example:
    row={"environment": "elc-sandbox", "cluster": "elc-sandbox-core-enterprise"}
    properties={"VALID_ENVIRONMENT_CLUSTERS": "elc-sandbox|elc-sandbox-core-enterprise"}

    Output example:
    [] means the environment and cluster pair is valid.

    Error example:
    ["Row 3: invalid environment-cluster combination 'elc-sandbx|elc-sandbox-core-enterprise'."]
    """
    valid_combinations = parse_csv_property(properties.get("VALID_ENVIRONMENT_CLUSTERS", ""))

    if not valid_combinations:
        return ["Property 'VALID_ENVIRONMENT_CLUSTERS' is missing or empty."]

    environment = row.get("environment", "").lower()
    cluster = row.get("cluster", "").lower()

    if not environment:
        return [f"Row {row_number}: environment is mandatory."]

    if not cluster:
        return [f"Row {row_number}: cluster is mandatory."]

    environment_cluster = f"{environment}|{cluster}"

    if environment_cluster not in valid_combinations:
        return [
            f"Row {row_number}: invalid environment-cluster combination '{environment_cluster}'. "
            f"Valid combinations: {', '.join(sorted(valid_combinations))}"
        ]

    return []


# Validate one CSV row using the already loaded property file for its type.
def validate_row(
    row: dict[str, str], request_type: str, properties: dict[str, str], row_number: int
) -> list[str]:
    """Validate one CSV row and return all row-level errors.

    Input example:
    {"type": "topic", "action": "create", "environment": "elc-nonprod-eastus2"}

    Processing example:
    request_type=topic uses topic_config.properties, then validates TOPIC_REQUIRED_COLUMNS.
    """
    errors = validate_type_columns(row, request_type, properties, row_number)
    errors.extend(validate_action(row, properties, row_number))
    errors.extend(validate_environment_cluster(row, properties, row_number))

    if request_type == "topic":
        errors.extend(validate_topic_row(row, properties, row_number))

    return errors


# Validate the complete CSV file and return a process-friendly exit code.
def validate_csv(csv_file: Path) -> int:
    """Validate the CSV file from header to all data rows.

    Input example:
    Path("request.csv")

    Output example:
    0 means validation passed. 1 means validation failed.
    """
    logging.info("Starting CSV validation: %s", csv_file)

    if not csv_file.exists():
        logging.error("CSV file not found: %s", csv_file)
        return 1

    all_errors: list[str] = []

    with csv_file.open("r", encoding="utf-8-sig", newline="") as file_handle:
        reader = csv.DictReader(file_handle)
        header_errors = validate_csv_headers(reader.fieldnames)

        if header_errors:
            for error in header_errors:
                logging.error(error)
            return 1

        rows = [
            (row_number, normalize_row(raw_row))
            for row_number, raw_row in enumerate(reader, start=2)
        ]

        header_count = len(reader.fieldnames or [])
        row_count = len(rows)
        logging.info("CSV header count: %s", header_count)
        logging.info("CSV data row count: %s", row_count)

        request_type, type_errors = validate_single_request_type(rows)
        all_errors.extend(type_errors)

        platform_environment, platform_environment_errors = validate_single_platform_environment(rows)
        all_errors.extend(platform_environment_errors)

        if not all_errors and request_type and platform_environment:
            property_file = resolve_property_file(request_type, platform_environment)
            try:
                properties = load_properties(property_file)
                logging.info("Loaded %s properties from %s", request_type, property_file)
                logging.debug("Loaded property keys: %s", sorted(properties))

                required_columns_property = f"{request_type.upper()}_REQUIRED_COLUMNS"
                required_columns = parse_csv_property(properties.get(required_columns_property, ""))
                logging.info("CSV request type: %s", request_type)
                logging.info("CSV platform environment: %s", platform_environment)
                logging.info("Required column count for %s: %s", request_type, len(required_columns))

                for row_number, row in rows:
                    row_errors = validate_row(row, request_type, properties, row_number)
                    all_errors.extend(row_errors)
            except (FileNotFoundError, ValueError) as error:
                all_errors.append(str(error))

    if all_errors:
        logging.error("CSV validation failed with %s error(s).", len(all_errors))
        for error in all_errors:
            logging.error(error)
        return 1

    logging.info("CSV validation completed successfully. Headers: %s, rows: %s.", header_count, row_count)
    return 0


# Parse command-line arguments supplied by the user or pipeline.
def parse_args() -> argparse.Namespace:
    """Read script arguments from the command line.

    Command example:
    python main/scripts/validate_csv_request.py request.csv
    """
    parser = argparse.ArgumentParser(
        description="Validate a Confluent Cloud onboarding CSV request file."
    )
    parser.add_argument("csv_file", help="Path to the CSV request file.")
    return parser.parse_args()


# Script entry point used when this file is executed from PowerShell or a pipeline.
def main() -> int:
    """Run the validator and return the final exit code."""
    setup_logging()
    args = parse_args()
    return validate_csv(Path(args.csv_file))


if __name__ == "__main__":
    sys.exit(main())
