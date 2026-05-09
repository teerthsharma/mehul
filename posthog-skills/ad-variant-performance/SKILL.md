---
name: ad-variant-performance
category: novelpedia
version: 4.0.0
description: "Ad creative (variant) evaluation playbook -- three-layer model for diagnosing ad quality, acquisition efficiency, and content quality. Uses BigQuery spend data + PostHog event data. Primary rank: conversion rate (completers per users), NOT cost per completion."
priority: critical
inputs:
  - campaign_slug (for Layer 1 single-campaign analysis)
  - campaign_list (for Layer 2 cross-campaign comparison)
  - date_range (7d, 14d, 30d, all-time)
outputs:
  - Creative ranking by conversion rate (spend-independent)
  - Cost per user (acquisition efficiency)
  - PostHog capture rate (Layer 2 health check)
  - Chapter open %, completion %, ch.3 % per creative
  - Decision: continue / prune / new creative / fix tracking
requires:
  - BigQuery: ads.spend_daily (impressions, clicks, cost_usd by utm_campaign/utm_content)
  - PostHog project 314999 events: dollar_pageview, chapter_opened, chapter_completed, user_registered
  - PostHog person properties: initial_utm_campaign, initial_utm_content
---

# Ad Variant Performance -- Analysis Playbook

## The Core Principle

> Never rank ads on a single metric. Cost per completion is corrupted by spend volume. Conversion rate ignores acquisition cost. CTR ignores what happens after the click. The truth lives in the intersection of all three layers.

## The Three-Layer Model

Every creative fails or succeeds at exactly one layer. Know which before deciding.

| Layer | Metrics | Failure signal | Fix |
|-------|---------|----------------|-----|
| **1. Ad quality** | CTR, impressions, CPC | Low CTR -- ad is not compelling | New creative |
| **2. Acquisition efficiency** | PostHog capture rate, cost per user | Capture rate <30% -- tracking broken | Fix UTM / PostHog wiring |
| **3. Content quality** | Chapter open %, completion %, ch.3 % | Low completion despite high opens -- novel weak | Fix novel content / first-chapter hook |

**Diagnosis rules:**
- High CTR + low chapter open -- landing page broken
- Low CTR + high completion -- novel is good, ad is weak -- new creative needed
- Low CTR + low completion -- both broken -- do not scale
- High CTR + high completion -- scale aggressively
- Capture rate <30% -- fix tracking before any spend decision

## The Ranking Rule

> **Always rank by conversion rate (completers per users), never by cost per completion.**

Cost per completion = spend divided by completers. Since completers scale with spend, high-budget creatives always look artificially good on this metric. Conversion rate is spend-independent -- it reveals true audience quality regardless of budget behind it.

Use cost per user separately to understand acquisition efficiency. The best creative has both a high conversion rate AND a low cost per user.

## Layer 1 -- Single Campaign Creative Breakdown

Compare creatives within one campaign. Replace `your-campaign` with the slug.

