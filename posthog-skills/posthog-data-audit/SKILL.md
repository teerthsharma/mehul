---
name: posthog-data-audit
description: PostHog ground-truth audit pattern — verify dashboards, funnels, events, and person properties before building any analytics skills. Prevents building skills with placeholder IDs or wrong event semantics.
version: 1.0.0
category: novelpedia
metadata:
  novelpedia:
    owner: ai-engineering
    review_cadence: on PostHog config changes
---

# PostHog Data Audit — Verify Before You Build

## Context
When integrating PostHog into an analytics system, initial API queries often return empty results or use placeholder names that mislead downstream skill building. This skill encodes the audit pattern used to establish ground truth before building any PostHog-based skills.

## The Problem
- `/api/projects/{id}/funnels/` returning `{"results": []}` does NOT mean funnels don't exist — PostHog funnels are `insight` objects with `insight_type: "funnels"`, not a separate `/funnels/` endpoint
- `/api/projects/{id}/cohorts/` returning `{"results": []}` may mean the API key lacks permissions or the endpoint is wrong
- `user_active` event — always verify it actually exists in the event taxonomy before using it as an active user proxy
- `app_opened` and `chapter_opened` are SEMANTICALLY DIFFERENT — one means PWA launch, one means a chapter was read (the actual business event)

## Audit Sequence (in order)

### Step 1: List real dashboards
```
GET /api/projects/{project_id}/dashboards/
```
Response: `{"results": [{"id": 1458931, "name": "Executive Overview (The Pulse)", ...}, ...]}`
Always get dashboard IDs — they're needed for deep-links and skill references.

### Step 2: List all insights (includes funnels)
```
GET /api/projects/{project_id}/insights/?insight=funnel&limit=100
```
This is the correct endpoint for funnels. The dedicated `/funnels/` endpoint often returns empty even when funnels exist.

### Step 3: Verify event names in the actual event taxonomy
```
GET /api/projects/{project_id}/events/?limit=1&event=chapter_opened
GET /api/projects/{project_id}/events/?limit=1&event=app_opened
GET /api/projects/{project_id}/events/?limit=1&event=user_active
```
Check which events actually fire. Do NOT assume event names from documentation or convention.

### Step 4: Query person properties
```
GET /api/projects/{project_id}/persons/properties/
```
Verify `is_paying_user`, `initial_utm_source`, `chapter_progress` etc. are actually set as person properties.

### Step 5: Check cohorts
```
GET /api/projects/{project_id}/cohorts/
```
If empty, cohorts may need to be created via UI or the API key may lack permissions. Do NOT assume cohorts exist.

### Step 6: Verify distinct_id stitching
In PostHog UI: People → Devices → "Unidentified users" count.
If high, anonymous sessions aren't merging to registered users — all person-level analytics are unreliable.

## Common Pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| Using wrong endpoint for funnels | Funnel API returns empty despite funnels existing | Use `/insights/?insight=funnel` not `/funnels/` |
| `app_opened` as active user | Metrics inflated by non-reading PWA opens | Use `chapter_opened` as active user proxy |
| Placeholder funnel IDs in skills | Skills reference `[FUNNEL_ID]` or non-existent IDs | Always get real IDs from `/insights/` before building skills |
| `user_active` event assumed | Event doesn't exist in the project | Verify with `/events/?event=user_active` |
| Dashboard IDs guessed | Wrong deep-links in skills | Always fetch from `/dashboards/` API |
| Author events mixed with reader events | Reader metrics polluted by author activity | Scope by `$host` property: `author.novelpedia.net` vs `novelpedia.net` |

## Verification Checklist Before Building PostHog Skills

- [ ] Dashboard IDs fetched and stored in skill
- [ ] Funnel IDs fetched (via `/insights/?insight=funnel`) and stored in skill
- [ ] Event names verified against actual PostHog events API
- [ ] `chapter_opened` confirmed as the north-star / active-user event
- [ ] `app_opened` confirmed as NOT a business event (PWA launch only)
- [ ] Host scoping confirmed: `novelpedia.net` = reader, `author.novelpedia.net` = author
- [ ] Person properties verified (especially `is_paying_user`)
- [ ] `distinct_id` stitching verified (anonymous → registered merge)
