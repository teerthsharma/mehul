---
name: claude-browser-aads-campaign
description: Use browser automation (Claude Code, Codex, etc.) to create or clone an A-ADS campaign for Novelpedia. Logs in, fills the campaign wizard form, and submits. Designed for copy-paste into a Claude Agent prompt.
category: novelpedia
---

# A-ADS Campaign Creation via Browser Agent

Use this skill when asked to create or clone an A-ADS campaign for Novelpedia. Copy-paste the instructions below into your agent.

## Prerequisites

- Browser must be logged into https://aads.com with the Novelpedia account
- Session must be active (login again if redirected to homepage without user menu)

## Credentials (stored — do not share)

- Email: `mehulguptaji114@gmail.com`
- Password: `riIXBDDD9K1u3gbpyMlU`

## URLs

| Action | URL |
|---|---|
| Login | https://aads.com |
| New campaign | https://aads.com/campaigns/new/ |
| Clone campaign | https://aads.com/campaigns/{ID}/clone |

---

## Step 1 — Log in (if not already authenticated)

```
1. Navigate to https://aads.com
2. Click the "Log in" button in the header (ref=e45 or button with text "Log in")
3. Wait for the login modal to appear (class: style_popup-root__tVo_B)
4. In the modal:
   - Find: input[name="/data/attributes/login"] → type: mehulguptaji114@gmail.com
   - Find: input[name="/data/attributes/password"] → type: riIXBDDD9K1u3gbpyMlU
   - Click: button.style_sign-button__ZFEdH (the "Log in" submit button)
5. Wait 3 seconds for redirect
```

**Login modal CSS selectors:**
- Modal container: `.style_popup-root__tVo_B`
- Username input: `input[name="/data/attributes/login"]`
- Password input: `input[name="/data/attributes/password"]`
- Submit button: `button.style_sign-button__ZFEdH`
- reCAPTCHA notice is auto-accepted (hidden checkbox, not blocking)

---

## Step 2 — Navigate to Campaign Form

```
New campaign:    https://aads.com/campaigns/new/
Clone existing:  https://aads.com/campaigns/{ID}/clone  (e.g. 209563)
```

Clone is fastest — all fields pre-fill. For a fresh campaign use the new form.

---

## Step 3 — Fill the Form (new campaign wizard)

Use browser_type for text fields, browser_click for checkboxes/radio buttons.

### Traffic Package (top of page)
- Click the desired traffic package (e.g. "All traffic" or a niche)
- Element: generic clickable with image "all-traffic.title" / "tokens.title", etc.

### Language
- Default: English — no change needed unless targeting non-English

### Ratings (checkboxes — set to false/unchecked)
```
rating-gambling:       unchecked
rating-investments:     unchecked
rating-nsfw:           unchecked
rating-risky:           unchecked
```

### Daily Budget
- Toggle to USD: click "Fixed in USD" button
- Fill textbox `campaign-form-daily-buget-main-value` with BTC amount
  (e.g. `0.003` for ~$250/day at current BTC price)
- Or fill `campaign-form-daily-buget-converted-value` with USD amount

```
Example BTC: 0.00332868 BTC = ~$254.88/day
```

### Max CPM (optional — leave unchecked to let A-ADS optimize)
- `campaign-form-max-cpm-checkbox`: unchecked

### Total Budget (optional)
- `campaign-form-total-budget-checkbox`: unchecked

### Advertisement Section (REQUIRED — the most important part)

Three required text fields:

| Field | Input name | Max chars | Example |
|---|---|---|---|
| Ad title | `campaign-wizard-v3-link-text` | 50 | Read This Fantasy Novel Free |
| Ad text | (textarea) | 50 | A kobold levels up in a dungeon. Chapter 1 is free. |
| URL address | `campaign-wizard-v3-link` | 200 | (see URL rules below) |

**Logo:** Upload via the "Upload file" button (generic with image). Optional but recommended.
**Image:** Same upload pattern.
**Banners only:** `campaign-creation-wizard-v3-banners-only` checkbox — check if running banner ads only.

#### URL Construction Rules