```sql
WITH
spend AS (
    SELECT
        utm_content AS creative,
        SUM(impressions) AS impressions,
        SUM(clicks) AS reported_clicks,
        SUM(cost_usd) AS total_cost_usd
    FROM bigquery.spend_daily
    WHERE utm_campaign = 'your-campaign'
      AND date >= CURRENT_DATE - 30
    GROUP BY utm_content
),
rm_persons AS (
    SELECT DISTINCT
        person_id,
        person.properties.initial_utm_content AS creative
    FROM events
    WHERE event = 'dollar_pageview'
      AND person.properties.initial_utm_campaign = 'your-campaign'
      AND timestamp >= now() - INTERVAL 30 DAY
),
chapter_openers AS (
    SELECT DISTINCT person_id FROM events
    WHERE event = 'chapter_opened'
      AND person.properties.initial_utm_campaign = 'your-campaign'
      AND timestamp >= now() - INTERVAL 30 DAY
),
chapter_completers AS (
    SELECT DISTINCT person_id FROM events
    WHERE event = 'chapter_completed'
      AND person.properties.initial_utm_campaign = 'your-campaign'
      AND timestamp >= now() - INTERVAL 30 DAY
),
ch3_completed AS (
    SELECT DISTINCT person_id FROM events
    WHERE event = 'chapter_completed'
      AND toInt(properties.chapter_number) = 3
      AND person.properties.initial_utm_campaign = 'your-campaign'
      AND timestamp >= now() - INTERVAL 30 DAY
),
registrations AS (
    SELECT DISTINCT person_id FROM events
    WHERE event = 'user_registered'
      AND person.properties.initial_utm_campaign = 'your-campaign'
      AND timestamp >= now() - INTERVAL 30 DAY
),
funnel AS (
    SELECT
        p.creative,
        count(DISTINCT p.person_id) AS posthog_users,
        count(DISTINCT co.person_id) AS chapter_openers,
        count(DISTINCT cc.person_id) AS chapter_completers,
        count(DISTINCT c3.person_id) AS ch3_completed,
        count(DISTINCT reg.person_id) AS registrations
    FROM rm_persons p
    LEFT JOIN chapter_openers co ON co.person_id = p.person_id
    LEFT JOIN chapter_completers cc ON cc.person_id = p.person_id
    LEFT JOIN ch3_completed c3 ON c3.person_id = p.person_id
    LEFT JOIN registrations reg ON reg.person_id = p.person_id
    GROUP BY p.creative
)
SELECT
    f.creative,
    s.impressions,
    s.reported_clicks,
    round(100.0 * s.reported_clicks / nullIf(s.impressions, 0), 3) AS ctr_pct,
    round(s.total_cost_usd, 2) AS total_cost_usd,
    f.posthog_users,
    round(s.total_cost_usd / nullIf(f.posthog_users, 0), 3) AS cost_per_user,
    round(100.0 * f.chapter_openers / nullIf(f.posthog_users, 0), 1) AS pct_opened_chapter,
    round(100.0 * f.chapter_completers / nullIf(f.posthog_users, 0), 1) AS pct_completed_chapter,
    round(100.0 * f.ch3_completed / nullIf(f.posthog_users, 0), 1) AS pct_completed_ch3,
    round(s.total_cost_usd / nullIf(f.chapter_completers, 0), 3) AS cost_per_chapter_completion,
    round(s.total_cost_usd / nullIf(f.ch3_completed, 0), 3) AS cost_per_ch3_completed,
    round(100.0 * f.posthog_users / nullIf(s.reported_clicks, 0), 1) AS posthog_capture_rate_pct
FROM spend s
LEFT JOIN funnel f ON f.creative = s.creative
ORDER BY pct_completed_chapter DESC
LIMIT 100
```

**Key columns to read:**
- `pct_completed_chapter` -- primary rank (conversion rate, spend-independent)
- `cost_per_user` -- acquisition efficiency
- `posthog_capture_rate_pct` -- if below 30%, tracking is broken; investigate before any decision
- `ctr_pct` -- Layer 1 ad quality signal
- `pct_opened_chapter` -- landing page / onboarding conversion

## Layer 2 -- Cross-Campaign Comparison

Compare two or more campaigns head-to-head. Update the `IN (...)` list with campaign slugs.

