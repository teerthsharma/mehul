---
name: posthog-metrics-pack
category: novelpedia/analytics
version: 2.0.0
description: Canonical metric definitions for Novelpedia PostHog analytics. Updated with real API-verified data.
priority: critical
inputs:
  - date_range (7d, 30d, 90d)
  - host (novelpedia.net, author.novelpedia.net)
  - campaign_filter (utm_campaign, utm_source)
outputs:
  - Metric values with units
  - Comparison to baseline/threshold
  - Decision recommendation
requires:
  - PostHog events API (events list)
  - PostHog insights API (trends)
  - NO funnel API (funnels return 404 — use TrendsQuery instead)

---

# Novelpedia Metrics Pack v2.0

> CRITICAL CHANGES from v1:
> - chapter_opened = north-star (NOT app_opened)
> - user_registered has NO UTM — attribution broken at registration
> - Funnel IDs (GDMegn0H etc.) return 404 — use TrendsQuery event series
> - 0 cohorts, 0 feature flags exist

---

## North-Star Metric

**chapter_opened** = active user = north-star

A "active user" is someone who opens a chapter. Not app_opened. Not $pageview. chapter_opened.

WAU = distinct users with chapter_opened in 7-day window
DAU = distinct users with chapter_opened in 1-day window
MAU = distinct users with chapter_opened in 30-day window

---

## Core Event Map

| Event | UTM | Geo | North-Star | Funnel Step | Author-Side |
|-------|-----|-----|------------|-------------|-------------|
| chapter_opened | ✅ | ✅ | ✅ | Step 2 | |
| chapter_completed | ✅ | ✅ | | Step 3 | |
| user_registered | ❌ | | | Conversion | |
| novel_detail_viewed | ✅ | ✅ | | Step 1 | |
| novel_followed | ✅ | | | Engagement | |
| share_clicked | ✅ | | | Engagement | |
| comment_created | ✅ | | | Engagement | ✅ |
| novel_card_clicked | ✅ | | | Discovery | |
| carousel_clicked | ✅ | | | Discovery | |
| app_opened | ✅ | ✅ | | | |
| $pageview | ✅ | ✅ | | | |
| novel_published | | | | | ✅ |
| `comment_created` | 60 events/30d | 0% UTM | Author dopamine | WARNING | ✅ (but unattributable) |
| streak_milestone_reached | | | | Retention | |

---

## Dashboard Index

| ID | Name | Purpose |
|----|------|---------|
| 1458931 | Executive Overview | Binge Reader North Star + platform health |
| 1458292 | Reader App | demo.novelpedia.net + novelpedia.net |
| 1458291 | Author App | author.novelpedia.net |
| 1484131 | Campaign ROI & Activation | Campaign × creative × activation |
| 1458933 | Content & Discovery Engine | Product + content optimization |
| 1483188 | Overall Platform | Cross-platform north star + core funnels |
| 1483189 | Reader Platform | ⚠️ Only demo.novelpedia.net (not novelpedia.net) |
| 1483191 | Author Platform | author.novelpedia.net |

---

## Critical Bugs to Check

1. **Registration attribution BROKEN** — user_registered has no UTM. Must fix at instrumentation level.
2. **Funnels don't exist** — all funnel IDs (GDMegn0H etc.) return 404. Use TrendsQuery.
3. **Reader dashboard wrong host** — 1483189 queries only demo.novelpedia.net, not novelpedia.net.
4. **Author events partially dark** — chapter_published fires (205 events), but comment_created has 0% UTM. Author engagement cannot be campaign-attributed yet.
5. **0 cohorts, 0 feature flags** — cohort queries will return empty.

---

## Alert Thresholds

| Metric | Critical | Warning |
|--------|----------|---------|
| chapter_opened (daily) | < 5 | < 20 |
| chapter_completed (daily) | < 2 | < 5 |
| user_registered (daily) | 0 (if expected) | < 3 |
| novel_detail_viewed (daily) | < 10 | < 25 |
| Funnel step drop-off | > 50% per step | > 30% per step |

---

## UTM Filters (from real dashboards)

```
# Standard campaign filter (used in most dashboards)
event_filter: utm_campaign is_set AND utm_campaign is_not ["novelpedia-launch", "novelpedia"]
utm_source_filter: utm_source is_not ["aads-ranobes", "aads-freewebnovel"]
utm_content_filter: utm_content is_set

# Attribution filter (for $identify / person attribution)
person_filter: $initial_utm_campaign is_set AND $initial_utm_campaign is_not ["novelpedia-launch", "novelpedia"]
```

---

## API Notes

- Funnel API: `/api/projects/314999/funnels/{id}/` → **404 for all IDs**
- TrendsQuery via `/api/projects/314999/insights/trend/` → **403 Forbidden**
- Events API: `/api/projects/314999/events/` → **✅ WORKS**
- Dashboards API: `/api/projects/314999/dashboards/{id}/` → **✅ WORKS**
- Cohort API: `/api/projects/314999/cohorts/` → ✅ works, returns empty

**Primary data access**: Events API (paginated) + Dashboard tile queries

---

## Verified Event Properties (from 1000-event sample)

### chapter_opened
`chapter_id, chapter_number, chapter_title, novel_id, novel_title, word_count, time_spent_sec, path, referrer, referring_domain, http_country_code, utm_campaign, utm_content, utm_medium, utm_source, utm_term, is_online, is_pwa_installed`

### chapter_completed
Same as chapter_opened + `time_spent_sec`

### user_registered
`role, has_email, is_migrated` ← **NO UTM**

### novel_detail_viewed
`novel_id, novel_title, path, referrer, referring_domain, utm_*`

### novel_card_clicked
`novel_id, novel_title, source, source_surface, rank, path, referrer, utm_*`

### novel_followed, share_clicked, comment_created
`novel_id, novel_title, utm_*`

### $pageview
`title, path, referrer, $host, utm_*, http_country_code`

---

## Degraded Mode (when APIs are restricted)

When insights/trends API returns 403:
- Use Events API with date filtering + aggregation in Python
- Group events by date using chapter_opened timestamp
- Count distinct users with chapter_opened per day for WAU/DAU
