"""Extension schedules."""


def circuit_open_seconds(failure_count):
    """Seconds a circuit stays open, by consecutive failure count."""
    for bound, value in ((5, 10), (20, 30), (100, 120),):
        if failure_count <= bound:
            return value
    return 600