```sql
WITH
spend AS (
    SELECT
        utm_campaign AS campaign,
        utm_content AS creative,
        SUM(impressions) AS impressions,
        SUM(clicks) AS reported_clicks,
        SUM(cost_usd) AS total_cost_usd
    FROM bigquery.spend_daily
    WHERE utm_campaign IN ('campaign-a', 'campaign-b')
      AND date >= CURRENT_DATE - 30
    GROUP BY utm_campaign, utm_content
),
all_persons AS (
    SELECT DISTINCT
        person_id,
        person.properties.initial_utm_campaign AS campaign,
        person.properties.initial_utm_content AS creative
    FROM events
    WHERE event = 'dollar_pageview'
      AND person.properties.initial_utm_campaign IN ('campaign-a', 'campaign-b')
      AND timestamp >= now() - INTERVAL 30 DAY
),
chapter_completers AS (
    SELECT DISTINCT person_id FROM events
    WHERE event = 'chapter_completed'
      AND person.properties.initial_utm_campaign IN ('campaign-a', 'campaign-b')
      AND timestamp >= now() - INTERVAL 30 DAY
),
ch3_completed AS (
    SELECT DISTINCT person_id FROM events
    WHERE event = 'chapter_completed'
      AND toInt(properties.chapter_number) = 3
      AND person.properties.initial_utm_campaign IN ('campaign-a', 'campaign-b')
      AND timestamp >= now() - INTERVAL 30 DAY
),
registrations AS (
    SELECT DISTINCT person_id FROM events
    WHERE event = 'user_registered'
      AND person.properties.initial_utm_campaign IN ('campaign-a', 'campaign-b')
      AND timestamp >= now() - INTERVAL 30 DAY
),
funnel AS (
    SELECT
        p.campaign,
        p.creative,
        count(DISTINCT p.person_id) AS posthog_users,
        count(DISTINCT cc.person_id) AS chapter_completers,
        count(DISTINCT c3.person_id) AS ch3_completed,
        count(DISTINCT reg.person_id) AS registrations
    FROM all_persons p
    LEFT JOIN chapter_completers cc ON cc.person_id = p.person_id
    LEFT JOIN ch3_completed c3 ON c3.person_id = p.person_id
    LEFT JOIN registrations reg ON reg.person_id = p.person_id
    GROUP BY p.campaign, p.creative
)
SELECT
    s.campaign,
    s.creative,
    round(100.0 * s.reported_clicks / nullIf(s.impressions, 0), 3) AS ctr_pct,
    round(s.total_cost_usd, 2) AS total_cost_usd,
    f.posthog_users,
    round(s.total_cost_usd / nullIf(f.posthog_users, 0), 3) AS cost_per_user,
    round(100.0 * f.chapter_completers / nullIf(f.posthog_users, 0), 1) AS pct_completed_chapter,
    round(100.0 * f.ch3_completed / nullIf(f.posthog_users, 0), 1) AS pct_completed_ch3,
    round(s.total_cost_usd / nullIf(f.chapter_completers, 0), 3) AS cost_per_chapter_completion,
    round(s.total_cost_usd / nullIf(f.ch3_completed, 0), 3) AS cost_per_ch3_completed
FROM spend s
LEFT JOIN funnel f ON f.campaign = s.campaign AND f.creative = s.creative
ORDER BY s.campaign, pct_completed_chapter DESC
LIMIT 100
```

## Layer 3 -- All-Time Creative Ranking (Spend-Independent)

Rank every creative ever run. Primary sort = conversion rate, not cost per completion.

