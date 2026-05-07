#!/usr/bin/env python3
"""Lightweight structural validator for Regis policy gate specifications."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
POLICY_DIR = ROOT / "policy" / "regis"
REQUIRED_TOP_LEVEL = {"id", "version", "purpose", "inputs", "outcomes", "rules"}
REQUIRED_RULE_FIELDS = {"id", "description", "when", "outcome"}


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = yaml.safe_load(handle)
    if not isinstance(value, dict):
        raise AssertionError(f"{path} did not parse to a mapping")
    return value


def validate_policy(path: Path) -> None:
    policy = load_yaml(path)
    missing = REQUIRED_TOP_LEVEL - set(policy)
    if missing:
        raise AssertionError(f"{path} missing top-level fields: {sorted(missing)}")

    if not isinstance(policy["inputs"], list) or not policy["inputs"]:
        raise AssertionError(f"{path} inputs must be a non-empty list")
    if not isinstance(policy["outcomes"], list) or not policy["outcomes"]:
        raise AssertionError(f"{path} outcomes must be a non-empty list")
    if not isinstance(policy["rules"], list) or not policy["rules"]:
        raise AssertionError(f"{path} rules must be a non-empty list")

    declared_outcomes = set(policy["outcomes"])
    for index, rule in enumerate(policy["rules"]):
        if not isinstance(rule, dict):
            raise AssertionError(f"{path} rule {index} is not a mapping")
        missing_rule = REQUIRED_RULE_FIELDS - set(rule)
        if missing_rule:
            raise AssertionError(f"{path} rule {index} missing fields: {sorted(missing_rule)}")
        if rule["outcome"] not in declared_outcomes:
            raise AssertionError(
                f"{path} rule {rule['id']} outcome {rule['outcome']} not declared in outcomes"
            )


def main() -> int:
    if not POLICY_DIR.exists():
        raise SystemExit(f"Missing policy directory: {POLICY_DIR}")
    policies = sorted(POLICY_DIR.glob("*.yaml"))
    if not policies:
        raise SystemExit(f"No Regis policy files found in {POLICY_DIR}")
    for policy in policies:
        validate_policy(policy)
        print(f"validated {policy.relative_to(ROOT)}")
    print("Regis policy validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
