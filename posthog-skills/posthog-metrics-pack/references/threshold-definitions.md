# Threshold Definitions

> Last verified: 2026-04-29 | Based on 30-day actual data from PostHog 314999

## Critical Thresholds

| Metric | Healthy | Degraded | Critical | Current 30-day |
|--------|---------|----------|----------|---------------|
| chapter_opened / day | > 200 | 50–200 | < 50 | ~151/day avg |
| chapter_completed / day | > 50 | 15–50 | < 15 | ~46/day avg |
| user_registered / day | > 20 | 5–20 | < 5 | ~6/day avg |
| chapter_completion rate | > 40% | 25–40% | < 25% | 30.6% (1,382/4,517) |
| UTM person coverage (chapter_opened) | > 70% | 40–70% | < 40% | 54.8% 🟡 |
| UTM person coverage (chapter_completed) | > 70% | 40–70% | < 40% | 56.5% 🟡 |
| UTM person coverage (user_registered) | > 50% | 20–50% | < 20% | 0.0% 🔴 |
| comment_created / week | > 30 | 10–30 | < 10 | ~14/week 🟡 |
| share_clicked / week | > 20 | 5–20 | < 5 | ~6/week 🟡 |

## Flatline Alerts

Fire when:
- chapter_opened = 0 for 24 hours → 🔴 CRITICAL
- chapter_opened drops > 50% week-over-week → 🔴 CRITICAL
- user_registered = 0 for 48 hours → 🔴 CRITICAL
- No $pageview events for 4 hours → 🟠 WARNING

## Anomaly Detection Baselines (30-day)

| Event | 30-day total | Daily avg | SD |
|-------|------------|----------|-----|
| chapter_opened | 4,517 | 151 | TBD (needs more history) |
| chapter_completed | 1,382 | 46 | TBD |
| novel_detail_viewed | 26,527 | 884 | TBD |
| user_registered | 191 | 6 | TBD |
| app_opened | 17,864 | 595 | TBD |

**Note:** SD requires 4+ weeks of data. Currently only ~1 week of reliable history. Baselines stabilize after 4 weeks.