```sql
WITH
spend AS (
    SELECT
        utm_campaign AS campaign,
        utm_content AS creative,
        SUM(impressions) AS impressions,
        SUM(clicks) AS reported_clicks,
        SUM(cost_usd) AS total_cost_usd
    FROM bigquery.spend_daily
    WHERE utm_content IS NOT NULL AND utm_content != ''
    GROUP BY utm_campaign, utm_content
),
all_persons AS (
    SELECT DISTINCT
        person_id,
        person.properties.initial_utm_campaign AS campaign,
        person.properties.initial_utm_content AS creative
    FROM events
    WHERE event = 'dollar_pageview'
      AND person.properties.initial_utm_campaign IS NOT NULL
      AND person.properties.initial_utm_content IS NOT NULL
      AND timestamp >= now() - INTERVAL 365 DAY
),
chapter_completers AS (
    SELECT DISTINCT person_id FROM events
    WHERE event = 'chapter_completed'
      AND person.properties.initial_utm_campaign IS NOT NULL
      AND timestamp >= now() - INTERVAL 365 DAY
),
ch3_completed AS (
    SELECT DISTINCT person_id FROM events
    WHERE event = 'chapter_completed'
      AND toInt(properties.chapter_number) = 3
      AND person.properties.initial_utm_campaign IS NOT NULL
      AND timestamp >= now() - INTERVAL 365 DAY
),
registrations AS (
    SELECT DISTINCT person_id FROM events
    WHERE event = 'user_registered'
      AND person.properties.initial_utm_campaign IS NOT NULL
      AND timestamp >= now() - INTERVAL 365 DAY
),
funnel AS (
    SELECT
        p.campaign,
        p.creative,
        count(DISTINCT p.person_id) AS posthog_users,
        count(DISTINCT cc.person_id) AS chapter_completers,
        count(DISTINCT c3.person_id) AS ch3_completed,
        count(DISTINCT reg.person_id) AS registrations
    FROM all_persons p
    LEFT JOIN chapter_completers cc ON cc.person_id = p.person_id
    LEFT JOIN ch3_completed c3 ON c3.person_id = p.person_id
    LEFT JOIN registrations reg ON reg.person_id = p.person_id
    GROUP BY p.campaign, p.creative
)
SELECT
    s.campaign,
    s.creative,
    s.impressions,
    s.reported_clicks,
    round(100.0 * s.reported_clicks / nullIf(s.impressions, 0), 3) AS ctr_pct,
    round(s.total_cost_usd, 2) AS total_cost_usd,
    f.posthog_users,
    round(s.total_cost_usd / nullIf(f.posthog_users, 0), 3) AS cost_per_user,
    round(100.0 * f.chapter_completers / nullIf(f.posthog_users, 0), 1) AS pct_completed_chapter,
    round(100.0 * f.ch3_completed / nullIf(f.posthog_users, 0), 1) AS pct_completed_ch3,
    round(100.0 * f.posthog_users / nullIf(s.reported_clicks, 0), 1) AS posthog_capture_rate_pct
FROM spend s
LEFT JOIN funnel f ON f.campaign = s.campaign AND f.creative = s.creative
WHERE f.posthog_users > 0
ORDER BY pct_completed_chapter DESC, pct_completed_ch3 DESC
LIMIT 500
```

## Layer 4 -- Low-Volume Deep Dive (Ad vs. Novel Diagnosis)

Use when a creative has low tracked users (<50) to diagnose which layer is broken.

```sql
WITH
spend AS (
    SELECT
        utm_campaign AS campaign,
        utm_content AS creative,
        SUM(impressions) AS impressions,
        SUM(clicks) AS reported_clicks,
        SUM(cost_usd) AS total_cost_usd
    FROM bigquery.spend_daily
    WHERE utm_campaign IN ('campaign-a', 'campaign-b', 'campaign-c')
    GROUP BY utm_campaign, utm_content
),
all_persons AS (
    SELECT DISTINCT
        person_id,
        person.properties.initial_utm_campaign AS campaign,
        person.properties.initial_utm_content AS creative
    FROM events
    WHERE event = 'dollar_pageview'
      AND person.properties.initial_utm_campaign IN ('campaign-a', 'campaign-b', 'campaign-c')
      AND timestamp >= now() - INTERVAL 365 DAY
),
chapter_openers AS (
    SELECT DISTINCT person_id FROM events
    WHERE event = 'chapter_opened'
      AND person.properties.initial_utm_campaign IN ('campaign-a', 'campaign-b', 'campaign-c')
      AND timestamp >= now() - INTERVAL 365 DAY
),
chapter_completers AS (
    SELECT DISTINCT person_id FROM events
    WHERE event = 'chapter_completed'
      AND person.properties.initial_utm_campaign IN ('campaign-a', 'campaign-b', 'campaign-c')
      AND timestamp >= now() - INTERVAL 365 DAY
),
ch3_completed AS (
    SELECT DISTINCT person_id FROM events
    WHERE event = 'chapter_completed'
      AND toInt(properties.chapter_number) = 3
      AND person.properties.initial_utm_campaign IN ('campaign-a', 'campaign-b', 'campaign-c')
      AND timestamp >= now() - INTERVAL 365 DAY
),
funnel AS (
    SELECT
        p.campaign,
        p.creative,
        count(DISTINCT p.person_id) AS posthog_users,
        count(DISTINCT co.person_id) AS chapter_openers,
        count(DISTINCT cc.person_id) AS chapter_completers,
        count(DISTINCT c3.person_id) AS ch3_completed
    FROM all_persons p
    LEFT JOIN chapter_openers co ON co.person_id = p.person_id
    LEFT JOIN chapter_completers cc ON cc.person_id = p.person_id
    LEFT JOIN ch3_completed c3 ON c3.person_id = p.person_id
    GROUP BY p.campaign, p.creative
)
SELECT
    s.campaign,
    s.creative,
    s.impressions,
    s.reported_clicks,
    round(s.total_cost_usd, 2) AS total_cost_usd,
    round(100.0 * s.reported_clicks / nullIf(s.impressions, 0), 3) AS ctr_pct,
    round(s.total_cost_usd / nullIf(s.reported_clicks, 0), 3) AS cost_per_click,
    f.posthog_users,
    round(100.0 * f.posthog_users / nullIf(s.reported_clicks, 0), 1) AS posthog_capture_rate_pct,
    round(100.0 * f.chapter_openers / nullIf(f.posthog_users, 0), 1) AS pct_opened_chapter,
    round(100.0 * f.chapter_completers / nullIf(f.posthog_users, 0), 1) AS pct_completed_chapter,
    round(100.0 * f.ch3_completed / nullIf(f.posthog_users, 0), 1) AS pct_completed_ch3
FROM spend s
LEFT JOIN funnel f ON f.campaign = s.campaign AND f.creative = s.creative
ORDER BY s.campaign, pct_completed_chapter DESC
LIMIT 100
```

