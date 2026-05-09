# Assistant Suggestions

## Emerging operating-system design

### 1. Canonical execution system
Current truth for tasks, owners, action items, and follow-through is split across weekly sync notes, Discord, and manual follow-ups. The assistant should help design a single canonical layer that turns decisions into:
- owner
- due date
- status
- blocker
- last follow-up timestamp
- escalation status

### 2. Decision log
Important decisions are currently partly in weekly sync notes and partly lost in Discord/DMs. A formal decision log should exist so that every meaningful decision has:
- date
- decision summary
- why it was made
- owner
- expected impact
- links to source discussion

### 3. Meeting memory pipeline
Meeting context currently lives in Drive, Meet transcripts, and ad hoc docs. The assistant should eventually convert meetings into a standard output:
- short summary
- decisions made
- action items
- open questions
- linked source transcript/doc

### 4. Growth intelligence layer
Growth and product truth is currently spread across PostHog, Google Analytics, AADS, sheets, and manual analysis of organic efforts like YouTube/TikTok/Instagram. The assistant should help create a unified metrics layer with special focus on:
- retention
- retention funnel by campaign/source
- WAU / DAU / MAU
- chapters read
- campaign effectiveness

### 5. Team nudging / standup system
A high-priority system should exist for daily team nudging, standups, enforcement of decisions, and founder visibility into slippage.

### 6. Employee development files
Maintain a markdown file on each employee tracking:
- role
- strengths
- current tasks
- blockers
- skills
- reliability
- growth areas
- recent misses
- advice/coaching notes

## Accepted current channel inputs
Important operating Discord channels identified so far:
- weekly-sync
- announcements
- bug report
- developer general

## Emerging assistant behavior rules
- Treat fragmented context and undocumented decisions as a core operating problem.
- Bias toward converting conversations into explicit follow-through.
- Build for execution pressure, not just note-taking.
- Prioritize retention understanding over vanity growth reporting.
- Treat employee coaching/tracking as an execution improvement system, not HR theater.
- Push back brutally when Mehul is being vague, optimistic, or delaying.
- Proactively monitor growth, follow-ups, delays, and any important open loops.
- Use reminders and cron-style nudges like an execution alarm clock when appropriate.
- Draft nudges for both Mehul and team members when something is slipping.
- If unsure how hard to escalate, advise first and log it in the standup/founder brief.
- Founder brief cadence should be daily plus urgent event-triggered messages.
- Daily founder brief should always include: team blockers, growth movement, and urgent risks.
- In founder reporting, include both exceptions/problems and wins/momentum.
- Default team-blocker escalation is same day.
- Avoid talking about life outside work unless it materially affects execution and Mehul explicitly wants that discussion.
- Standup digest should evolve into the founder brief, then into growth reporting.
- Never expose credentials, and maintain strict cross-peer privacy.

## Deferred after onboarding / after access
- Drive audit and restructuring can happen after Mehul grants access; at that stage Hermes should identify garbage, suggest cleaner file structures, update things carefully, and recommend missing artifacts.
- Daily standup format can be designed after onboarding, using real system context instead of guessing prematurely.
- Folder/sheet cleanup should be based on observed usage patterns rather than naming theory.
- Campaign labels currently use: domain / graphic / test number.

## Multi-peer company assistant concept (initial evaluation)
The idea is strong, but only if built as a policy-enforced platform rather than a swarm of free-roaming employee bots.

Promising parts:
- per-employee profile and memory
- company skill graph over time
- blocker/complementarity discovery across people
- CEO/founder synthesis layer
- cron-based triage and follow-through

Critical guardrails:
- venting is not a target use case; the focus is proactive work help, nudging, and brainstorming
- prompts/soul.md can shape behavior, but privacy still must be enforced in memory and retrieval scopes
- executive views should prefer aggregates, exceptions, and evidence-backed summaries, even if the founder ultimately has root-level oversight
- do not let AI become an autonomous reprimand machine or hidden surveillance layer
- canonical work truth should still come from systems of record, and memory should sync back into updated markdown/docs rather than becoming a floating shadow layer
- if a CEO/founder profile has root access, that must be treated as a governance decision with explicit policy, auditability, and narrow practical usage — otherwise trust will rot

Recommended rollout:
1. Founder + small pilot profiles
2. Work-state capture from actual systems
3. Shared skill/blocker graph
4. Executive summaries
5. Limited approved automations

## Immediate execution next steps
1. Team members DM Hermes on Discord for lightweight onboarding.
2. For each employee, create a dedicated onboarding folder with employee profile, onboarding summary, SOUL draft, and AGENTS draft.
3. Keep SOUL focused on identity/style; keep Novelpedia workflow and reporting instructions in AGENTS/profile docs.
4. After access is granted, audit Drive/Sheets/Docs before restructuring anything major.
5. Only after team mapping and source audit, start the canonical daily triage / standup / founder-brief layer.

## Suggested build order
1. Decision + action capture layer
2. Team nudging / standup visibility system
3. Growth dashboard tying retention to campaigns
4. Employee execution/growth markdown system
5. Meeting memory standardization
6. Only then: scoped multi-peer company assistant system
