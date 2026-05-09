# North-Star Metrics

> Last verified: 2026-04-29 | Source: PostHog project 314999 (30-day full pull)

## The One North-Star

**`chapter_opened`** = read = active user = WAU = DAU = MAU

Every metric that matters traces back to a user opening a chapter. Registrations without reads are vanity. Clicks without chapters are noise.

---

## 1. chapter_activation_rate

**Definition:** % of registered users who open at least 1 chapter within 7 days of registration.

**Query:**
```python
# Numerator: distinct users with chapter_opened within 7d of registration
# Denominator: distinct users with user_registered in the same period
# Use person properties: user_id, registration_date, first_chapter_date
```

**Target:** > 40% within 7 days of registration.

**Why it matters:** Registration is free. Getting someone to read is the entire game.

**Current (30-day):** 191 registrations / 608 chapter_opened users — exact activation rate requires joining on user_id across both events.

---

## 2. binge_reader_core

**Definition:** % of chapter_openers who complete 5+ chapters within a single session.

**Query:**
```python
# Session = same distinct_id within 30-minute gap
# Binge = 5+ chapter_completed events in one session
# Divided by all chapter_openers
```

**Target:** > 20% of readers reach chapter 5.

**Current (30-day):** chapter_opened = 4,517 events / 608 users; chapter_completed = 1,382 / 270 users.

---

## 3. WAU / DAU / MAU

**`chapter_opened` = north-star for all three.**

| Metric | Query | Current 30-day |
|--------|-------|---------------|
| WAU | Distinct users with chapter_opened in any 7-day window | 608 distinct users with chapter_opened |
| DAU | Distinct users with chapter_opened in a single day | Needs daily breakdown query |
| MAU | Distinct users with chapter_opened in 30-day window | 608 distinct users |

**⚠️ `app_opened` is NOT the north-star.** It fires on PWA launch — a technical event, not a reading event. Always use `chapter_opened` for active user counts.

---

## 4. registration_rate

**Definition:** % of chapter_openers who complete `user_registered`.

**Current (30-day):**
- chapter_openers: 608 distinct users
- user_registered: 191 distinct users
- Implied registration rate: 191/608 = 31.4%

**⚠️ BROKEN:** user_registered has 0% UTM. Cannot attribute registrations to campaigns. This is the critical gap.

---

## 5. active_user_definition

**Official definition:** A Novelpedia **active user** = a distinct browser/device (`distinct_id`) with at least one `chapter_opened` event within the measurement window.

- WAU = distinct active users in any 7-day rolling window
- DAU = distinct active users in a single calendar day
- MAU = distinct active users in a 30-day month

**Event to measure:** `chapter_opened` — NOT `app_opened`, NOT `novel_detail_viewed`.

---

## UTM Attribution on North-Star Events

| Event | Event UTM% | Person UTM% | Gap | Status |
|-------|-----------|------------|-----|--------|
| chapter_opened | 34.4% | 54.8% | +20.4pp | 🟡 PARTIAL |
| chapter_completed | 36.3% | 56.5% | +20.2pp | 🟡 PARTIAL |
| user_registered | 0.0% | 0.0% | — | 🔴 BROKEN |
| novel_detail_viewed | 72.3% | 48.8% | −23.5pp | 🟡 PARTIAL |

**Key insight:** Person UTM is higher than event UTM for reading events — UTM was captured on first visit but not re-attached to subsequent chapter events. This is the anonymous session UTM gap.