## Decision Matrix

| Situation | Action |
|-----------|--------|
| Conversion rate high + cost per user competitive + CTR healthy | **Continue** (hold spend) |
| Conversion rate average, not enough volume yet, no red flags | **Continue** (gather more signal) |
| Conversion rate below average consistently with 50+ users | **Prune** (stop spending) |
| Low CTR but strong completion rates | **New creative** (novel works, ad does not -- do not kill campaign) |
| Capture rate <30% | **Fix tracking first** -- do not make spend decisions on bad data |
| Under 30 tracked users | **Wait** -- too noisy, not enough signal |

## The Inference Engine -- Diagnosing Which Component is Broken

Every underperforming creative has exactly one root cause. Your job is to identify which of the three components is failing, then apply the right fix. Fixing the wrong component wastes budget.

### The Diagnostic Matrix

Use this 2x2 grid with the four key ratios to pinpoint the failure:

```
                        LOW CTR (Layer 1 broken)
                      /                          \
HIGH Conv. Rate  ----|  Novel is PROVEN GOOD    |  ABANDON -- ad is
(Layer 3 works)        Keep the novel,             terrible AND novel
                       fix the ad format           won't convert
                       (new creative needed)       (kill campaign)
                      \
                       LOW Conv. Rate (Layer 3 broken)
                      /                          \
HIGH CTR          ----|  ABANDON -- novel has     |  ABANDON -- both
(Layer 1 works)       no hook despite             components are
                      strong traffic              broken (kill
                       (fix novel content)        campaign)
                      \
                    HIGH CTR + HIGH Conv. Rate
                         SCALE AGGRESSIVELY
```

### The Three Failure Modes

**Failure Mode 1 -- The Ad is Broken, The Novel is Good**

Signs:
- CTR is low or below campaign average
- BUT conversion rate (completers per users) is high relative to other creatives
- Capture rate is healthy (>30%)

Interpretation: The novel hooked everyone who arrived. The problem is attracting the right people to click in the first place.

Action: **Keep the novel. Replace the ad creative.** The current ad is filtering out the right audience or not being compelling enough. Test new images, copy, formats, or targeting.

Example from live session: `reader-mage/static-v3` had 0.05% CTR (worst) but 4.2% conversion rate (best) -- novel is proven, ad needs replacement.

---

**Failure Mode 2 -- The Novel is Broken, The Ad is Good**

Signs:
- CTR is healthy (at or above average for the platform/campaign)
- BUT conversion rate is low -- users click, open chapters, then leave
- Ch.1 completion is high but Ch.3 is 0 or near-zero

