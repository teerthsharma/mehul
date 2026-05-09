# Event Taxonomy

> **Last verified:** 2026-04-29 | **Source:** PostHog project 314999 (full 30-day pull)
> **Total events:** 206,489 | **Distinct users:** 5,405 | **Event types:** 44

## ⚠️ CRITICAL BUGS — Read First

1. **`user_registered` has 0% UTM at BOTH event and person level** — registration does NOT capture UTM.
   Only `role`, `has_email`, `is_migrated` are set. Attribution from campaign → registration is BROKEN.
   Fix: persist UTM to person profile on first `$pageview` (including anonymous users), so `$initial_utm_*` survives through `$identify` to registration.

2. **0 funnel objects exist** — all funnel IDs (GDMegn0H etc.) return 404.
   Queries must use TrendsQuery event series instead of funnel API.

3. **`comment_created` has 0% UTM at both levels** — 60 events in 30 days, all unattributable.
   Author dopamine signal is completely dark. Same fix as above.

4. **~43.5% of `chapter_completed` events are unattributable** at person level.
   Person UTM = 56.5%, Event UTM = 36.3%. The gap means UTM was captured on first visit
   but not re-attached to later chapter completion events.

---

## Business Events

### `chapter_opened` ← NORTH-STAR = ACTIVE USER
- **30-day count:** 4,517 events | 608 distinct users
- **UTM:** 34.4% event-level | 54.8% person-level | **45.2% unattributed at person level**
- **Properties:** chapter_id, chapter_number, chapter_title, novel_id, novel_title, word_count, path, referrer, referring_domain, is_online, is_pwa_installed, http_country_code
- **Use for:** WAU/DAU/MAU (distinct users), funnel step, UTM attribution
- **⚠️ 45% gap** means nearly half of readers completing chapters cannot be linked to a campaign

### `chapter_completed`
- **30-day count:** 1,382 events | 270 distinct users
- **UTM:** 36.3% event-level | 56.5% person-level | **43.5% unattributed at person level**
- **Properties:** chapter_id, chapter_number, chapter_title, novel_id, novel_title, word_count, time_spent_sec, referrer, referring_domain, is_online, is_pwa_installed
- **Use for:** Funnel completion, reading depth, engagement quality

### `user_registered` 🔴 CRITICAL
- **30-day count:** 191 events | 191 distinct users
- **UTM:** 0.0% event-level | 0.0% person-level | **100% unattributed**
- **Properties:** role (READER/AUTHOR), has_email (bool), is_migrated (bool)
- **Use for:** Registration volume ONLY. NOT for attribution.
- **⚠️ BROKEN:** Cannot attribute registrations to campaigns. Fix UTM persistence at registration.

### `novel_detail_viewed`
- **30-day count:** 26,527 events | 3,998 distinct users
- **UTM:** 72.3% event-level | 48.8% person-level
- **Properties:** novel_id, novel_title, path, referrer, referring_domain, http_country_code
- **Use for:** Discovery funnel step, content performance

### `novel_followed`
- **30-day count:** 19 events | 13 distinct users
- **UTM:** 0.0% event-level | 0.0% person-level
- **Properties:** novel_id, novel_title
- **Use for:** Engagement depth, content quality signal

### `share_clicked`
- **30-day count:** 25 events | 16 distinct users
- **UTM:** 16.0% event-level | 16.0% person-level
- **Use for:** Viral engagement signal

### `comment_created` 🟡 WARNING
- **30-day count:** 60 events | 21 distinct users
- **UTM:** 0.0% event-level | 0.0% person-level | **100% unattributed**
- **Use for:** Author dopamine signal. Currently completely dark.

### `novel_card_clicked`
- **30-day count:** 3,525 events | 743 distinct users
- **UTM:** 8.5% event-level | 12.9% person-level
- **Properties:** novel_id, novel_title, source, source_surface, rank, path, referrer

### `carousel_clicked`
- **30-day count:** 2,308 events | 612 distinct users
- **UTM:** 9.0% event-level | 15.0% person-level
- **Properties:** carousel_title, carousel_type, novel_id, novel_title, novel_order, path, referrer

### `streak_milestone_reached`
- **30-day count:** 1,731 events | 319 distinct users
- **UTM:** 3.0% event-level | 11.0% person-level
- **Properties:** streak_count, path
- **Use for:** Reader loyalty, retention signal

### `registration_nudge_shown`
- **30-day count:** 659 events | 210 distinct users
- **UTM:** 23.8% event-level | 53.1% person-level
- **Properties:** chapter_id, novel_id, chapters_read (count), path

### `registration_nudge_dismissed`
- **30-day count:** 197 events | 159 distinct users
- **UTM:** 41.6% event-level | 64.5% person-level
- **Properties:** chapter_id, novel_id, chapters_read, path

### `registration_nudge_clicked`
- **30-day count:** 13 events | 13 distinct users
- **UTM:** 38.5% event-level | 61.5% person-level
- **Properties:** chapter_id, novel_id, chapters_read, path

### `notification_clicked`
- **30-day count:** 153 events | 35 distinct users
- **UTM:** 0.0% event-level | 3.3% person-level
- **Properties:** notification_id, notification_type, path

---

## Platform Events

### `app_opened` ⚠️ PWA launch only — NOT the north-star
- **30-day count:** 17,864 events | 4,707 distinct users
- **UTM:** 52.7% event-level | 39.5% person-level
- **Properties:** path, is_online, is_pwa_installed, http_country_code
- **Note:** PWA launch event. NOT equivalent to "active user". Use `chapter_opened`.

### `Application opened`
- **Note:** Variant name seen in Overall Platform dashboard (1483188). May be same as app_opened.

