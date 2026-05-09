# Novelpedia Daily Triage / Standup / Founder-Brief Implementation Plan

> For Hermes: build this as an execution system, not a note-taking hobby. If a task, blocker, or decision is not captured with an owner, status, and next action, it is still at risk.

**Goal:** Create a practical daily operating system that turns fragmented team updates, Discord chatter, meeting notes, and growth signals into a canonical execution layer, same-day blocker escalation, and a founder brief that is fast to read and hard to ignore.

**Architecture:** Keep raw evidence in the tools where it already lives (Discord, Drive, Meet transcripts, PostHog, Google Analytics, AADS, sheets). Add one canonical operating layer for normalized work truth, plus markdown logs for narrative memory. Hermes sits in the middle: collect, normalize, classify, nudge, escalate, and summarize.

**Scope:** Daily standups, blocker triage, decision capture, daily founder brief, urgent alerts, and the minimum supporting file/sheet structure needed to keep the system alive.

**Explicitly out of scope for now:** Multi-peer employee bots, autonomous HR-style surveillance, full analytics warehousing, or trying to automate every data source before the process works manually.

---

## 1. What this system must solve

Novelpedia does not have a data problem first. It has an execution-truth problem.

Current pain points:
- tasks, owners, and decisions are split across weekly sync notes, Discord, and manual follow-up
- decisions get buried in Discord/DMs and then become folklore
- standups do not reliably convert into founder visibility or same-day intervention
- blockers get mentioned without structured follow-through
- growth signals exist, but they do not consistently show up in daily operating decisions
- founder attention gets wasted re-deriving reality from scattered sources

This system should create one reliable answer to the following questions every day:
- What is each person committed to today?
- What is blocked right now?
- What slipped or was missed?
- What decisions were made and where is the evidence?
- What growth moved materially today?
- What needs Mehul to act today versus merely know about?

---

## 2. Non-negotiable design rules

1. One canonical operating layer.
   - Raw chat, docs, and dashboards remain evidence sources.
   - Normalized execution truth lives in one place.
   - If the same action item lives in three places, the system is already rotting.

2. Hermes memory is support, not source of truth.
   - If something matters, it must be written into a maintained doc or sheet.
   - Nothing important should exist only in invisible model memory.

3. Standups are for commitments and blockers, not diary entries.
   - Keep them short.
   - Force explicit next actions.
   - Tie them to current action items whenever possible.

4. Same-day escalation is the default for team blockers.
   - If severity is ambiguous, Hermes should advise first and log the ambiguity.
   - Do not quietly let blockers age all day.

5. Founder brief must be exception-first.
   - Mehul should not read a wall of paraphrased standups.
   - Surface blockers, growth movement, urgent risks, missed follow-ups, and real momentum.

6. Provenance matters.
   - Every important blocker, decision, and growth claim should link back to the underlying source.
   - No source link means low trust.

7. Employee files are execution tools, not gossip files.
   - Track role, strengths, tasks, blockers, reliability, growth areas, and recent misses.
   - Keep evidence-backed notes only.

---

## 3. Recommended system architecture

```text
Discord channels       Drive docs / sync notes       Meet transcripts
       \                      |                           /
        \                     |                          /
         --> Hermes ingest + normalization + triage <--
                         |
                         v
        Canonical operating layer (master sheet + markdown logs)
                         |
        -----------------------------------------------
        |                    |                        |
        v                    v                        v
   Team nudges         Founder brief            Decision / blocker /
   + reminders         + urgent alerts          meeting memory logs
                         |
                         v
                Daily founder action + follow-through
```

### 3.1 Core components

1. Input layer
   - Discord standups and channel activity
   - weekly sync notes
   - meeting transcripts and docs
   - PostHog, Google Analytics, AADS, manual organic channel analysis
   - manual founder/team updates when needed

2. Normalization layer
   - Hermes parses updates into structured records
   - converts vague statements into owner / status / blocker / next action / due date / escalation state
   - flags missing context instead of hallucinating closure

3. Canonical operating layer
   - one master sheet for structured state
   - markdown logs for briefs, decisions, meetings, blocker reports, and employee profiles

4. Output layer
   - standup nudges
   - blocker follow-up nudges
   - daily founder brief
   - event-triggered urgent alerts