Interpretation: The ad is working. It attracts the right audience and earns the click. But the novel fails to hold readers past the first chapter.

Action: **Keep the ad format. Fix the novel's first-chapter hook and pacing.** Do not increase budget until ch.3 completion improves.

Example from live session: `self-summoning-demon/gif-v2` had 0.11% CTR (strong) but only 2.0% conversion -- 17 users opened chapters, only 3 completed, 0 reached ch.3. Novel hook is broken.

---

**Failure Mode 3 -- Both Are Broken**

Signs:
- CTR is low
- Conversion rate is low or zero
- Either zero tracked users despite spend, or capture rate <30%

Interpretation: Either the ad is attracting the wrong audience AND the novel has no hook, OR there is a tracking/wiring problem making data unreliable.

Action: **ABANDON. Do not scale.** Fix the UTM wiring first (verify capture rate >30%). Then retest with a new creative/novel combination before spending again.

---

**Failure Mode 4 -- Scale Aggressively**

Signs:
- CTR is at or above platform average
- Conversion rate is high
- CPA is competitive or improving with volume

Action: **Scale the budget.** The creative combination is working on all three layers. Increase spend until CPA starts degrading or conversion rate drops.

---

### CPA vs Conversion Rate Decision Guide

| Metric | Budget-Corrupted? | Best Use |
|--------|-------------------|----------|
| Cost per completion (CPA) | YES -- high-spend creatives always look better | Reporting to investors |
| Conversion rate (completers per users) | NO -- spend-independent | Creative ranking and decisions |

Always rank by conversion rate. Use CPA to judge acquisition efficiency only after filtering to creatives with at least 30 tracked users and healthy capture rates.

---

## Red Flags Checklist

Run through before any spend decision:

- [ ] PostHog capture rate above 30%? If not, investigate tracking before drawing conclusions
- [ ] UTM campaign name formatted correctly and consistently? (check for typos like `self-summoning-gif-v2`)
- [ ] At least 30 tracked users per creative? Below that, conversion rates are too noisy
- [ ] Ranking by conversion rate (completers per users), not cost per completion?
- [ ] Comparing creatives within the same campaign first? (different novels attract different audiences)
- [ ] Ch.3 rate driven by real volume or a single user in a tiny sample?
- [ ] Is CTR healthy for the platform? (compare against own historical CTR, not across campaigns)

## Known A-ADS Variants (Reference)

| Campaign | Variants |
|----------|----------|
| `reader-mage` | static-v3 (high volume), trial-static-v1 |
| `self-summoning-demon` | gif-v2 (clear winner), gif-v1, gif-v3 |
| `gu-demon-king` | gif-v1, static-v1 |
| `weakest-kobold` | static-v1 |
| `inertia-beneath-starlit-veil` | trial-static-v1 |
| `unmade` | static-v1 |

**Campaign name mapping for JOIN**: `self-summoning-gif-v2` (A-ADS/BigQuery) maps to `self-summoning-demon` (PostHog events) -- this is a literal exception. All others use regex strip of `__.*$` suffix.

---

## Live Session Examples (Reference)

These are real diagnoses from live analysis sessions to illustrate how to apply the Inference Engine.

### reader-mage / static-v3 (12h snapshot)
- CTR: 0.05% (worst of all active)
- CPA: $4.68 (highest -- 4x weakest-kobold)
- Conversion rate: 4.2% (best -- novel is proven good)
- **Diagnosis: Failure Mode 1 -- The Ad is Broken, The Novel is Good**
- **Action: Keep novel. Replace ad creative. Do not kill campaign.**

### self-summoning-demon / gif-v2 (12h snapshot)
- CTR: 0.11% (strong -- ad is working)
- CPA: $1.42
- Conversion rate: 2.0% (low -- novel loses readers after ch.1)
- Ch.3 completions: 0 (no one is getting hooked past ch.1)
- **Diagnosis: Failure Mode 2 -- The Novel is Broken, The Ad is Good**
- **Action: Keep ad format. Fix novel's first-chapter hook. Do not increase budget.**

