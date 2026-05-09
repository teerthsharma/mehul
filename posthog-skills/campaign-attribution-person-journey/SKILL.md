---
name: campaign-attribution-person-journey
category: novelpedia/analytics
version: 2.0.0
description: First-touch UTM attribution via $identify/$set events. Resolves person journey from landing pageview to all downstream events. WARNING: user_registered has NO UTM - this skill uses $initial_utm_* on person profiles.
priority: critical
inputs:
  - date_range (7d, 14d, 30d)
  - person_id (distinct_id)
outputs:
  - First-touch campaign for a person
  - Downstream events attributed to that campaign
  - Registration status
requires:
  - PostHog Events API ($identify, $set, chapter_opened, chapter_completed)
  - Person profile with $initial_utm_* set

---

# Campaign Attribution: Person Journey

## CRITICAL: UTM Persistence Broken at Registration

`user_registered` does NOT carry UTM params. The UTM attribution path must use `$identify`/`$set` events which set `$initial_utm_*` on the person profile.

## How UTM Attribution Works (Should Work)

1. User lands on novelpedia.net via UTM URL
2. PostHog JS captures UTM params on $pageview
3. If user registers: posthog.identify() should be called with $initial_utm_* from URL
4. $identify event carries $initial_utm_campaign, $initial_utm_source, $initial_utm_medium
5. Person profile now has UTM stored for attribution

## Current Status

- $pageview events DO carry UTM params (verified)
- chapter_opened events DO carry UTM params (verified)
- $identify events exist in raw stream (verified)
- $initial_utm_* is set on person at registration: UNVERIFIED

## MCP Commands

```python
# Get $identify events (person identification with initial UTM)
GET /events/?event=$identify&limit=100

# Get person profile
GET /api/projects/314999/persons/?id={distinct_id}
# Check properties for $initial_utm_campaign, $initial_utm_source, $initial_utm_medium
```

## Attribution Path

For a given distinct_id:
1. Find most recent $identify event -> get $initial_utm_* from properties
2. Find all chapter_opened events by this distinct_id
3. All chapters are attributed to the first-touch campaign

## Known Campaigns

- reader-mage - aads-novelfire, cpc
- self-summoning-demon - aads-novelfire, cpc
- inertia-beneath-starlit-veil - aads-novelfire, cpc
- gu-demon-king - aads-novelfire, cpc

## Attribution Matrix

| Event | Has UTM | Attributable |
|-------|---------|-------------|
| $pageview | YES (landing only) | First-touch only |
| chapter_opened | YES | First-touch |
| chapter_completed | YES | First-touch |
| novel_detail_viewed | YES | First-touch |
| novel_followed | YES | First-touch |
| user_registered | NO | NOT attributable |
| $identify | YES ($initial_utm_*) | Should work |
