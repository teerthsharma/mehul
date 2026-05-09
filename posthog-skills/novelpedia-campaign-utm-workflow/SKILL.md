---
name: novelpedia-campaign-utm-workflow
description: Build and register a new A-ADS campaign with UTM links and BigQuery registry for Novelpedia marketing ops
category: novelpedia
---

# Novelpedia Campaign UTM Workflow

## When to use this skill

Use this skill whenever:
- A new A-ADS campaign needs to be created for any novel
- A team member asks for help building a UTM link
- A new novel is being added to the ad rotation
- Launching a variant test, expanding to a new site, or migrating to a new ad network

**Access limitations:** I do not have A-ADS or BigQuery access. I generate the campaign artifacts (name, URL, suffix, SQL). The user handles A-ADS creation, campaign ID retrieval, and SQL execution manually.

## Step 1 — Get campaign details

Before building anything, collect:

1. **Novel slug** — short, consistent identifier (e.g. `darkweb-romance`, `weakest-kobold`)
   - Must match the canonical list in the campaign-utm-guide.md
   - If new, add it to the canonical table before proceeding
2. **Source** — the ad site (e.g. `aads-novelfire`, `aads-freewebnovel`)
3. **Creative format** — `gif`, `static`, `video`, `banner`, `native`, or `carousel`
4. **Variant** — `v1`, `v2`, or descriptive tag (e.g. `chapter1-hook`, `cover-v2`)

## Step 2 — Build the A-ADS campaign name

Format: `<novel-slug>__<source>__<creative>__<variant>`

Example: `weakest-kobold__aads-novelfire__static__v1`

**Rules:**
- Four segments, separated by double underscores (`__`)
- Lowercase, no spaces
- Dashes within a segment are fine; underscores inside a segment are NOT

## Step 3 — Build the UTM tracking URL

Base URL + destination novel URL, then append:

```
?utm_campaign=<novel-slug>&utm_source=<source>&utm_medium=cpc&utm_content=<creative>-<variant>
```

Example (for weakest-kobold):
```
https://novelpedia.net/novels/the-weakest-kobold-in-the-dungeon-gets-a-level-6aa676?utm_campaign=weakest-kobold&utm_source=aads-novelfire&utm_medium=cpc&utm_content=static-v1
```

**Rule:** If the base URL already has query parameters (e.g. `?ref=aads`), use `&` to start the UTM parameters. Never use two `?` in one URL.

## Step 4 — Build the A-ADS suffix

Copy-paste exactly as-is for every A-ADS campaign:

```
&partner={{partner}}&http_country_code={{http_country_code}}
```

**Important:** The param name is `http_country_code` NOT `country`. Order is `partner` first, then `http_country_code`. This exact format was validated against a working A-ADS campaign (self-summoning-demon on Novel Fire).

## Step 5 — Write ad copy

Before finalizing, write 2–3 short ad copy options (under 15 words each) suited to the novel's hook and genre. Include one "punchy/short" option best suited for static/banner, one "curiosity hook" option, and one variant. Keep the novel's core appeal front and center.

## Step 6 — Give the user everything they need

Output the complete package (campaign name, URL, suffix, SQL query, ad copy). Tell them:

> **Now do this yourself:**
> 1. Create the campaign in A-ADS using the campaign name and UTM URL
> 2. Set the A-ADS suffix field to the suffix string
> 3. Copy the SQL query below, fill in the campaign ID (found in the A-ADS campaign URL), and send it to KarmicDaoist — they will execute it in BigQuery
> 4. Message KarmicDaoist in Discord with the campaign name and A-ADS campaign ID so the pipeline can be verified

## Step 6 — SQL registry query

After the campaign is live in A-ADS, run this in BigQuery. Replace the placeholder values:

```sql
MERGE `novelpedia-prod.ads.campaign_registry` AS T
USING (
  SELECT
    'aads' AS network,
    '<CAMPAIGN_ID>' AS campaign_id,
    '<novel-slug>' AS utm_campaign,
    '<source>' AS utm_source,
    '<creative>-<variant>' AS utm_content,
    'novelpedia' AS product,
    CURRENT_DATE() AS launched_at
) AS S
ON T.network = S.network
AND T.campaign_id = S.campaign_id
WHEN MATCHED THEN
  UPDATE SET
    utm_campaign = S.utm_campaign,
    utm_source   = S.utm_source,
    utm_content  = S.utm_content,
    product      = S.product,
    launched_at  = S.launched_at
WHEN NOT MATCHED THEN
  INSERT (network, campaign_id, utm_campaign, utm_source, utm_content, product, launched_at)
  VALUES (S.network, S.campaign_id, S.utm_campaign, S.utm_source, S.utm_content, S.product, S.launched_at);
```

**`<CAMPAIGN_ID>`** comes from the A-ADS campaign URL or dashboard — it's the numeric ID A-ADS assigns.

## Step 7 — Verify canonical table

If the novel slug, source, or creative is genuinely new (not in the list below), update the canonical table in the campaign-utm-guide.md and notify the data team.

**Current canonical values:**

| Segment | Allowed values |
|---|---|
| novel-slug | `darkweb-romance`, `fantasy-kingdom`, `rebirth-assassin`, `weakest-kobold` |
| source | `aads-novelfire`, `aads-freewebnovel`, `aads-ranobes`, `aads-novelplus` |
| creative | `gif`, `static`, `video`, `banner`, `native`, `carousel` |
| variant | `v1`, `v2`, ..., or descriptive tag |
| medium | `cpc` (paid), `social`, `email`, `organic`, `partner` |

## Quick reference output (what to give the user)

When the campaign is ready, output:

```
**A-ADS campaign name:**
<novel-slug>__<source>__<creative>__<variant>

**Tracking URL:**
<full URL with UTMs>

**A-ADS suffix:**
&country={{http_country_code}}&partner={{partner}}

**SQL registry query** (copy, fill in campaign ID from A-ADS, send to KarmicDaoist):
<full SQL MERGE with placeholder values>

**Next:** Create the campaign in A-ADS. After it's live, message KarmicDaoist in Discord with the campaign name and the A-ADS campaign ID (found in the campaign URL).
```

## Pitfalls to watch for

- **Two `?` in one URL** — silently breaks all attribution. Always check the base URL first.
- **Inconsistent slug spelling** — `DarkwebRomance`, `darkweb-romance`, and `darkweb_romance` are three different campaigns in PostHog.
- **Forgetting the suffix** — country and partner data cannot be recovered after the click.
- **Sending SQL before campaign is live** — the campaign ID must exist in A-ADS first. Get it from the A-ADS campaign URL.
- **Not messaging KarmicDaoist** — the pipeline won't be verified and the campaign may sit unmapped indefinitely.