**Base URL format** (paste into `campaign-wizard-v3-link`):
```
https://novelpedia.net/novels/{slug}?utm_campaign={slug}&utm_source={source}&utm_medium=cpc&utm_content={creative}-{variant}
```

**CRITICAL — Append the suffix AFTER the UTM params:**
```
&utm_campaign={slug}&utm_source={source}&utm_medium=cpc&utm_content={creative}-{variant}&partner={{partner}}&http_country_code={{http_country_code}}
```

**Complete URL example:**
```
https://novelpedia.net/novels/the-weakest-kobold-in-the-dungeon-gets-a-level-6aa676?utm_campaign=weakest-kobold&utm_source=aads-novelfire&utm_medium=cpc&utm_content=static-v1&partner={{partner}}&http_country_code={{http_country_code}}
```

**Slug/source/creative/variant values to use:**

| Segment | Allowed values |
|---|---|
| slug | `darkweb-romance`, `fantasy-kingdom`, `rebirth-assassin`, `weakest-kobold` |
| source | `aads-novelfire`, `aads-freewebnovel`, `aads-ranobes`, `aads-novelplus` |
| creative | `gif`, `static`, `video`, `banner`, `native`, `carousel` |
| variant | `v1`, `v2`, or descriptive tag like `chapter1-hook` |

**Filename convention (campaign name):**
```
{slug}__{source}___{creative}__{variant}
Example: weakest-kobold__aads-novelfire__static__v1
```

### Submit
- Find and click the "Submit" or "Create campaign" button
- Button text: "Create campaign", "Submit", or a green/success button
- If no submit visible: scroll to bottom of form

---

## Step 4 — After Submission

1. Note the **A-ADS campaign ID** from the redirect URL (e.g. `https://aads.com/campaigns/209563/edit`)
2. Report back:
   - Campaign ID
   - Campaign name (slug__source__creative__variant)
   - Final URL used (with all params)
   - Status: created / pending moderation / failed

---

## Form Field Reference (complete)

```
input[name="/data/attributes/language"]          Hidden, value="en"
input#rating-gambling                             Checkbox (gambling category)
input#rating-investments                           Checkbox (investments category)
input#rating-nsfw                                 Checkbox (NSFW category)
input#rating-risky                                Checkbox (risky projects category)
input#campaign-form-daily-buget-main-value         BTC daily budget textbox
input#campaign-form-daily-buget-converted-value    USD daily budget textbox
input#campaign-form-max-cpm-checkbox                Set max CPM checkbox
input#campaign-form-total-budget-checkbox           Set total budget checkbox
input#campaign-wizard-v3-link-text                 Ad title (max 50 chars)
textarea[name="/included/0/attributes/text"]        Ad text (max 50 chars)
input#campaign-wizard-v3-link                      URL address (max 200 chars)
input#campaign-creation-wizard-v3-banners-only     Banners only checkbox
```

---

## Common Errors

| Error | Fix |
|---|---|
| "Page not found" after login | Session expired — click Log in again and repeat |
| URL too long (>200 chars) | Shorten slug or use shorter variant names |
| Modal not appearing | Navigate to https://aads.com first, then click Log in |
| Form fields not found | Page may still be loading — add 2s wait after navigation |

---

## Pitfalls

- **UTM params in Link Address field?** NO — A-ADS has no separate suffix/backfill field. Append `&partner={{partner}}&http_country_code={{http_country_code}}` directly to the URL in the URL address field.
- **Two `?` in URL** — if the base novel URL already has query params, use `&` before UTM params.
- **Session expiry** — A-ADS sessions expire ~30 min. If redirected to homepage, log in again.
- **Slug case** — always lowercase, dashes only. `weakest-kobold` not `WeakestKobold`.

---

## Ad Copy Guidelines

Write 2-3 ad copy options under 50 chars each:

- **Punchy/short:** Best for static/banner — front-load the hook
  - e.g. "A Kobold's Dungeon Diary — Free to Read"
- **Curiosity hook:** Create intrigue
  - e.g. "Level 1 Kobold. Level 6 Skills. Unstoppable."
- **Genre-specific:** Appeal to web novel readers
  - e.g. "I Read 47 Chapters in One Sitting. You Will Too."

Ad title = 50 chars max, ad text = 50 chars max.