### weakest-kobold / static-v1 (12h snapshot)
- CTR: 0.10% (solid)
- CPA: $1.06 (cheapest completion of all)
- Conversion rate: 3.6% (real signal with n=83)
- Ch.3 completions: 1
- **Diagnosis: Failure Mode 4 -- Scale Aggressively**
- **Action: Increase budget. Best efficiency + proven novel.**

### gu-demon-king / static-v1 (12h snapshot)
- CTR: 0.13% (best ad quality)
- CPA: $1.94
- Conversion rate: 1.2% (worst of all active)
- **Diagnosis: Failure Mode 2 -- The Novel is Broken**
- **Action: Novel not holding readers. Fix content or replace.**

### gu-demon-king / gif-v1 (12h snapshot)
- CTR: 0.04% (worst CTR)
- Conversion rate: 3.3% (decent but n=30)
- CPA: $2.17 (second highest)
- **Diagnosis: Failure Mode 1 -- The Ad is Broken, Novel is OK**
- **Action: Replace ad creative. Novel has some signal.**

## Execution Steps

1. Identify the campaign slug(s) to analyze
2. Pick the right Layer query (1-4) based on scope:
   - Layer 1: single campaign, which creative wins?
   - Layer 2: 2+ campaigns, compare head-to-head
   - Layer 3: all-time ranking of everything ever run
   - Layer 4: low volume creative, is it ad or novel?
3. Run in BigQuery (PostHog native queries option available)
4. Cross-reference with PostHog dashboards: `1458292` (reader_app), `1458291` (author_app)
5. Apply the decision matrix
6. Record decision and rationale in campaign doc

## Pitfalls

- **Never compare cross-campaign conversion rates directly** -- different novels attract different audiences; compare within campaign first
- **Cost per completion is budget-corrupted** -- always use conversion rate as primary rank
- **Capture rate <30% means data is unreliable** -- fix UTM wiring before making decisions
- **Small samples lie** -- wait for 30+ tracked users before drawing conclusions
- **Ch.3 is a milestone, not a vanity metric** -- high ch.3 rate means readers are genuinely hooked
- **ALWAYS label the funnel stage for every CPA metric** -- mixing funnel stages across campaigns (e.g., comparing cost-per-chapter-opened for one campaign against cost-per-completed-chapter for another) produces meaningless comparisons. Every CPA number must specify its stage: click, visitor, chapter-opened, chapter-completed, registered.

## Output Format -- MANDATORY

When presenting ad performance results, always use this exact format so comparisons are unambiguous:

```
| Metric                    | Campaign A | Campaign B | Winner |
|---------------------------|-----------|-----------|--------|
| A-ADS Spend               | $X.XX     | $X.XX     | ...    |
| Impressions               | X         | X         | ...    |
| Clicks                    | X         | X         | ...    |
| CPC                       | $X.XXX    | $X.XXX    | Tie    |
| PostHog Visitors          | X         | X         | ...    |
| Chapter Opens             | X         | X         | ...    |
| Chapter Completions        | X         | X         | ...    |
| CPA per Visitor           | $X.XX     | $X.XX     | ...    |
| CPA per Chapter Opened    | $X.XX     | $X.XX     | ...    |  <-- LABEL THIS
| CPA per Completed Chapter | $X.XX     | $X.XX     | ...    |  <-- LABEL THIS
| Conversion Rate (completers/visitors) | X% | X% | ... |  <-- LABEL THIS
| Ch.3 Completions           | X         | X         | ...    |
```

> **Critical:** CPA per chapter opened and CPA per completed chapter are DIFFERENT metrics. Comparing one campaign's chapter-opened CPA against another's completed-chapter CPA is meaningless. Always compare the same stage across campaigns.

**Verdict must state:** Which funnel stage was used to rank the winner, and why that stage is the right one for the business goal.


---

## Execution: API Access Methods

### Method 1 -- PostHog MCP (HogQL + BigQuery) -- PREFERRED FOR SPEND DATA

Use when you need cost data from BigQuery (`ads.spend_daily`) joined with PostHog events.