5. Review layer
   - same-day blocker escalation
   - daily review of missed follow-ups
   - weekly cleanup so the system does not become another graveyard

---

## 4. Source-of-truth mapping

| Domain | Raw source(s) | Canonical record | Owner of record | Hermes job | What founder sees |
|---|---|---|---|---|---|
| Daily commitments | daily standup thread or structured standup form | `daily_standups` tab + daily standup markdown digest | each team member for input; Hermes for normalization | parse, validate, flag missing items, map to actions/blockers | exceptions, missing standups, slips, confidence |
| Action items | weekly sync notes, Discord, meeting summaries, founder directives | `action_items` tab | action owner | create/update record, enforce owner/due date/status | overdue items, critical next actions |
| Blockers | standups, bug report channel, direct updates, meetings | `blockers` tab + blocker report markdown | blocker owner initially; Hermes for escalation state | classify severity, age, dependency, next check, escalation | active blockers, aging blockers, founder-needed unblockers |
| Decisions | weekly sync, announcements, meetings, Discord discussions | `decisions` tab + decision log markdown | decision owner | extract, summarize why, link evidence, attach actions | key decisions made, missing decisions still undocumented |
| Meeting memory | Drive notes, Meet transcripts, ad hoc docs | standardized meeting summary markdown + index tab | meeting owner / facilitator | convert transcript into summary, decisions, actions, open questions | only if relevant to current execution or decisions |
| Growth movement | PostHog, GA, AADS, sheets, organic channel analysis | `growth_snapshot` tab + daily growth note | source owner varies; Hermes normalizes | capture daily deltas and anomalies with campaign context | movement in retention, WAU/DAU/MAU, chapters read, campaign anomalies |
| Employee execution profile | observed execution patterns + evidence-backed updates | markdown employee profile + `people` tab link | Mehul / manager with Hermes support | maintain structured profile without speculation | only durable strengths, risks, reliability patterns |
| Nudges / reminders | Hermes-generated | `nudges_log` tab | Hermes | track reminders sent and whether they were answered | repeated misses and ignored nudges |
| Urgent incidents | bug report, production alerts, founder/team messages | `alerts_log` tab + urgent alert message | incident owner | alert immediately, log timeline, keep status fresh | real-time alert plus status changes |

### Raw sources that remain raw
- Discord is evidence, not the final operating layer.
- Drive and Meet transcripts are evidence, not action truth.
- PostHog, GA, and AADS remain metric sources; Hermes writes only the daily snapshot and interpretation.
- Hermes memory should never be treated as durable truth unless synced into the maintained artifacts above.

---

## 5. Canonical data model

Use one master sheet called:
`Novelpedia Founder Ops - Canonical Layer`

### 5.1 Sheet tabs

#### `people`
Columns:
- `person_id`
- `name`
- `role`
- `manager`
- `timezone`
- `active`
- `preferred_nudge_channel`
- `standup_required`
- `employee_profile_link`
- `last_standup_date`
- `reliability_status`
- `current_focus`

#### `action_items`
Columns:
- `action_id`
- `title`
- `owner`
- `created_at`
- `source_type`
- `source_link`
- `related_decision_id`
- `related_meeting_id`
- `priority`
- `status` (`todo`, `in_progress`, `waiting`, `blocked`, `done`, `dropped`)
- `due_date`
- `blocker_id`
- `last_follow_up_at`
- `escalation_state` (`none`, `advise`, `same_day_founder`, `urgent_alert`, `closed`)
- `next_action`
- `last_status_note`
- `updated_at`

#### `daily_standups`
Columns:
- `standup_id`
- `date`
- `person`
- `submitted_at`
- `channel_link`
- `yesterday_commitment`
- `what_shipped`
- `today_commitment`
- `blocker_flag`
- `blocker_summary`
- `confidence` (`high`, `medium`, `low`)
- `need_from_others`
- `parsed_status`
- `missing_input_flag`
- `Hermes_summary`

#### `blockers`
Columns:
- `blocker_id`
- `date_opened`
- `owner`
- `summary`
- `severity` (`P1`, `P2`, `P3`, `P4`)
- `impact`
- `blocking_action_id`
- `dependency_owner`
- `needed_from`
- `needed_by_when`
- `current_status`
- `next_check_at`
- `escalation_state`
- `founder_visible`
- `source_link`
- `resolved_at`
- `resolution_note`

