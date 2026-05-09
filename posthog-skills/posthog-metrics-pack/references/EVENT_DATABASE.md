# EVENT_DATABASE.md — Novelpedia PostHog Ground Truth
> **Period:** 30 days | **Total events:** 206,489 | **Distinct users:** 5,405 | **Event types:** 44
> **Last verified:** 2026-04-29 | **Status:** ✓ VERIFIED — all counts from live PostHog data

## ⚠️ Critical Bugs (Fix Before Next Campaign)
| # | Event | Event UTM% | Person UTM% | Unattributed | Severity | Fix |
|---|-------|-----------|------------|--------------|----------|-----|
| 1 | `user_registered` | 0.0% | 0.0% | 100% | 🔴 CRITICAL | Persist UTM on first $pageview (incl. anonymous) |
| 2 | `chapter_completed` | 36.3% | 56.5% | 43.5% | 🟡 WARNING | Same — close anonymous session UTM gap |
| 3 | `chapter_opened` | 34.4% | 54.8% | 45.2% | 🟡 WARNING | Same — ensure $identify called with $initial_utm_* |
| 4 | `comment_created` | 0.0% | 0.0% | 100% | 🟡 WARNING | Author dopamine signal dark — same fix |

## Key Correction to Prior Report
- Prior report claimed **28 events**. **CORRECTED: 44 events** in the last 30 days.
- Prior report claimed **chapter_completed = 90 events, 0% UTM**. **CORRECTED: 1,382 events, 36.3% event UTM / 56.5% person UTM.**
- Prior report claimed **user_registered = 5 events**. **CORRECTED: 191 events.**
- Prior report claimed **share_clicked = 0 events**. **CORRECTED: 25 events, 16% event UTM.**
- Prior report claimed **comment_created = 0 events**. **CORRECTED: 60 events, 0% UTM at both levels.**
- Prior report claimed **$identify broken**. **CORRECTED: 202 events, actively working.**

## UTM Attribution Summary
> **Event UTM%** = UTM parameters attached directly to the event. **Person UTM%** = first-touch UTM persisted to the person profile via $set/$identify.
> **Gap** = Person% minus Event%. A positive gap means UTM was captured on first visit but not re-attached to later events.

