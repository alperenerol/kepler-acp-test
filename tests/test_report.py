# WS2 — tests for reporting/report.py (JSON report module).
# Spec: load_events(path) accepts a JSON array or JSON-lines file, returns list
# of event dicts, ValueError on unparseable content, ts (num/str) + kind (str)
# required; aggregate(events) fixed keys; format_summary emits keys in
# SUMMARY_KEY_ORDER via json.dumps(sort_keys=False).

import json

import pytest

from reporting.report import load_events, aggregate, format_summary, SUMMARY_KEY_ORDER


EV_A = {"ts": "2026-01-01T00:00:00Z", "kind": "run_start"}
EV_B = {"ts": "2026-01-02T00:00:00Z", "kind": "step"}
EV_NUM = {"ts": 1719999999, "kind": "step"}
EV_FLOAT = {"ts": 1719999999.5, "kind": "run_end"}


def _event_lines(events):
    return "\n".join(json.dumps(ev) for ev in events) + "\n"


# --- load_events -------------------------------------------------------------

def test_load_events_json_array(tmp_path):
    path = tmp_path / "events.json"
    path.write_text(json.dumps([EV_A, EV_B, EV_NUM]), encoding="utf-8")
    assert load_events(str(path)) == [EV_A, EV_B, EV_NUM]


def test_load_events_json_lines(tmp_path):
    path = tmp_path / "events.jsonl"
    path.write_text(_event_lines([EV_A, EV_B, EV_NUM]), encoding="utf-8")
    assert load_events(str(path)) == [EV_A, EV_B, EV_NUM]


def test_load_events_json_lines_skips_blank_lines(tmp_path):
    path = tmp_path / "events.jsonl"
    path.write_text("\n\n" + json.dumps(EV_A) + "\n   \n" + json.dumps(EV_B) + "\n\n", encoding="utf-8")
    assert load_events(str(path)) == [EV_A, EV_B]


def test_load_events_lines_vs_array_equivalence(tmp_path):
    events = [EV_A, EV_NUM, EV_FLOAT]
    array_path = tmp_path / "array.json"
    lines_path = tmp_path / "lines.jsonl"
    array_path.write_text(json.dumps(events), encoding="utf-8")
    lines_path.write_text(_event_lines(events), encoding="utf-8")
    from_array = load_events(str(array_path))
    from_lines = load_events(str(lines_path))
    assert from_array == from_lines == events


def test_load_events_single_dict_line(tmp_path):
    path = tmp_path / "single.jsonl"
    path.write_text(json.dumps(EV_A) + "\n", encoding="utf-8")
    assert load_events(str(path)) == [EV_A]


def test_load_events_garbage_raises_valueerror(tmp_path):
    path = tmp_path / "garbage.json"
    path.write_text("not json at all", encoding="utf-8")
    with pytest.raises(ValueError):
        load_events(str(path))


def test_load_events_broken_json_raises_valueerror(tmp_path):
    path = tmp_path / "broken.json"
    path.write_text('{"ts": 1, "kind": "step",', encoding="utf-8")
    with pytest.raises(ValueError):
        load_events(str(path))


def test_load_events_broken_json_line_raises_valueerror(tmp_path):
    path = tmp_path / "broken.jsonl"
    path.write_text(json.dumps(EV_A) + '\n{"ts": 1, "kind": "step"\n', encoding="utf-8")
    with pytest.raises(ValueError):
        load_events(str(path))


def test_load_events_missing_ts_raises_valueerror(tmp_path):
    path = tmp_path / "no_ts.json"
    path.write_text(json.dumps([{"kind": "step"}]), encoding="utf-8")
    with pytest.raises(ValueError):
        load_events(str(path))


def test_load_events_missing_kind_raises_valueerror(tmp_path):
    path = tmp_path / "no_kind.json"
    path.write_text(json.dumps([{"ts": 1719999999}]), encoding="utf-8")
    with pytest.raises(ValueError):
        load_events(str(path))


