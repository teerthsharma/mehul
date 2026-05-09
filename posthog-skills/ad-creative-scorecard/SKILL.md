---
name: ad-creative-scorecard
category: novelpedia
version: 1.0.0
description: "Ad creative performance scorecard with full funnel metrics -- CPC, CPA per chapter opened, CPA per chapter completed, CPA per ch.3 reached, and conversion rates. Replaces informal per-session analysis with a standardized table format for comparing campaigns and creatives."
priority: critical
inputs:
  - A-ADS spend data (spend, impressions, clicks by campaign)
  - PostHog funnel data (visitors, chapter_opened, chapter_completed, ch.3_completed by campaign/creative)
  - date_range for the analysis window
outputs:
  - Standardized scorecard table with all 8 metrics per creative
  - Ranked verdict per creative (scale / hold / prune)
  - Layer diagnosis (ad broken vs novel broken)
requires:
  - A-ADS platform data (spend, impressions, clicks per campaign/creative)
  - PostHog Events API (distinct_id sets for $pageview, chapter_opened, chapter_completed, chapter_completed where chapter_number=3)
  - API key for PostHog project 314999
---

# Ad Creative Scorecard

## What This Skill Does

Produces a standardized, comparable scorecard for any set of ad creatives. Every metric is computed at the correct funnel stage, with no mixing of layers. This is the canonical output format for any ad performance question.

## The Standard Scorecard Table

Every analysis session should produce this exact table format:

```
| Creative     | Spend | Clicks | CPC    | Visitors | Ch.Opened | Ch.Opened CPA | Ch.Completed | Ch.Comp CPA | Ch.3 Reached | Ch.3 CPA | Conv.Rate | Verdict |
|--------------|-------|--------|--------|----------|-----------|---------------|--------------|-------------|--------------|----------|-----------|---------|
| weakest-kobold/static-v1 | $3.52 | 383 | $0.009 | 88 | 8 | $0.44 | 3 | $1.17 | 1 | $3.52 | 3.4% | SCALE |
| self-summoning-demon/gif-v2 | $4.70 | 527 | $0.009 | 150 | 15 | $0.31 | 3 | $1.57 | 0 | -- | 2.0% | HOLD |
```

**All monetary values in USD unless specified. All rates as percentages with one decimal.**

---

## Metric Definitions

| Column | Formula | What It Tells You |
|--------|---------|-------------------|
| `Spend` | A-ADS reported spend | Total acquisition cost |
| `Clicks` | A-ADS reported clicks | Raw traffic volume from ad network |
| `CPC` | Spend / Clicks | Cost per click -- Layer 1 efficiency |
| `Visitors` | PostHog distinct_id from $pageview events | Tracked users who arrived (capture rate = Visitors/Clicks) |
| `Ch.Opened` | PostHog distinct_id from chapter_opened events | Users who actually started reading |
| `Ch.Opened CPA` | Spend / Ch.Opened | Cost to get one reader to start reading |
| `Ch.Completed` | PostHog distinct_id from chapter_completed events | Users who finished a chapter |
| `Ch.Comp CPA` | Spend / Ch.Completed | Cost to get one completed chapter read -- key conversion metric |
| `Ch.3 Reached` | PostHog distinct_id from chapter_completed where chapter_number=3 | Users who reached milestone chapter |
| `Ch.3 CPA` | Spend / Ch.3 Reached | Cost to get one reader to chapter 3 -- highest-intent signal |
| `Conv.Rate` | Ch.Completed / Visitors × 100 | Spend-independent creative quality score |

**Critical: Do NOT mix funnel stages when comparing.** CPC is a click-level metric. Ch.Opened CPA is a reader-level metric. They measure different things.

---

## Conversion Rate vs CPA: Which to Use for Ranking

> **Always rank by Conversion Rate (Conv.Rate) for creative quality.**
> **Always use CPA for acquisition efficiency decisions.**

- Conversion Rate (completers/visitors) is **spend-independent** -- a creative's true quality regardless of budget
- CPA is **budget-corrupted** -- high-spend creatives will always look cheaper per completion because volume smooths out variance
- Ch.3 CPA is the most expensive because it requires the most reader commitment

**The hierarchy of signal:**
1. Ch.3 reached > Ch.Completed > Ch.Opened > Visitors > Clicks
2. More commitment required = stronger signal of real reader intent

---

## The Six Verdict Types