| Event | Count 30d | Users | Event UTM% | Person UTM% | Gap | Tier | Verdict |
|-------|----------|-------|-----------|------------|-----|------|---------|
| `$autocapture` | 62,172 | 2,659 | 13.6% | 17.0% | +3.4pp | ⚪ INFO | ⚪ LOW |
| `$pageview` | 39,741 | 5,405 | 21.2% | 24.4% | +3.2pp | ⚪ INFO | ⚪ LOW |
| `novel_detail_viewed` | 26,527 | 3,998 | 72.3% | 48.8% | -23.5pp | 🟡 WARNING | 🟡 PARTIAL |
| `app_opened` | 17,864 | 4,707 | 52.7% | 39.5% | -13.2pp | 🟡 WARNING | 🟡 PARTIAL |
| `$web_vitals` | 15,216 | 3,549 | 25.7% | 29.2% | +3.5pp | ⚪ INFO | ⚪ LOW |
| `$pageleave` | 9,219 | 4,407 | 40.2% | 34.0% | -6.2pp | 🟡 WARNING | 🟡 PARTIAL |
| `$set` | 5,050 | 2,881 | 80.2% | 80.2% | — | 🟢 HEALTHY | 🟢 GOOD |
| `$exception` | 4,533 | 3,595 | 4.0% | 4.7% | +0.7pp | 🟡 WARNING | 🟡 DARK |
| `chapter_opened` | 4,517 | 608 | 34.4% | 54.8% | +20.4pp | 🟢 HEALTHY | 🟢 GOOD |
| `novel_card_clicked` | 3,525 | 743 | 8.5% | 12.9% | +4.4pp | ⚪ INFO | ⚪ LOW |
| `carousel_clicked` | 2,308 | 612 | 9.0% | 15.0% | +6.0pp | ⚪ INFO | ⚪ LOW |
| `streak_milestone_reached` | 1,731 | 319 | 3.0% | 11.0% | +8.0pp | ⚪ INFO | ⚪ LOW |
| `chapter_completed` | 1,382 | 270 | 36.3% | 56.5% | +20.2pp | 🟢 HEALTHY | 🟢 GOOD |
| `install_prompt_shown` | 1,191 | 1,153 | 41.9% | 39.3% | -2.6pp | 🟡 WARNING | 🟡 PARTIAL |
| `$rageclick` | 723 | 282 | 14.8% | 16.2% | +1.4pp | ⚪ INFO | ⚪ LOW |
| `registration_nudge_shown` | 659 | 210 | 23.8% | 53.1% | +29.3pp | 🟢 HEALTHY | 🟢 GOOD |
| `install_prompt_dismissed` | 207 | 206 | 21.7% | 17.4% | -4.3pp | ⚪ INFO | ⚪ LOW |
| `chapter_published` | 205 | 20 | 0.0% | 0.0% | — | 🟡 WARNING | 🟡 DARK |
| `$identify` | 202 | 116 | 1.5% | 1.5% | — | 🟡 WARNING | 🟡 DARK |
| `profile_completed` | 198 | 197 | 0.0% | 1.5% | +1.5pp | 🟡 WARNING | 🟡 DARK |
| `registration_nudge_dismissed` | 197 | 159 | 41.6% | 64.5% | +22.9pp | 🟢 HEALTHY | 🟢 GOOD |
| `user_registered` | 191 | 191 | 0.0% | 0.0% | — | 🔴 CRITICAL | 🔴 BROKEN |
| `notification_clicked` | 153 | 35 | 0.0% | 3.3% | +3.3pp | 🟡 WARNING | 🟡 DARK |
| `reply_click` | 63 | 16 | 6.3% | 7.9% | +1.6pp | ⚪ INFO | ⚪ LOW |
| `comment_created` | 60 | 21 | 0.0% | 0.0% | — | 🟡 WARNING | 🟡 DARK |
| `install_completed` | 54 | 34 | 9.3% | 18.5% | +9.2pp | ⚪ INFO | ⚪ LOW |
| `reply_submit_success` | 46 | 13 | 4.3% | 6.5% | +2.2pp | ⚪ INFO | ⚪ LOW |
| `install_prompt_clicked` | 39 | 38 | 2.6% | 2.6% | — | ⚪ INFO | ⚪ LOW |
| `author_profile_created` | 38 | 1 | 0.0% | 0.0% | — | ⚪ INFO | ⚪ LOW |
| `user_identified` | 38 | 1 | 0.0% | 0.0% | — | ⚪ INFO | ⚪ LOW |
| `report_open` | 31 | 7 | 0.0% | 16.1% | +16.1pp | ⚪ INFO | ⚪ LOW |
| `report_submit` | 26 | 4 | 0.0% | 19.2% | +19.2pp | ⚪ INFO | ⚪ LOW |
| `share_clicked` | 25 | 16 | 16.0% | 16.0% | — | ⚪ INFO | ⚪ LOW |
| `novel_created` | 25 | 21 | 0.0% | 0.0% | — | ⚪ INFO | ⚪ LOW |
| `novel_published` | 22 | 19 | 0.0% | 0.0% | — | ⚪ INFO | ⚪ LOW |
| `review_submitted` | 20 | 13 | 0.0% | 0.0% | — | ⚪ INFO | ⚪ LOW |
| `novel_followed` | 19 | 13 | 0.0% | 0.0% | — | ⚪ INFO | ⚪ LOW |
| `registration_nudge_clicked` | 13 | 13 | 38.5% | 61.5% | +23.0pp | 🟢 HEALTHY | 🟢 GOOD |
| `import_request_created` | 8 | 7 | 0.0% | 0.0% | — | ⚪ INFO | ⚪ LOW |
| `content_flagged` | 8 | 4 | 0.0% | 0.0% | — | ⚪ INFO | ⚪ LOW |
| `image_uploaded` | 8 | 1 | 0.0% | 0.0% | — | ⚪ INFO | ⚪ LOW |
| `thread_collapse_toggle` | 4 | 2 | 50.0% | 100.0% | +50.0pp | 🟢 HEALTHY | 🟢 GOOD |
| `reply_submit_fail` | 1 | 1 | 100.0% | 100.0% | — | 🟢 HEALTHY | 🟢 GOOD |

## Author-Side Events (Server-Instrumented)

| Event | Count 30d | Users | Event UTM% | Person UTM% |
|-------|----------|-------|-----------|------------|
| `chapter_published` | 205 | 20 | 0.0% | 0.0% |
| `author_profile_created` | 38 | 1 | 0.0% | 0.0% |
| `user_identified` | 38 | 1 | 0.0% | 0.0% |
| `report_open` | 31 | 7 | 0.0% | 16.1% |
| `report_submit` | 26 | 4 | 0.0% | 19.2% |
| `novel_created` | 25 | 21 | 0.0% | 0.0% |
| `novel_published` | 22 | 19 | 0.0% | 0.0% |
| `review_submitted` | 20 | 13 | 0.0% | 0.0% |
| `import_request_created` | 8 | 7 | 0.0% | 0.0% |
| `content_flagged` | 8 | 4 | 0.0% | 0.0% |
| `image_uploaded` | 8 | 1 | 0.0% | 0.0% |

## Reader Engagement Events