#### `decisions`
Columns:
- `decision_id`
- `date`
- `title`
- `decision_summary`
- `owner`
- `why`
- `alternatives_considered`
- `expected_impact`
- `reversibility`
- `source_link`
- `related_action_ids`
- `status` (`active`, `superseded`, `revisited`)

#### `growth_snapshot`
Columns:
- `snapshot_date`
- `source`
- `metric_name`
- `metric_value`
- `period_compare`
- `delta`
- `campaign_label`
- `campaign_components` (`domain`, `graphic`, `test_number`)
- `anomaly_flag`
- `confidence_note`
- `source_link`
- `interpretation`

#### `nudges_log`
Columns:
- `nudge_id`
- `sent_at`
- `recipient`
- `reason`
- `channel`
- `message_text`
- `response_due`
- `responded_at`
- `status`
- `related_action_id`
- `related_blocker_id`

#### `alerts_log`
Columns:
- `alert_id`
- `triggered_at`
- `alert_type`
- `severity`
- `summary`
- `owner`
- `founder_notified_at`
- `status`
- `latest_update`
- `source_link`

#### `founder_briefs_index`
Columns:
- `brief_date`
- `brief_link`
- `topline`
- `open_blockers_count`
- `urgent_risks_count`
- `key_growth_note`
- `actions_recommended`

#### `meeting_memory_index`
Columns:
- `meeting_id`
- `meeting_date`
- `title`
- `participants`
- `summary_link`
- `decision_ids`
- `action_ids`
- `open_questions`

#### `campaign_reference`
Columns:
- `campaign_label`
- `domain`
- `graphic`
- `test_number`
- `channel`
- `launch_date`
- `notes`

### 5.2 Entity rules

- Every `action_item` needs one owner.
- Every active blocker must point to the action it blocks if possible.
- Every decision worth remembering needs a source link.
- Every founder brief claim should be traceable to a sheet row or source link.
- If a field is unknown, leave it explicit as unknown rather than inventing it.

---

## 6. Recommended doc, sheet, and file structure

### 6.1 Shared Drive / operating folder structure

Create one top-level folder:
`Novelpedia / 00 Founder Ops`

Inside it:

```text
00 Founder Ops/
  01 Templates/
    daily-standup-template.md
    decision-log-template.md
    founder-brief-template.md
    employee-profile-template.md
    blocker-report-template.md
    meeting-summary-template.md
  02 Daily Standups/
    YYYY/
      MM/
        YYYY-MM-DD-team-standup.md
  03 Founder Briefs/
    YYYY/
      MM/
        YYYY-MM-DD-founder-brief.md
  04 Decisions/
    YYYY/
      YYYY-MM-decision-log.md
  05 People/
    employee-name.md
  06 Meetings/
    YYYY/
      MM/
        YYYY-MM-DD-meeting-name.md
  07 Blockers/
    YYYY/
      MM/
        YYYY-MM-DD-blockers.md
  08 Growth/
    YYYY/
      MM/
        YYYY-MM-DD-growth-snapshot.md
  09 Archives/
```

### 6.2 Canonical sheet

Create one master sheet:
`Novelpedia Founder Ops - Canonical Layer`

This is the structured source of truth for execution state.

### 6.3 Local Hermes mirror

Optional but recommended for resilience and versionable memory:
`~/.hermes/novelpedia-founder-ops/`

Mirror the same folders locally. This should be a working cache and backup, not a second competing system.

### 6.4 Ownership of artifacts

- sheet tabs = structured state
- markdown docs = narrative summary, human-readable history, durable context
- raw source links = evidence only
- Hermes memory = convenience layer only

---

## 7. Daily operating flow

Use one operating timezone. Do not let every person self-interpret the day boundary.

### 7.1 Default daily cadence

Recommended starting cadence:
- `08:45` Hermes pre-scan
- `09:00` standup reminder goes out
- `09:30` standup deadline
- `09:35` missing standup nudge
- `10:00` triage complete and blocker list updated
- `13:00` midday blocker sweep
- `16:00` missed follow-up sweep
- `18:00` founder brief delivered
- anytime: urgent event-triggered alert

Adjust once real team behavior is observed, but start with this. A vague cadence means no cadence.

### 7.2 Detailed flow

