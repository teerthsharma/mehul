---
name: posthog-live-audit
category: novelpedia/analytics
version: 1.0.0
description: Reverse-engineer a live PostHog project by pulling raw API data first. Use this before building any analytics skill — always verify events, dashboards, and funnels exist with real API calls, not assumptions.
trigger: Before building any new PostHog analytics skill
inputs:
  - API key (phx_...)
  - Project ID (from project settings URL)
outputs:
  - Verified event taxonomy with real property names
  - Working API endpoints (some return 404/403 — discover which)
  - Dashboard IDs and their actual query patterns
  - Host scoping verified from data
  - Critical bugs flagged before skills are built on top of bad assumptions
requires:
  - PostHog Personal API key
  - Python stdlib (urllib, json)

---

# PostHog Live Audit Pattern

> **When to use:** Before building any analytics skill, or when debugging PostHog data issues. Always verify before building.

## The Core Problem

PostHog skills fail silently when:
- Funnel IDs don't exist (return 404)
- Insights API returns 403 (requires higher permissions)
- Events have different property names than expected
- UTM persistence is broken at registration
- Author events aren't firing

Building skills on assumptions leads to skills that return empty data or 404s in production.

## The Pattern

```
Step 1: Pull raw events (large sample, no filters)
Step 2: Verify event types and property names
Step 3: Test dashboard and funnel endpoints
Step 4: Extract dashboard query patterns
Step 5: Verify host scoping
Step 6: Flag critical bugs before building skills
Step 7: Build grounded skills from verified data
```

---

## Step 1: Pull Raw Events

```python
import urllib.request
import json

API_KEY = "phx_YOUR_KEY"
BASE = "https://app.posthog.com"
PROJECT_ID = "314999"  # from app.posthog.com/project/<id>/settings
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

def get(url):
    req = urllib.request.Request(BASE + url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read())

# Get 500-1000 events in ONE request (no pagination - sandbox DNS drops after first redirect)
resp = get(f"/api/projects/{PROJECT_ID}/events/?limit=1000")
events = resp.get('results', [])
```

## Step 2: Build Event Taxonomy

```python
event_data = {}
for e in events:
    n = e['event']
    if n not in event_data:
        event_data[n] = {"count": 0, "sample": None, "properties": set()}
    event_data[n]["count"] += 1
    if event_data[n]["sample"] is None:
        # Only non-$ properties
        event_data[n]["sample"] = {k: v for k, v in e.get('properties', {}).items() if not k.startswith('$')}
    for k in e.get('properties', {}).keys():
        if not k.startswith('$'):
            event_data[n]["properties"].add(k)

for ev, data in sorted(event_data.items(), key=lambda x: -x[1]["count"]):
    print(f"{ev}: {data['count']} events")
    print(f"  Properties: {sorted(data['properties'])}")
```

## Step 3: Test Endpoint Availability

```python
# These patterns are common failures - test them all
tests = [
    ("Events API", f"/api/projects/{PROJECT_ID}/events/?limit=1"),
    ("Dashboard", f"/api/projects/{PROJECT_ID}/dashboards/1458931/"),
    ("Funnel by ID", f"/api/projects/{PROJECT_ID}/funnels/GDMegn0H/"),
    ("Funnel list", f"/api/projects/{PROJECT_ID}/funnels/"),
    ("Cohorts", f"/api/projects/{PROJECT_ID}/cohorts/"),
    ("Feature Flags", f"/api/projects/{PROJECT_ID}/feature_flags/"),
    ("Insights Trend", f"/api/projects/{PROJECT_ID}/insights/trend/"),
]

for name, url in tests:
    try:
        resp = get(url)
        print(f"OK  {name}: {str(resp)[:80]}")
    except Exception as e:
        print(f"FAIL {name}: {type(e).__name__}: {e}")
```

## Step 4: Extract Dashboard Query Patterns

```python
# Get all tiles from a dashboard to reverse-engineer actual queries
resp = get(f"/api/projects/{PROJECT_ID}/dashboards/1484131/")  # Campaign ROI
for i, tile in enumerate(resp.get('tiles', [])):
    ins = tile.get('insight', {})
    query = ins.get('query', {})
    source = query.get('source', {})
    series = source.get('series', [])
    
    for j, s in enumerate(series):
        ev = s.get('event')
        math = s.get('math', 'total')
        props = s.get('properties', [])
        print(f"  Tile {i+1}: {ev} ({math})")
        for p in props:
            print(f"    Filter: {p['key']} {p['operator']} {p.get('value', '?')}")
```

## Step 5: Verify Host Scoping

```python
hosts = set()
for e in events:
    h = e.get('properties', {}).get('$host', e.get('properties', {}).get('host', 'N/A'))
    hosts.add(h)
print(f"Hosts seen: {hosts}")
```

## Step 6: Check UTM Persistence

```python
# CRITICAL: verify user_registered has UTM
user_reg = [e for e in events if e['event'] == 'user_registered']
print(f"user_registered events: {len(user_reg)}")
for e in user_reg[:5]:
    props = {k: v for k, v in e['properties'].items() if not k.startswith('$')}
    has_utm = any('utm' in k.lower() for k in props.keys())
    print(f"  UTM present: {has_utm} | props: {list(props.keys())}")
```

## Step 7: Check Author Events

```python
import urllib.parse
# Filter by author.novelpedia.net
filter_str = urllib.parse.quote('{"$host":"author.novelpedia.net"}')
resp = get(f"/api/projects/{PROJECT_ID}/events/?limit=500&properties={filter_str}")
event_types = {}
for e in resp.get('results', []):
    n = e['event']
    event_types[n] = event_types.get(n, 0) + 1
print(f"Author app event types: {event_types}")
```

---

## Known PostHog API Failure Patterns

| Pattern | Symptom | Solution |
|---------|---------|----------|
| Funnel IDs return 404 | `/funnels/{id}/` returns not found | Use TrendsQuery with event series instead |
| Insights returns 403 | `/insights/trend/` forbidden | Use events API + Python aggregation |
| Dashboard tile name is "?" | Tile name not in API response | Use `insight.name` field |
| Pagination DNS failure | Sandbox can't resolve on 2nd request | Use large limit in single request |
| 0 cohorts | Cohort API returns empty | Create cohorts in UI or use property filters |
| UTM missing on registration | `user_registered` has no UTM | Fix instrumentation at registration page |
| Author events not firing | novel_published missing | Instrument author.novelpedia.net frontend |

---

## Critical Checks Before Building Skills

1. **user_registered has UTM?** If not, registration attribution is broken
2. **Funnel IDs return 404?** If yes, use TrendsQuery/event series
3. **Insights API accessible?** If 403, use events API + Python agg
4. **Author events firing?** If not, author dashboard will be empty
5. **Host scoping correct?** Verify dashboard queries match your host map
6. **0 cohorts?** Flag this - retention analysis needs cohorts or property filters

---

## Pitfalls

- **Don't assume event property names** — verify from raw data. `chapter_number` not `chapter`, `http_country_code` not `country`.
- **Don't use funnel IDs without verifying** — always test `/funnels/{id}/` first.
- **Don't rely on insights API** — test it. 403 is common.
- **Don't assume UTM persistence works** — check `user_registered` specifically.
- **Don't build skills without host scoping verified** — dashboard may query wrong host.

---

## Verification Steps

After building a skill, verify it works:
```python
# Test skill logic against real events
test_events = get(f"/api/projects/{PROJECT_ID}/events/?event=chapter_opened&limit=100")
print(f"chapter_opened events found: {len(test_events.get('results', []))}")
```