| Event | Count 30d | Users | Event UTM% | Person UTM% |
|-------|----------|-------|-----------|------------|
| `streak_milestone_reached` | 1,731 | 319 | 3.0% | 11.0% |
| `registration_nudge_shown` | 659 | 210 | 23.8% | 53.1% |
| `registration_nudge_dismissed` | 197 | 159 | 41.6% | 64.5% |
| `notification_clicked` | 153 | 35 | 0.0% | 3.3% |
| `reply_click` | 63 | 16 | 6.3% | 7.9% |
| `comment_created` | 60 | 21 | 0.0% | 0.0% |
| `reply_submit_success` | 46 | 13 | 4.3% | 6.5% |
| `share_clicked` | 25 | 16 | 16.0% | 16.0% |
| `novel_followed` | 19 | 13 | 0.0% | 0.0% |
| `registration_nudge_clicked` | 13 | 13 | 38.5% | 61.5% |
| `reply_submit_fail` | 1 | 1 | 100.0% | 100.0% |

## Campaign Distribution (Person-Level UTM, 30 days)

| Campaign | Events 30d | Unique Users |
|----------|-----------|-------------|
| `self-summoning-demon` | 34,263 | 1,900 |
| `reader-mage` | 5,537 | 367 |
| `unmade` | 4,975 | 286 |
| `gu-demon-king` | 4,187 | 246 |
| `weakest-kobold` | 3,090 | 176 |
| `failed-hero-journey` | 1,792 | 167 |
| `inertia-beneath-starlit-veil` | 1,118 | 83 |
| `origins-of-blood` | 408 | 34 |
| `arc-of-the-souls` | 277 | 23 |
| `novelpedia` | 1,041 | 14 |
| `Illusia MOU` | 138 | 3 |
| `novelpedia-launch` | 411 | 2 |

## UTM Source Distribution (Person-Level, 30 days)

| Source | Events 30d | Unique Users |
|--------|-----------|-------------|
| `aads-novelfire` | 56,449 | 2,782 | 27.3% |
| `findnovel` | 239 | 22 | 0.1% |
| `Illusia` | 138 | 3 | 0.1% |
| `aads-freewebnovel` | 411 | 2 | 0.2% |
| `summer` | 270 | 1 | 0.1% |

## Country Distribution (Top 30, 30 days)

| Country | Events 30d | Users | Tier |
|---------|-----------|------|------|
| United States | 61,314 | 2,825 | 🟢 TIER_1 |
| India | 34,404 | 714 | 🟢 TIER_1 |
| United Kingdom | 9,640 | 466 | 🟢 TIER_1 |
| Brazil | 8,180 | 205 | 🟡 TIER_2 |
| Nigeria | 5,198 | 105 | 🟡 TIER_2 |
| Canada | 4,260 | 123 | 🟡 TIER_2 |
| Philippines | 4,062 | 135 | 🟡 TIER_2 |
| Germany | 4,889 | 190 | 🟡 TIER_2 |
| Netherlands | 10,332 | 77 | 🟡 TIER_2 |
| Singapore | 1,604 | 101 | 🟡 TIER_2 |
| Indonesia | 1,791 | 99 | 🟡 TIER_2 |
| Australia | 2,204 | 42 | 🟠 TIER_3 |
| Vietnam | 2,571 | 62 | 🟡 TIER_2 |
| Malaysia | 1,621 | 49 | 🟠 TIER_3 |
| Nepal | 2,082 | 44 | 🟠 TIER_3 |
| South Africa | 1,550 | 38 | 🟠 TIER_3 |
| Bangladesh | 1,310 | 38 | 🟠 TIER_3 |
| Pakistan | 683 | 35 | 🟠 TIER_3 |
| France | 1,145 | 34 | 🟠 TIER_3 |
| Poland | 739 | 34 | 🟠 TIER_3 |
| Ghana | 1,199 | 31 | 🟠 TIER_3 |
| Sweden | 1,659 | 30 | 🟠 TIER_3 |
| Spain | 1,104 | 29 | 🟠 TIER_3 |
| Montenegro | 3,113 | 28 | 🟠 TIER_3 |
| Portugal | 1,551 | 28 | 🟠 TIER_3 |
| Egypt | 1,089 | 27 | 🟠 TIER_3 |
| Israel | 493 | 25 | 🟠 TIER_3 |
| United Arab Emirates | 260 | 24 | 🟠 TIER_3 |
| Italy | 1,092 | 22 | 🟠 TIER_3 |
| Kenya | 421 | 17 | 🔴 TIER_4 |

## Host Mapping

| Host | Role | Events in DB |
|------|------|-------------|
| `novelpedia.net` | Reader app — chapters, registrations, reading activity | ~170k |
| `author.novelpedia.net` | Author dashboard — publish, author profile | ~300 |
| `demo.novelpedia.net` | Demo/staging — negligible (~77 events, excluded from primary metrics) | ~77 |
