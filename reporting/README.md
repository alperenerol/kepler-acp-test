# WS2 — Python events report module.

This module implements the JSON report module spec.

## API

```python
from reporting import load_events, aggregate, format_summary, SUMMARY_KEY_ORDER
```

- `load_events(path)` -> list of event dicts (JSON array file or JSON lines, `{ts, kind}` objects); raises `ValueError` on unparseable content or invalid events.
- `aggregate(events)` -> `{"total_events": int, "kinds": {...}, "first_ts": ts-or-None, "last_ts": ts-or-None}`; deterministic ordering across mixed epoch-number/ISO-string timestamps (numbers sort before strings).
- `SUMMARY_KEY_ORDER = ("total_events", "kinds", "first_ts", "last_ts")`
- `format_summary(summary)` -> `json.dumps(..., sort_keys=False)` string with keys re-ordered per `SUMMARY_KEY_ORDER` — downstream consumers diff this exact output only.

## Tests

```bash
python3 -m pytest tests/ -p no:cacheprovider
```