#### Step A: Pre-scan (`08:45`)
Inputs:
- overnight Discord messages in `weekly-sync`, `announcements`, `bug report`, `developer general`
- unresolved blockers from yesterday
- overdue action items
- yesterday's founder action list
- latest available growth signals

Hermes does:
- scans for unresolved blockers and overdue tasks
- identifies missing decision capture from yesterday's discussions
- creates a pre-standup watchlist: overdue items, repeated misses, likely founder-needed unblocks
- logs any overnight risk or incident candidates

Stores:
- updated statuses in `action_items`, `blockers`, `alerts_log` if needed
- pre-standup notes in the daily standup digest draft

Founder sees:
- nothing yet unless a P1 incident already exists

Logged for later:
- stale items carried forward
- alerts and watchlist candidates

#### Step B: Standup capture (`09:00` to `09:30`)
Inputs:
- each team member submits a standup in the dedicated standup thread/channel using the template

Recommended submission channel:
- start with a dedicated Discord thread/channel because adoption is more important than perfect form UX
- force a strict template
- if formatting quality collapses, move to a short form feeding the same sheet

Each person submits:
- what shipped yesterday
- what they are committed to today
- blockers
- what they need from others
- confidence / risk level
- links if relevant

Hermes does:
- validates template completion
- asks a follow-up only if critical fields are missing
- writes parsed data into `daily_standups`
- maps stated commitments to existing `action_items` or creates missing items
- creates or updates `blockers` rows when blockers are declared

Stores:
- raw link to Discord message
- parsed row in `daily_standups`
- corresponding updates to `action_items` and `blockers`

Founder sees:
- only the exceptions later, not raw standup spam

Logged for later:
- missing standups
- malformed standups
- new commitments and blockers

#### Step C: Missing standup enforcement (`09:35` onward)
Inputs:
- any team member who has not submitted by deadline

Hermes does:
- sends direct nudge
- logs nudge in `nudges_log`
- after one more missed check window, marks standup as missing
- if repeated pattern emerges, adds reliability note candidate for employee file and flags it in founder brief

Stores:
- `nudges_log`
- `daily_standups.missing_input_flag`

Founder sees:
- repeat misses, not every minor lateness

Logged for later:
- compliance patterns by person

#### Step D: Triage and normalization (`09:30` to `10:00`)
Inputs:
- completed standups
- overnight source scan
- yesterday's unresolved items

Hermes does:
- identifies what slipped from yesterday versus what actually shipped
- converts vague blockers into structured blocker records
- identifies actions with no owner, no due date, or no next action
- tags likely founder-needed interventions
- updates escalation states
- drafts the core standup digest that will later feed the founder brief

Stores:
- updated `action_items`
- updated `blockers`
- daily standup digest markdown

Founder sees:
- nothing yet unless urgent

Logged for later:
- normalized operating state for the day

#### Step E: Midday blocker management (`13:00`)
Inputs:
- all open blockers
- any bug report or dependency delays since morning

Hermes does:
- checks whether blockers moved
- nudges dependency owners if action is waiting on them
- upgrades severity when a blocker threatens today's commitment or launch-critical work
- writes blocker report entries for anything non-trivial
- advises first if escalation is ambiguous, but still logs the ambiguity

Stores:
- `blockers`
- `blocker` markdown report
- `nudges_log`
- `alerts_log` if severity crosses urgent threshold

Founder sees:
- same-day blocker escalations that need intervention

Logged for later:
- blocker aging and response latency

#### Step F: Missed follow-up sweep (`16:00`)
Inputs:
- overdue follow-ups, unanswered nudges, unclosed decisions, tasks still missing status updates

Hermes does:
- checks for silence where explicit follow-up was due
- pings owners again when justified
- flags fake closure patterns like saying done without evidence or no linked output
- captures candidate misses for employee profiles only when evidence-backed and repeat enough to matter

Stores:
- `nudges_log`
- `action_items.last_follow_up_at`
- notes for founder brief

Founder sees:
- repeated misses and material slips, not every routine delay

Logged for later:
- follow-through quality patterns

#### Step G: Founder brief generation (`18:00`)
Inputs:
- final blocker state
- daily standups and slips
- growth snapshot
- key decisions captured or still missing
- wins, momentum, and urgent risks

Hermes does:
- writes concise founder brief markdown
- separates signal from noise
- includes team blockers, growth movement, urgent risks every single day
- adds recommended founder interventions for today or tomorrow morning
- links evidence for any strong claim

