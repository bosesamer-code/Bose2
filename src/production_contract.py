"""Validate the safe handoff contract entering the public factory."""

from __future__ import annotations

from typing import Any


REQUIRED_FIELDS = {
    "contract_version",
    "task_id",
    "production_status",
    "permissions",
    "inputs",
    "scene_plan",
    "validation_requirements",
}

FORBIDDEN_KEYS = {
    "api_key",
    "apikey",
    "token",
    "access_token",
    "password",
    "secret",
    "private_key",
    "credentials",
    "customer_data",
}


def _contains_forbidden(value: Any) -> bool:
    if isinstance(value, dict):
        for key, nested in value.items():
            normalized = str(key).lower().replace("-", "_")
            if normalized in FORBIDDEN_KEYS or any(
                marker in normalized for marker in ("api_key", "access_token", "password", "private_key")
            ):
                return True
            if _contains_forbidden(nested):
                return True
    elif isinstance(value, list):
        return any(_contains_forbidden(item) for item in value)
    return False


def validate_contract(contract: dict[str, Any]) -> tuple[bool, list[str]]:
    errors: list[str] = []

    missing = sorted(REQUIRED_FIELDS - set(contract))
    if missing:
        errors.append(f"missing_fields:{','.join(missing)}")

    if contract.get("contract_version") != 1:
        errors.append("unsupported_contract_version")

    if contract.get("production_status") != "ready_for_public_factory":
        errors.append("invalid_production_status")

    permissions = contract.get("permissions", {})
    if permissions.get("publish") is not False:
        errors.append("publish_must_be_false")
    if permissions.get("access_private_core") is not False:
        errors.append("private_core_access_must_be_false")

    inputs = contract.get("inputs", {})
    if not isinstance(inputs, dict):
        errors.append("inputs_must_be_object")
    elif not str(inputs.get("script", "")).strip():
        errors.append("script_is_required")

    if not isinstance(contract.get("scene_plan"), list):
        errors.append("scene_plan_must_be_list")
    if not isinstance(contract.get("validation_requirements"), list):
        errors.append("validation_requirements_must_be_list")

    if _contains_forbidden(contract):
        errors.append("forbidden_secret_or_private_data")

    return not errors, errors
