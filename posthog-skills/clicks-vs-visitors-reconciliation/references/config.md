# Configuration


## Data Sources
- A-ADS API (clicks, campaign stats)
- PostHog events API (chapter_opened, distinct_ids by UTM)

## Reconciliation Logic
Join on UTM params + date. A-ADS provides clicks per campaign/creative/date. PostHog provides distinct chapter_openers per UTM. click_to_visitor_rate = PostHog visitors / A-ADS clicks. <5% = likely bot or bad UTM. 5-20% = average. >20% = strong landing page.