The PostHog MCP (`mcp.posthog.com`) requires session initialization via SSE transport:

```python
import urllib.request, json, re

API_KEY = "phx_HBorvUARpdZwGBNBuCuTmjnBoRetfHTc4ELdvD5f9pjrECAc"
MCP_URL = "https://mcp.posthog.com/mcp"

def mcp_init():
    init_payload = json.dumps({
        "jsonrpc": "2.0", "method": "initialize",
        "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                   "clientInfo": {"name": "hermes", "version": "1.0"}}, "id": 1
    }).encode()
    req = urllib.request.Request(MCP_URL, data=init_payload,
        headers={"Authorization": f"Bearer {API_KEY}",
                 "Content-Type": "application/json",
                 "Accept": "application/json, text/event-stream"},
        method="POST")
    with urllib.request.urlopen(req, timeout=15) as resp:
        # SSE response -- read until session ID appears
        body = resp.read().decode()
        sid = re.search(r'"Mcp-Session-Id"\s*:\s*"([^"]+)"', body)
        return sid.group(1) if sid else None

session_id = mcp_init()
```

**Known issue:** If `mcp_init()` returns `None`, the MCP SSE transport is failing in this environment. Do NOT fall back to simple JSON parsing -- the session ID is embedded in SSE stream data. Move to Method 2.

### Method 2 -- PostHog REST API (Events endpoint) -- FALLBACK / NO BIGQUERY

Use when MCP fails or when BigQuery spend data is unavailable. This was the primary method used in a live session when MCP session establishment failed (SSE transport issue in hermes-agent sandbox).

```python
import urllib.request, json
from collections import defaultdict

API_KEY = "phx_HBorvUARpdZwGBNBuCuTmjnBoRetfHTc4ELdvD5f9pjrECAc"
BASE = "https://app.posthog.com/api/projects/314999"

EVENTS = ["$pageview", "chapter_opened", "chapter_completed"]

all_events = {}
for ev in EVENTS:
    events = []
    url = f"{BASE}/events/?event={ev}&limit=50000&after=-12h"
    while url:
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {API_KEY}"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
        events.extend(data.get('results', []))
        url = data.get('next')  # SSE streaming URL -- follow for pagination

# distinct_id is the user identifier across events
visitors = defaultdict(set)        # (campaign, creative) -> set of distinct_ids
chapter_openers = defaultdict(set)
chapter_completers = defaultdict(set)
ch3_completers = defaultdict(set)

for e in all_events["$pageview"]:
    p = e.get("properties", {})
    campaign = p.get("utm_campaign"); content = p.get("utm_content"); did = e.get("distinct_id")
    if campaign and content and did:
        visitors[(campaign, content)].add(did)

for e in all_events["chapter_opened"]:
    p = e.get("properties", {})
    campaign = p.get("utm_campaign"); content = p.get("utm_content"); did = e.get("distinct_id")
    if campaign and did:
        chapter_openers[(campaign, content)].add(did)

for e in all_events["chapter_completed"]:
    p = e.get("properties", {})
    campaign = p.get("utm_campaign"); content = p.get("utm_content"); did = e.get("distinct_id")
    ch_num = p.get("chapter_number")
    if campaign and did:
        chapter_completers[(campaign, content)].add(did)
        if str(ch_num) == "3":
            ch3_completers[(campaign, content)].add(did)
```

**Limitation:** REST API has no access to BigQuery `ads.spend_daily`. Spend data (cost per user, cost per completion) requires BigQuery credentials. Without spend data, conversion rate (completers per users) is the only rankable metric -- this is still valid for creative comparison but does not support absolute CPA decisions.

### BigQuery Access (Required for Spend Data)

To run Layer 1-4 queries with cost data, BigQuery credentials are needed:
- GCP service account with `bigquery.dataViewer` on project `novelpedia-prod`
- Or `gcloud auth application-default-login` with ADC on the host machine
- The auth-dash workspace at `workspace/auth-dash/` has the infra but no `.env` with BQ credentials in the profile directory

Without BigQuery: run REST API method, report conversion rates only, flag that spend decisions require cost data.
