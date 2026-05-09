---
name: data-hygiene-checks
category: novelpedia/analytics
version: 3.0.0
description: Validate PostHog data quality before any analysis. Ground-truth verified 2026-04-29.
priority: medium
inputs:
  - date_range (default: 7d)
outputs:
  - Hygiene score per check
  - Bug list with severity
  - Fix recommendations
requires:
  - PostHog Events API
---

# Data Hygiene Checks

## Run These Before Any Analysis

---

## Check 1: UTM Persistence at Registration 🔴 CRITICAL

**Query:**
```python
/events/?event=user_registered&limit=100
```

**Expected:** user_registered events should have utm_campaign, utm_source, utm_medium on the person profile (via $identify)

**Actual (2026-04-29):**
- 191 registrations in 30 days
- 0.0% have UTM at event level
- 0.0% have UTM at person level (via $set/$identify)
- Only `role`, `has_email`, `is_migrated` are set

**Severity:** 🔴 CRITICAL

**Impact:** Cannot attribute registrations to campaigns. All registration ROI is unknown.

**Fix:** Persist UTM to person profile on first $pageview (including anonymous users). Call `$set` with `$initial_utm_campaign`, `$initial_utm_source`, `$initial_utm_medium`, `$initial_utm_content` on the person's FIRST pageview. This survives through `$identify` to registration. Arcsol must implement this on the reader app.

---

## Check 2: Chapter Completion Attribution Gap 🟡 WARNING

**Query:**
```python
/events/?event=chapter_completed&limit=100
```

**Actual (2026-04-29):**
- 1,382 chapter completions in 30 days | 270 distinct users
- 36.3% have UTM at event level
- 56.5% have UTM at person level
- **43.5% unattributed at person level**

**Severity:** 🟡 WARNING

**Impact:** Nearly half of chapter completions cannot be linked to a campaign. Author dopamine signal is partially dark.

**Fix:** Same as Check 1 — improve UTM persistence for anonymous sessions. Ensure `$identify` with `$initial_utm_*` is called for all first-touch sessions before any chapter interaction.

---

## Check 3: Author Events — `chapter_published` Fires ✅ WORKING

**Query:**
```python
/events/?event=chapter_published&limit=10
```

**Actual (2026-04-29):**
- 205 events in 30 days | 20 distinct authors
- 0% UTM (server-side, expected)
- ✅ Event IS firing correctly

**Note:** `chapter_published` is server-side and UTM-free by design. No action needed.

---

## Check 4: Author Events — `comment_created` 🟡 WARNING (UTM only)

**Query:**
```python
/events/?event=comment_created&limit=100
```

**Actual (2026-04-29):**
- 60 comment events in 30 days | 21 distinct users
- 0.0% UTM at event level
- 0.0% UTM at person level
- **Event IS firing** — but completely unattributed

**Severity:** 🟡 WARNING (UTM only — event works)

**Impact:** Author dopamine from comments cannot be linked to campaigns.

**Fix:** Same UTM persistence fix as Check 1 will cover comment attribution.

---

## Check 5: Host Scoping on Reader Dashboard 🟡 WARNING

**Dashboard:** 1483189 (Reader platform)

**Expected:** Should query novelpedia.net AND demo.novelpedia.net

**Actual:** May only query demo.novelpedia.net

**Severity:** 🟡 WARNING

**Impact:** Real reader data from novelpedia.net (~170k events) may be excluded from Reader Platform dashboard.

**Fix:** Update dashboard tiles to include `$host = "novelpedia.net"` OR create unified reader dashboard. Verify with: `SELECT DISTINCT properties.$host FROM events WHERE event = 'chapter_opened'`

---

## Check 6: $identify is Working ✅ CONFIRMED

**Query:**
```python
/events/?event=$identify&limit=100
```

**Actual (2026-04-29):**
- 202 events in 30 days | 116 distinct users
- 96 fires in last 7 days
- 1.5% UTM (expected — identify merges guest→user, doesn't originate UTM)

**Status:** ✅ NOT broken. Confirmed working.

---

## Check 7: No Funnel Objects Exist 🟠 INFO

**Query:**
```python
GET /api/projects/314999/funnels/
```

**Actual:** Returns `{"results": [], "count": 0}`

**Severity:** 🟠 INFO (not a bug — by design)

**Impact:** `ph_get_funnel` MCP tool returns 404. All funnel analysis must use TrendsQuery with event series instead.

**Fix:** No fix needed for queries — just use event series queries. If you want funnel objects, create them in PostHog UI or via API.

---

## Check 8: No Cohorts Defined 🟠 INFO

**Query:**
```python
GET /api/projects/314999/cohorts/
```

**Actual:** Returns `{"results": [], "count": 0}`

**Severity:** 🟠 INFO

**Impact:** Retention analysis cannot use cohort queries. Must use ad-hoc person property filters.

**Fix:** Create cohorts via PostHog UI: `new_users_7d`, `binge_readers_5chapters`, `churned_7d`

---

## Check 9: Test Account Detection

**Query:**
```python
/events/?event=$identify&limit=1000
# Filter by properties.$email matching test|dev|qa patterns
```

**Note:** `$identify` events carry user properties including email. No user_registered events have UTM, so test account detection via email requires filtering `$identify` events.

---

## Data Quality Summary (2026-04-29)

| Check | Status | Severity |
|-------|--------|----------|
| UTM → Registration | 🔴 BROKEN | CRITICAL |
| UTM → chapter_completed | 🟡 PARTIAL (43.5% gap) | WARNING |
| UTM → chapter_opened | 🟡 PARTIAL (45.2% gap) | WARNING |
| UTM → comment_created | 🔴 DARK (100% gap) | WARNING |
| chapter_published fires | ✅ YES | — |
| comment_created fires | ✅ YES (60 events) | — |
| app_opened fires | ✅ YES (17,864 events) | — |
| $identify works | ✅ YES (202 events) | — |
| Host scoping (novelpedia.net) | ⚠️ UNCONFIRMED | WARNING |
| Funnel objects | 🟠 0 exist | INFO |
| Cohorts | 🟠 0 defined | INFO |