### `$pageview`
- **30-day count:** 39,741 events | 5,405 distinct users
- **UTM:** 21.2% event-level | 24.4% person-level
- **Properties:** title, path, referrer, $host, utm_campaign, utm_content, utm_medium, utm_source, http_country_code
- **$host values:** novelpedia.net (reader app), author.novelpedia.net (author dashboard), demo.novelpedia.net (staging)

### `$autocapture`
- **30-day count:** 62,172 events | 2,659 distinct users
- **UTM:** 13.6% event-level | 17.0% person-level
- **Note:** High volume — autocaptured interactions across the app

### `$web_vitals`
- **30-day count:** 15,216 events | 3,549 distinct users
- **UTM:** 25.7% event-level | 29.2% person-level
- **Properties:** CLS, LCP, FCP, TTFB, path

### `$pageleave`
- **30-day count:** 9,219 events | 4,407 distinct users
- **UTM:** 40.2% event-level | 34.0% person-level
- **Properties:** path, referrer, time_on_page

### `$set`
- **30-day count:** 5,050 events | 2,881 distinct users
- **UTM:** 80.2% event-level | 80.2% person-level (highest attributed event)
- **Note:** Person/profile update events — this is where $initial_utm_* is stored

### `$identify` ✅ WORKING
- **30-day count:** 202 events | 116 distinct users
- **UTM:** 1.5% event-level | 1.5% person-level
- **Status:** NOT broken — actively firing. 96 fires in last 7 days.
- **Note:** Guest-to-user merge events. Near-zero UTM expected here since identify merges, not originates.

### `$rageclick`
- **30-day count:** 723 events | 282 distinct users
- **UTM:** 14.8% event-level | 16.2% person-level

### `$exception`
- **30-day count:** 4,533 events | 3,595 distinct users
- **UTM:** 4.0% event-level | 4.7% person-level

---

## Author-Side Events (Server-Instrumented)

### `chapter_published`
- **30-day count:** 205 events | 20 distinct users
- **UTM:** 0.0% event-level | 0.0% person-level
- **Server-side** — author publishes a chapter on author.novelpedia.net

### `author_profile_created`
- **30-day count:** 38 events | 1 distinct user
- **UTM:** 0.0% | **Server-side** — author onboarding event

### `novel_created`
- **30-day count:** 25 events | 21 distinct users
- **UTM:** 0.0% | **Server-side**

### `novel_published`
- **30-day count:** 22 events | 19 distinct users
- **UTM:** 0.0% | **Server-side**

### `review_submitted`
- **30-day count:** 20 events | 13 distinct users
- **UTM:** 0.0%

### `import_request_created`
- **30-day count:** 8 events | 7 distinct users
- **UTM:** 0.0% | **Server-side**

### `report_open` / `report_submit`
- **30-day count:** 31 / 26 events | 7 / 4 distinct users
- **UTM:** 0.0% event-level | 16.1% / 19.2% person-level

### `content_flagged`
- **30-day count:** 8 events | 4 distinct users
- **UTM:** 0.0%

### `image_uploaded`
- **30-day count:** 8 events | 1 distinct user
- **UTM:** 0.0% | **Server-side**

---

## UTM Attribution Verdict Table

| Event | Count 30d | Users | Event UTM% | Person UTM% | Verdict |
|-------|----------|-------|-----------|------------|---------|
| `$set` | 5,050 | 2,881 | 80.2% | 80.2% | 🟢 GOOD |
| `novel_detail_viewed` | 26,527 | 3,998 | 72.3% | 48.8% | 🟡 PARTIAL |
| `registration_nudge_dismissed` | 197 | 159 | 41.6% | 64.5% | 🟢 GOOD |
| `registration_nudge_clicked` | 13 | 13 | 38.5% | 61.5% | 🟢 GOOD |
| `chapter_completed` | 1,382 | 270 | 36.3% | 56.5% | 🟡 PARTIAL |
| `chapter_opened` | 4,517 | 608 | 34.4% | 54.8% | 🟡 PARTIAL |
| `app_opened` | 17,864 | 4,707 | 52.7% | 39.5% | 🟡 PARTIAL |
| `share_clicked` | 25 | 16 | 16.0% | 16.0% | 🟡 PARTIAL |
| `novel_card_clicked` | 3,525 | 743 | 8.5% | 12.9% | 🟡 LOW |
| `comment_created` | 60 | 21 | 0.0% | 0.0% | 🔴 DARK |
| `user_registered` | 191 | 191 | 0.0% | 0.0% | 🔴 BROKEN |
| `chapter_published` | 205 | 20 | 0.0% | 0.0% | ⚪ N/A (server) |
| `author_profile_created` | 38 | 1 | 0.0% | 0.0% | ⚪ N/A (server) |

---

## Host Mapping

| Host | Role | Data Volume |
|------|------|-------------|
| `novelpedia.net` | Reader app — chapters, registrations, reading activity | ~170k events |
| `author.novelpedia.net` | Author dashboard — publish, author profile | ~300 events |
| `demo.novelpedia.net` | Demo/staging — negligible | ~77 events |

---

## Key Corrections to Prior Report

| Prior Claim | Verdict | Corrected Value |
|-------------|---------|----------------|
| 28 events total | ❌ Wrong | 44 events in 30 days |
| chapter_completed = 90 events, 0% UTM | ❌ Wrong | 1,382 events, 36.3% evt / 56.5% pers |
| user_registered = 5 events | ❌ Wrong | 191 events |
| share_clicked = 0 events | ❌ Wrong | 25 events, 16% UTM |
| comment_created = 0 events | ❌ Wrong | 60 events, 0% UTM |
| $identify broken | ❌ Wrong | 202 events, working |
| user_registered 0% UTM | ✅ Confirmed | Still 0% — this IS the critical bug |