| Verdict | Condition | Action |
|---------|-----------|--------|
| **SCALE** | Conv.Rate above average AND CPA is competitive AND 30+ visitors | Increase budget aggressively |
| **HOLD** | Conv.Rate is average, not enough volume for certainty, CPA is acceptable | Keep spend steady, gather more signal |
| **NEW CREATIVE** | Conv.Rate is good BUT CTR/CPC is high (traffic problem) | Do not kill -- the novel is proven, replace the ad creative |
| **FIX NOVEL** | CTR is good BUT Conv.Rate is low (content problem) | Keep the ad format, fix the novel's first-chapter hook |
| **PRUNE** | Conv.Rate below average with 50+ visitors AND CPA is poor | Stop spending on this creative |
| **WAIT** | Under 30 visitors | Too noisy -- conversion rates are statistically unreliable |

---

## Layer Diagnosis (Ad vs Novel)

```
                        LOW CTR
                      /          \
HIGH Conv.Rate         | Novel proven  |  ABANDON -- ad filters
(Ch.Comp/Visitors)      | Replace ad   |  wrong people AND novel
                        | (NEW CREATIVE)| won't convert without them
                      \
                       LOW Conv.Rate
                      /          \
HIGH CTR               | Novel broken  |  ABANDON -- both
                       | Fix novel     |  components broken
                       | (FIX NOVEL)   |  (PRUNE)
                      \
                    HIGH CTR + HIGH Conv.Rate
                         SCALE
```

---

## Data Collection Code

Run this Python code to collect all funnel data from PostHog for a set of campaigns:

```python
import urllib.request, json, time
from collections import defaultdict

API_KEY = "phx_HBorvUARpdZwGBNBuCuTmjnBoRetfHTc4ELdvD5f9pjrECAc"
BASE = "https://app.posthog.com/api/projects/314999"
DATE_RANGE = "-12h"  # or "-7d", "-30d", "-365d"

EVENTS = ["$pageview", "chapter_opened", "chapter_completed"]

all_events = {}
for ev in EVENTS:
    events = []
    url = f"{BASE}/events/?event={ev}&limit=50000&after={DATE_RANGE}"
    while url:
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {API_KEY}"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
        results = data.get('results', [])
        events.extend(results)
        url = data.get('next')
        if not url:
            break
        time.sleep(0.3)
    all_events[ev] = events

# Aggregate by (campaign, creative)
visitors = defaultdict(set)
chapter_openers = defaultdict(set)
chapter_completers = defaultdict(set)
ch3_completers = defaultdict(set)

for e in all_events["$pageview"]:
    p = e.get("properties", {})
    campaign = str(p.get("utm_campaign") or "")
    content = str(p.get("utm_content") or "")
    did = e.get("distinct_id")
    if campaign and content and did:
        visitors[(campaign, content)].add(did)

for e in all_events["chapter_opened"]:
    p = e.get("properties", {})
    campaign = str(p.get("utm_campaign") or "")
    content = str(p.get("utm_content") or "")
    did = e.get("distinct_id")
    if campaign and did:
        chapter_openers[(campaign, content)].add(did)

for e in all_events["chapter_completed"]:
    p = e.get("properties", {})
    campaign = str(p.get("utm_campaign") or "")
    content = str(p.get("utm_content") or "")
    did = e.get("distinct_id")
    ch_num = str(p.get("chapter_number") or "")
    if campaign and did:
        chapter_completers[(campaign, content)].add(did)
        if ch_num == "3":
            ch3_completers[(campaign, content)].add(did)

# Print results
print("\n=== RAW COUNTS ===")
for key in sorted(set(list(visitors.keys()) + list(chapter_openers.keys()))):
    v = len(visitors.get(key, set()))
    co = len(chapter_openers.get(key, set()))
    cc = len(chapter_completers.get(key, set()))
    c3 = len(ch3_completers.get(key, set()))
    print(f"{key[0]}/{key[1]}: {v}v | {co}open | {cc}comp | {c3}ch3")
```

---

## Building the Scorecard Table

After collecting data, build the scorecard using A-ADS spend data alongside PostHog funnel counts:

```python
# A-ADS data (from platform export -- entered manually or via API)
aads_data = {
    ("weakest-kobold", "static-v1"):       {"spend": 3.52, "clicks": 383, "impressions": 385000},
    ("self-summoning-demon", "gif-v2"):    {"spend": 4.70, "clicks": 527, "impressions": 520000},
}

# PostHog counts (from code above)
# visitors, chapter_openers, chapter_completers, ch3_completers are dicts
# keyed by (campaign, creative) -> set of distinct_ids

rows = []
for key, aads in aads_data.items():
    campaign, creative = key
    spend = aads["spend"]
    clicks = aads["clicks"]
    v = len(visitors.get(key, set()))
    co = len(chapter_openers.get(key, set()))
    cc = len(chapter_completers.get(key, set()))
    c3 = len(ch3_completers.get(key, set()))

    cpc = spend / clicks if clicks else 0
    co_cpa = spend / co if co else 0
    cc_cpa = spend / cc if cc else 0
    c3_cpa = spend / c3 if c3 else 0
    conv_rate = 100 * cc / v if v else 0

    rows.append({
        "creative": f"{campaign}/{creative}",
        "spend": spend,
        "clicks": clicks,
        "cpc": cpc,
        "visitors": v,
        "ch_opened": co,
        "co_cpa": co_cpa,
        "ch_completed": cc,
        "cc_cpa": cc_cpa,
        "ch3": c3,
        "c3_cpa": c3_cpa,
        "conv_rate": conv_rate,
    })

# Sort by conv_rate descending
rows.sort(key=lambda x: x["conv_rate"], reverse=True)

# Print markdown table
print("| Creative | Spend | Clicks | CPC | Visitors | Ch.Opened | Ch.Opened CPA | Ch.Completed | Ch.Comp CPA | Ch.3 | Ch.3 CPA | Conv.Rate | Verdict |")
print("|----------|-------|--------|-----|----------|-----------|---------------|--------------|-------------|------|----------|-----------|---------|")
for r in rows:
    ver = "SCALE" if r["conv_rate"] > 3 and r["visitors"] > 30 else           "HOLD" if r["visitors"] > 10 else "WAIT"
    print(f"| {r['creative']} | ${r['spend']:.2f} | {r['clicks']} | ${r['cpc']:.3f} | "
          f"{r['visitors']} | {r['ch_opened']} | ${r['co_cpa']:.2f} | "
          f"{r['ch_completed']} | ${r['cc_cpa']:.2f} | {r['ch3']} | "
          f"{'${:.2f}'.format(r['c3_cpa']) if r['c3'] else '--'} | "
          f"{r['conv_rate']:.1f}% | {ver} |")
```

---

## Live Example: weakest-kobold vs self-summoning-demon (12h)

### Raw Counts (PostHog)

| Creative | Visitors | Ch.Opened | Ch.Completed | Ch.3 |
|---------|----------|-----------|--------------|------|
| weakest-kobold/static-v1 | 88 | 8 | 3 | 1 |
| self-summoning-demon/gif-v2 | 150 | 15 | 3 | 0 |

### A-ADS Data

| Creative | Spend | Clicks | Impressions | CPC |
|---------|-------|--------|-------------|-----|
| weakest-kobold/static-v1 | $3.52 | 383 | 385,000 | $0.009 |
| self-summoning-demon/gif-v2 | $4.70 | 527 | 520,000 | $0.009 |

### Scorecard Table

```
| Creative | Spend | Clicks | CPC | Visitors | Ch.Opened | Ch.Opened CPA | Ch.Completed | Ch.Comp CPA | Ch.3 | Ch.3 CPA | Conv.Rate | Verdict |
|----------|-------|--------|-----|----------|-----------|---------------|--------------|-------------|------|----------|-----------|---------|
| weakest-kobold/static-v1 | $3.52 | 383 | $0.009 | 88 | 8 | $0.44 | 3 | $1.17 | 1 | $3.52 | 3.4% | SCALE |
| self-summoning-demon/gif-v2 | $4.70 | 527 | $0.009 | 150 | 15 | $0.31 | 3 | $1.57 | 0 | -- | 2.0% | HOLD |
```

### Key Inferences

1. **Same CPC ($0.009)** -- both ads perform equally at the click level
2. **gif-v2 is 2x cheaper per chapter opened** ($0.31 vs $0.44) -- its traffic is more interested in reading
3. **weakest-kobold wins on completed chapter** -- $1.17 vs $1.57 CPA despite less traffic
4. **Only weakest-kobold reached Ch.3** -- 1 reader in 12h vs 0 for gif-v2. Ch.3 requires genuine reader commitment
5. **Conversion rate: weakest-kobold 3.4% vs gif-v2 2.0%** -- the novel is holding readers better

**Verdict: SCALE weakest-kobold.** Same spend, same completions, lower CPA, better conversion rate, and the only creative reaching Ch.3. gif-v2 is strong traffic but the novel hook needs work.

---

## Known Issues and Guardrails

- **12h data is noisy** -- wait for 30+ visitors before calling SCALE or PRUNE. Below 10 visitors is WAIT.
- **CPC varies by time of day and geography** -- compare within similar time windows
- **Ch.3 CPA can be infinite** (0 ch3 reached) -- do not use ch.3 CPA for decision-making on new/low-volume campaigns. Use it as a secondary signal only.
- **Capture rate** = Visitors / Clicks. If below 30%, the UTM wiring is broken and PostHog data is unreliable. Flag this before any analysis.
- **gif-v1 on self-summoning-demon historically shows impossible stats** (8 visitors, 54 chapter opens, 187% conversion rate) -- distinct_id mismatch between pageview and chapter events for some users. Treat gif-v1 data as unreliable.