Stores:
- founder brief markdown file
- `founder_briefs_index`

Founder sees:
- one concise brief with actions, not a pile of transcripts

Logged for later:
- searchable daily operating history

---

## 8. Event-triggered alerts

Daily cadence is not enough. Some things deserve interruption.

### Trigger immediate founder alert when any of the following happens

#### P1: Immediate alert
- production outage or reader-facing access issue
- payment, subscription, or publishing flow breakage
- security, data loss, or credential risk
- launch-critical deliverable blocked with no workaround
- major spend anomaly or campaign issue causing immediate waste
- retention or activity cliff that appears materially abnormal and source-verified

Hermes action:
- send urgent alert immediately
- log `alerts_log` row
- identify owner and next update time
- keep founder updated until resolved or stabilized

#### P2: Same-day founder visibility
- blocker threatening today's key commitment
- repeated missed follow-up on important work
- decision needed today to unblock progress
- campaign or product signal showing significant negative movement but not yet catastrophic
- repeated standup non-compliance by same person

Hermes action:
- log blocker or alert
- nudge relevant owner
- include in founder brief and, if needed, send same-day note before brief

#### P3: Log and monitor
- normal dependency wait
- small metric wobble with uncertain causality
- one-off late standup without pattern
- low-confidence issue with no immediate impact

Hermes action:
- log it, monitor it, do not spam the founder

#### P4: Informational only
- context worth preserving but not acting on today

---

## 9. Escalation rules

### 9.1 Blockers
- any blocker affecting a committed task gets logged the same day
- any blocker older than 2 hours without motion gets rechecked
- any blocker unresolved by midday that threatens today's work becomes founder-visible unless clearly minor
- if severity is ambiguous, Hermes writes an advice note and still logs the blocker
- blockers should name the dependency owner or required decision whenever possible

### 9.2 Missing ownership
- if an action item has no owner, it is not a real plan
- Hermes should mark it as structurally incomplete and push for owner assignment same day
- founder brief should call out ownerless critical work directly

### 9.3 Missing due dates or next actions
- not every task needs a hard date, but critical items need either a due date or explicit urgency class
- every active important item needs a next action
- missing next action is a planning failure and should be called out

### 9.4 Repeated misses
- first miss: log and nudge
- second meaningful miss in a short window: flag in founder brief
- repeated pattern: add evidence-backed note to employee profile and discuss directly

### 9.5 Decision ambiguity
- if people discuss a decision but no one closes it, Hermes creates a pending decision note
- unresolved decision that blocks action becomes founder-visible same day

---

## 10. What inputs come from whom, when, and what happens next

| Input | Who provides it | When | Where submitted / found | Hermes does | Stored in | Surfaced to founder | Logged for later |
|---|---|---|---|---|---|---|---|
| Daily standup | each team member | every workday by `09:30` | standup Discord thread/channel | parse, validate, map to actions, detect blockers | `daily_standups`, `action_items`, `blockers` | only exceptions, misses, low-confidence items | compliance history, commitments, slips |
| Blocker update | task owner or dependency owner | as soon as blocker appears; rechecked midday | standup, bug report, direct message, meeting follow-up | classify severity, identify dependency, set next check, escalate if needed | `blockers`, blocker markdown, `alerts_log` if urgent | P1 immediately; P2 same day; others in brief | blocker age, resolution speed, dependency patterns |
| Decision | founder, team lead, or discussion outcome | same day as decision | weekly sync notes, announcements, meetings, Discord discussion | create decision record, summarize why, attach actions | `decisions` + decision log markdown | major decisions and uncaptured decisions | searchable decision memory |
| Meeting memory | meeting owner / transcript | same day or within 24h | Drive notes, Meet transcript | convert to standard summary with decisions/actions/open questions | meeting markdown + index | only if affecting current execution | durable meeting memory |
| Growth snapshot | Hermes from tools or manual metric owner input | daily before founder brief | PostHog, GA, AADS, sheets, organic analysis | capture deltas, anomalies, campaign linkages | `growth_snapshot` + growth note | growth movement section in brief | time series of interpreted growth changes |
| Bug / incident | engineers or anyone spotting issue | immediately | `bug report` or direct escalation | decide P1/P2/P3, alert, assign owner, track updates | `alerts_log`, `blockers` if execution impact | immediate if severe | incident history |
| Missed follow-up | inferred by Hermes | midday and late afternoon sweeps | derived from action state and unanswered nudges | re-nudge, escalate repeated misses | `nudges_log`, `action_items` | repeated or material misses only | reliability patterns |

