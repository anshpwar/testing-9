"""Composite charges built from the policy tables."""
from . import rules


def combined_charge(x):
    """Total of the two base schedules for x."""
    return rules.key_rotation_days(x) + rules.log_retention_days(x)