def test_load_events_non_str_kind_raises_valueerror(tmp_path):
    path = tmp_path / "bad_kind.jsonl"
    path.write_text(json.dumps({"ts": 1719999999, "kind": 7}) + "\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_events(str(path))


def test_load_events_non_scalar_ts_raises_valueerror(tmp_path):
    path = tmp_path / "bad_ts.jsonl"
    path.write_text(json.dumps({"ts": [1, 2], "kind": "step"}) + "\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_events(str(path))


def test_load_events_array_of_non_objects_raises_valueerror(tmp_path):
    path = tmp_path / "scalar_array.json"
    path.write_text(json.dumps([1, 2, 3]), encoding="utf-8")
    with pytest.raises(ValueError):
        load_events(str(path))


# --- aggregate ---------------------------------------------------------------

def test_aggregate_empty_events():
    summary = aggregate([])
    assert summary == {"total_events": 0, "kinds": {}, "first_ts": None, "last_ts": None}
    assert sorted(summary.keys()) == sorted(SUMMARY_KEY_ORDER)


def test_aggregate_single_event():
    summary = aggregate([EV_A])
    assert summary == {
        "total_events": 1,
        "kinds": {"run_start": 1},
        "first_ts": "2026-01-01T00:00:00Z",
        "last_ts": "2026-01-01T00:00:00Z",
    }


def test_aggregate_multiple_kinds_counts():
    events = [EV_A, EV_B, EV_A, EV_NUM, EV_B]
    summary = aggregate(events)
    assert summary["total_events"] == 5
    assert summary["kinds"] == {"run_start": 2, "step": 3}


def test_aggregate_first_last_ts_str():
    summary = aggregate([EV_B, EV_A])
    assert summary["first_ts"] == "2026-01-01T00:00:00Z"
    assert summary["last_ts"] == "2026-01-02T00:00:00Z"


def test_aggregate_epoch_number_ts():
    events = [
        {"ts": 1719999999, "kind": "step"},
        {"ts": 1600000000, "kind": "run_start"},
        {"ts": 1719999999.5, "kind": "run_end"},
    ]
    summary = aggregate(events)
    assert summary["first_ts"] == 1600000000
    assert summary["last_ts"] == 1719999999.5
    assert summary["kinds"] == {"step": 1, "run_start": 1, "run_end": 1}
    assert summary["total_events"] == 3


# --- SUMMARY_KEY_ORDER / format_summary --------------------------------------

def test_summary_key_order_tuple():
    assert SUMMARY_KEY_ORDER == ("total_events", "kinds", "first_ts", "last_ts")


def test_format_summary_returns_str():
    assert isinstance(format_summary(aggregate([])), str)


def test_format_summary_key_order_from_scrambled_input():
    scrambled = {
        "last_ts": "2026-01-02T00:00:00Z",
        "first_ts": "2026-01-01T00:00:00Z",
        "total_events": 2,
        "kinds": {"step": 1, "run_start": 1},
    }
    ordered = json.loads(
        format_summary(scrambled), object_pairs_hook=lambda pairs: [k for k, _ in pairs]
    )
    assert ordered == ["total_events", "kinds", "first_ts", "last_ts"]


def test_format_summary_empty_summary_exact_output():
    assert format_summary(aggregate([])) == (
        '{"total_events": 0, "kinds": {}, "first_ts": null, "last_ts": null}'
    )


def test_format_summary_does_not_mutate_input():
    original = {"total_events": 1, "kinds": {"step": 1}, "first_ts": 1719999999, "last_ts": 1719999999}
    snapshot = dict(original)
    formatted = format_summary(original)
    assert original == snapshot
    assert json.loads(formatted) == original


# --- end to end --------------------------------------------------------------

def test_round_trip_load_aggregate_format(tmp_path):
    path = tmp_path / "events.jsonl"
    events = [EV_A, EV_B, EV_NUM]
    path.write_text(_event_lines(events), encoding="utf-8")
    summary = aggregate(load_events(str(path)))
    formatted = format_summary(summary)
    assert json.loads(formatted) == summary
    assert isinstance(formatted, str)