---

## 11. Cron and reminder design

Start simple. Manual consistency beats brittle automation theater.

### 11.1 Cron-style jobs to implement first

1. `08:45 daily_source_scan`
   - review key Discord channels
   - pull unresolved blockers and overdue actions
   - create watchlist for the day

2. `09:00 standup_reminder`
   - post standup prompt in daily thread
   - DM anyone with a repeated compliance problem

3. `09:35 standup_missing_check`
   - detect non-submitters
   - send reminder
   - log nudge

4. `10:00 standup_triage_finalize`
   - parse all standups
   - update sheet tabs
   - create blocker rows
   - draft daily digest

5. `13:00 blocker_sweep`
   - check aged blockers
   - prompt dependency owners
   - escalate same-day risks

6. `16:00 followup_sweep`
   - check overdue follow-ups and open loops
   - send second-wave nudges where justified

7. `17:30 growth_snapshot_refresh`
   - update key metrics from available sources
   - mark uncertainty explicitly if data is incomplete

8. `18:00 founder_brief_generate`
   - produce brief
   - store file and index row

### 11.2 Event-based triggers

Fire immediately when:
- a message in `bug report` suggests outage, payments problem, or reader-facing breakage
- a blocker is marked P1 or P2 by severity rules
- a key deliverable loses owner or becomes blocked near deadline
- a major campaign anomaly appears with evidence
- a critical decision remains unresolved and is preventing work

### 11.3 Reminder style rules

- first reminder: neutral and direct
- second reminder: direct and tied to commitment / blocker / consequence
- founder-visible reminder: only when issue is repeat or materially harmful
- do not send vague nagging; every reminder should cite the item, owner, and needed response

Example reminder shape:
- `You committed to X today and the current blocker/status is still unclear. Reply with shipped / blocked / next action by 13:00.`

---

## 12. Founder brief format rules

The founder brief should be readable in under 5 minutes.

### Always include
1. Team blockers
2. Growth movement
3. Urgent risks

### Usually include
- missed follow-ups
- key decisions captured today
- important decisions still undocumented
- wins / momentum
- recommended founder interventions

### Never do
- paste every standup line
- bury the main problem under polite filler
- present fake certainty from inconsistent metrics
- report a blocker without naming owner, impact, and next step

### Recommended founder brief outline
- topline in 3 bullets max
- blockers section sorted by severity
- growth section focused on retention, WAU/DAU/MAU, chapters read, and campaign movement
- urgent risks section with consequence and time horizon
- founder actions section with explicit recommendations
- evidence links at the end

---

## 13. Suggested markdown templates

### 13.1 Daily standup capture template

```md
# Daily Standup - YYYY-MM-DD

- Name:
- Role:
- Submitted at:
- Yesterday's commitment:
- What actually shipped yesterday:
- Today's top 1-3 commitments:
- Current blockers:
- What I need from others:
- Confidence level: high / medium / low
- Links / evidence:
- Notes for Hermes:
```

Rules:
- keep today's commitments to 1-3 items
- if blocked, name who or what is blocking it
- if yesterday's commitment slipped, say so directly

### 13.2 Decision log entry template

```md
## Decision: short title

- Decision ID:
- Date:
- Owner:
- Status: active / superseded / revisited
- Decision summary:
- Why this decision was made:
- Alternatives considered:
- Expected impact:
- Reversibility:
- Related action items:
- Source links:
- Notes / follow-up checks:
```

### 13.3 Founder brief template

```md
# Founder Brief - YYYY-MM-DD

## Topline
- 
- 
- 

## Team Blockers
- [Severity] Owner - blocker summary
  - Impact:
  - Needed from:
  - Next action:
  - Escalation state:

## Growth Movement
- Retention:
- WAU / DAU / MAU:
- Chapters read:
- Campaign movement:
- Confidence / data caveats:

## Urgent Risks
- Risk:
  - Why it matters now:
  - Time horizon:
  - Recommended intervention:

## Missed Follow-Ups
- Owner - missed item - current status

## Decisions Captured / Missing
- Captured:
- Missing or still unresolved:

## Wins / Momentum
- 

## Recommended Founder Actions
1. 
2. 
3. 

## Evidence Links
- 
```

