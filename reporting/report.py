# WS2 — JSON report module.
"""Load, aggregate, and format event summaries as deterministic JSON.

Public API (consumed by WS3 integration tests):
- load_events(path) -> list[dict]
- aggregate(events) -> dict
- SUMMARY_KEY_ORDER tuple
- format_summary(summary) -> str
"""

import json

SUMMARY_KEY_ORDER = ("total_events", "kinds", "first_ts", "last_ts")


def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _validate_event(event, lineno):
    is_object = isinstance(event, dict)
    has_required_keys = is_object and "ts" in event and "kind" in event
    if not is_object:
        raise ValueError(
            "line %d: event must be a JSON object, got %s" % (lineno, type(event).__name__)
        )
    if not has_required_keys:
        missing = [key for key in ("ts", "kind") if key not in event]
        raise ValueError("line %d: event missing key(s): %s" % (lineno, ", ".join(missing)))
    if not _is_number(event["ts"]) and not isinstance(event["ts"], str):
        raise ValueError(
            "line %d: 'ts' must be a number or string, got %s"
            % (lineno, type(event["ts"]).__name__)
        )
    if not isinstance(event["kind"], str):
        raise ValueError(
            "line %d: 'kind' must be a string, got %s" % (lineno, type(event["kind"]).__name__)
        )


def load_events(path):
    """Read events from ``path``: either a JSON array or JSON lines.

    Returns a list of event dicts. Each event must be an object with a
    'ts' key (number or string) and a 'kind' key (string).
    Raises ValueError on unparseable content or invalid events.
    """
    with open(path, "r", encoding="utf-8") as handle:
        text = handle.read()

    stripped = text.strip()
    if not stripped:
        return []

    try:
        data = json.loads(stripped)
    except json.JSONDecodeError as parse_error:
        # Not a single parseable JSON document: try JSON lines format.
        return _load_events_lines(text, parse_error)
    return _load_events_document(data, multiline=False)


def _load_events_document(data, multiline):
    if isinstance(data, dict):
        if multiline:
            raise ValueError("JSON lines input must contain one JSON object per line")
        _validate_event(data, 1)
        return [data]
    if not isinstance(data, list):
        raise ValueError("JSON document must be an array of events")
    if multiline:
        raise ValueError("JSON lines input must contain one JSON object per line")
    for lineno, event in enumerate(data, start=1):
        _validate_event(event, lineno)
    return data


def _load_events_lines(text, parse_error):
    events = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        stripped_line = line.strip()
        if not stripped_line:
            continue
        try:
            event = json.loads(stripped_line)
        except json.JSONDecodeError as line_error:
            raise ValueError(
                "line %d: unparseable content: %s" % (lineno, line_error)
            ) from line_error
        _validate_event(event, lineno)
        events.append(event)
    if not events:
        raise ValueError("unparseable content: %s" % (parse_error,))
    return events


def _ts_order_key(ts):
    """Total order across ts representations.

    Epoch numbers sort before ISO-8601 strings; within a representation the
    natural order applies (numeric / lexicographic -- chronological for
    consistent-format ISO timestamps). Makes mixed str/number event streams
    deterministic instead of raising TypeError.
    """
    if isinstance(ts, str):
        return (1, ts)
    return (0, float(ts))


def aggregate(events):
    """Summarize ``events``: total count, kinds counter, first/last ts."""
    total_events = len(events)
    kinds = {}
    first_ts = None
    last_ts = None
    first_key = None
    last_key = None

    for event in events:
        kind = event["kind"]
        kinds[kind] = kinds.get(kind, 0) + 1
        ts = event["ts"]
        order_key = _ts_order_key(ts)
        if first_key is None or order_key < first_key:
            first_key, first_ts = order_key, ts
        if last_key is None or order_key > last_key:
            last_key, last_ts = order_key, ts

    return {
        "total_events": total_events,
        "kinds": kinds,
        "first_ts": first_ts,
        "last_ts": last_ts,
    }


def format_summary(summary):
    """Render ``summary`` with keys in SUMMARY_KEY_ORDER via json.dumps."""
    ordered = {}
    for key in SUMMARY_KEY_ORDER:
        ordered[key] = summary[key]
    return json.dumps(ordered, sort_keys=False)
