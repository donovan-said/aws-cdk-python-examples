"""
A collection of tests to ensure that the EventBridge rules match the events
published bby ACM.

Event retrieved from:
https://docs.aws.amazon.com/acm/latest/userguide/supported-events.html
"""

import json

from pathlib import Path
from moto.events.models import EventPattern

CONTEXT_PATH = Path(__file__).parent / "context"


def context(path):
    with open(f"{CONTEXT_PATH}/{path}") as file:
        context_file = json.load(file)

    return context_file


def test_event_pattern_approaching_expiration():
    """
    Test to ensure that the "ACM Certificate Approaching Expiration" event
    pattern used in the EventBridge rule matches the published ACM event.
    """

    event_pattern = context("acm_event_pattern_approaching_expiration.json")
    event = context("acm_event_approaching_expiration.json")
    negative = context("acm_event_negative.json")

    pattern = EventPattern.load(json.dumps(event_pattern))
    assert pattern.matches_event(event)
    assert not pattern.matches_event(negative)


def test_event_pattern_expired():
    """
    Test to ensure that the "ACM Certificate Expired" event pattern used in the
    EventBridge rule matches the published ACM event.
    """

    event_pattern = context("acm_event_pattern_expired.json")
    event = context("acm_event_expired.json")
    negative = context("acm_event_negative.json")

    pattern = EventPattern.load(json.dumps(event_pattern))
    assert pattern.matches_event(event)
    assert not pattern.matches_event(negative)


def test_event_pattern_action_required():
    """
    Test to ensure that the "ACM Certificate Renewal Action Required" event
    pattern used in the EventBridge rule matches the published ACM event.
    """

    event_pattern = context("acm_event_pattern_action_required.json")
    event = context("acm_event_action_required.json")
    negative = context("acm_event_negative.json")

    pattern = EventPattern.load(json.dumps(event_pattern))
    assert pattern.matches_event(event)
    assert not pattern.matches_event(negative)