### 13.4 Employee profile template

```md
# Employee Profile - Name

- Role:
- Manager:
- Strengths:
- Current tasks:
- Current blockers:
- Skills:
- Reliability:
- Growth areas:
- Recent misses:
- Current coaching focus:
- Notes backed by evidence:
- Last updated:
```

Rules:
- update weekly, not constantly
- include evidence-backed observations only
- keep private coaching separate from general execution facts if governance requires it

### 13.5 Blocker report template

```md
# Blocker Report - YYYY-MM-DD

## Blocker
- Blocker ID:
- Owner:
- Summary:
- Severity:
- Blocking which task:
- Impact if unresolved:
- Started at:
- Needed from:
- Needed by when:
- Current status:
- Next check time:
- Escalation state:
- Source links:
- Resolution notes:
```

---

## 14. Meeting memory standardization

This system will fail if meetings keep producing ghost decisions.

After every important meeting, Hermes should create one standardized summary file with:
- short summary
- decisions made
- action items with owner and due date
- open questions
- source transcript or doc link

Then Hermes should:
- write decisions into `decisions`
- write action items into `action_items`
- carry open questions into next standup or founder brief only if they matter operationally

Suggested meeting summary template:

```md
# Meeting Summary - YYYY-MM-DD - Meeting Name

## Summary

## Decisions Made
- 

## Action Items
- Owner - action - due date

## Open Questions
- 

## Source Links
- 
```

---

## 15. Implementation roadmap, ordered by leverage and realism

### Phase 0: Post-access audit and map the mess
Duration: 2-3 days

Deliverables:
- map current Drive folders, sheets, dashboards, and relevant Discord channels
- identify what is raw source versus what should become canonical
- list recurring meetings and where transcripts/notes live
- document key metric sources and who trusts what today

Why first:
- without this, the new system will duplicate garbage instead of replacing ambiguity

Success criteria:
- clear source-of-truth map exists
- obvious dead artifacts and duplicate trackers identified
- team knows which channel/process will be used for daily standups

### Phase 1: Create the canonical operating spine
Duration: 2-4 days

Deliverables:
- create master sheet with tabs in this plan
- create Drive folder structure
- create markdown templates
- define severity taxonomy and escalation states
- define standup channel and posting rules

Why this phase matters:
- this is the minimum viable backbone
- do not start fancy automation before this exists

Success criteria:
- every important item has a home
- no active work depends on hidden memory alone

### Phase 2: Launch manual/semi-manual daily standups and founder brief
Duration: 1 week pilot

Deliverables:
- run daily standup prompt in Discord
- manually normalize updates into the sheet
- generate daily founder brief every day
- log blockers same day
- track compliance and pain points

Why this phase matters:
- proves the operating cadence before adding automation
- exposes template problems quickly

Success criteria:
- >80 percent standup compliance by end of week
- founder brief delivered daily
- same-day blockers visible before end of day

### Phase 3: Add reminder logic, blocker sweeps, and urgent alerts
Duration: 1 week

Deliverables:
- implement cron/reminder cadence
- log nudges automatically
- create event-triggered alert rules for P1/P2
- add repeated miss tracking

Why this phase matters:
- execution pressure appears here
- without this, the system is descriptive but not operative

Success criteria:
- reminders are sent on time
- blocker aging is visible
- urgent incidents generate founder alerts without waiting for the daily brief

### Phase 4: Integrate growth movement into the same daily operating loop
Duration: 1 week

Deliverables:
- define minimum daily growth snapshot process
- normalize campaign labels using `domain / graphic / test number`
- connect retention, WAU/DAU/MAU, chapters read, and campaign interpretation to founder brief
- mark uncertainty where data is not yet trustworthy

Why this phase matters:
- founder brief should not be team-only; it must connect execution to growth reality

Success criteria:
- growth section appears daily
- key campaign anomalies are visible with context
- retention stays central, not vanity metrics

### Phase 5: Standardize meeting memory and decision capture
Duration: 1 week

Deliverables:
- create meeting summary workflow
- require decision log entry for meaningful decisions
- make sure decisions link to actions

Why this phase matters:
- decisions otherwise keep leaking back into Discord folklore

Success criteria:
- important meetings generate structured summary within 24 hours
- key decisions are searchable and linked to actions

### Phase 6: Add employee execution / growth files carefully
Duration: 1 week, then ongoing

Deliverables:
- create one profile per employee
- if these profiles are exposed as live messaging gateways, provision one bot token/process per profile or add a routing layer; Hermes token locks prevent sharing one bot token across simultaneous profiles
- update from evidence-backed patterns only
- separate durable execution patterns from temporary daily noise

Why later:
- employee profiles are useful only after actual operating data exists
- if added too early, they become speculative and political

Success criteria:
- profiles help coaching and delegation
- they do not become a vague surveillance archive

### Phase 7: Only after the above works, consider multi-peer assistant ideas
Duration: later

Hard rule:
- do not build employee bots or shared memory meshes before the execution layer is stable, trusted, and governed

---

## 16. Success metrics for the system itself

Track whether the system is actually improving execution.

Minimum operating KPIs:
- daily standup compliance rate
- percent of active action items with owner + status + next action
- percent of blockers logged same day
- median blocker age by severity
- percent of meaningful decisions captured within 24 hours
- daily founder brief delivery rate
- percent of founder brief claims with source links
- repeated miss rate by person and by team area

Healthy-system targets after first month:
- standup compliance above 90 percent
- critical blockers visible to founder same day
- no important decision living only in Discord after 24 hours
- founder brief readable in under 5 minutes
- measurable reduction in dropped follow-ups

---

## 17. Blunt risks and failure modes

1. The system becomes another note graveyard.
   - Cause: lots of docs, no canonical state discipline.
   - Fix: one master sheet, strict ownership, weekly cleanup.

2. Standups become too long or too vague.
   - Cause: no template enforcement.
   - Fix: keep to 1-3 commitments, explicit blockers, hard deadline.

3. Founder brief becomes generic management theater.
   - Cause: summarizing everything instead of surfacing exceptions.
   - Fix: lead with blockers, growth movement, urgent risks, and required actions.

4. Hermes overstates certainty.
   - Cause: inconsistent metrics or weak evidence.
   - Fix: show caveats explicitly; if data is incomplete, say incomplete.

5. Too much automation too early.
   - Cause: trying to wire every tool before process discipline exists.
   - Fix: manual/semi-manual first, then automate only what is stable.

6. Employee profiles become political or creepy.
   - Cause: speculative notes, privacy leakage, or hidden judgments.
   - Fix: evidence-backed execution notes only; careful governance.

7. Nobody enforces owner/due date hygiene.
   - Cause: passive system ownership.
   - Fix: Hermes must push back every time an important item lacks owner, due date, or next action.

8. Alert fatigue.
   - Cause: too many low-value pings.
   - Fix: reserve immediate alerts for P1; route P2 selectively; log the rest.

9. Discord remains the real operating layer because the sheet is not updated fast enough.
   - Cause: slow normalization.
   - Fix: daily `10:00` triage deadline; same-day update discipline.

10. Growth reporting drifts into vanity reporting.
   - Cause: clicks and traffic get more attention than retention and reading behavior.
   - Fix: keep retention, WAU/DAU/MAU, chapters read, and campaign linkage as the core view.

---

## 18. Recommended first implementation sequence

If building this next week, do it in this exact order:

1. audit existing Drive, sheet, and Discord reality
2. create the master sheet tabs
3. create the Drive folder structure and templates
4. choose and announce the standup channel + deadline
5. run a one-week manual pilot
6. generate founder brief daily without fail
7. review misses, blocker quality, and template friction
8. add nudges and blocker sweep automation
9. add growth snapshot integration
10. standardize meeting memory and decisions
11. add employee profiles after evidence exists

This is the leverage-first order. Anything fancier before this is premature.

---

## 19. Final recommendation

The right v1 is not a giant platform. It is a disciplined operating loop:
- structured standups in one place
- same-day blocker logging and escalation
- one canonical action / blocker / decision sheet
- daily founder brief with evidence-backed exceptions
- weekly cleanup so the system stays trusted

If this loop becomes reliable, then Novelpedia gets actual execution memory and founder leverage.
If this loop becomes sloppy, every future automation built on top of it will be garbage faster.
