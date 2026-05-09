# Novelpedia Nudge System Implementation Plan

> For Hermes: use subagent-driven-development to execute this plan task-by-task once approved.

Goal: Build a real nudge and standup system for Novelpedia that drives daily accountability, catches silent slippage, escalates same-day blockers, and produces an exception-first founder brief without turning Hermes into a surveillance toy.

Architecture: V1 should run on top of the Hermes primitives that already exist: profile-local workspaces, cron jobs, message delivery, last-activity tracking, markdown artifacts, and profile isolation. Do not wait for Google Sheets or deep integrations. The correct first move is a reliable local operating layer that can later sync upward into Sheets/Drive once the workflows are stable.

Tech stack: Hermes profiles, cronjob scheduler, send_message delivery, profile-local markdown files, profile-local JSON state files, Discord DMs, optional Telegram fallback, later Google Sheets/Drive sync.

---

## 1. Current State Snapshot

What already exists:
- Multi-profile Novelpedia structure under `/home/LENOVO/.hermes/novelpedia-profiles/`
- Founder profile: `karmicdaoist-197440`
- Employee profile scaffold: `sajid-sharif-badhon-801504`
- Placeholder/unknown profile: `user-48042054`
- Existing founder workspace files:
  - `employee-profile.md`
  - `employee-onboarding-summary.md`
  - `growth-notes.md`
  - `nudge-log.md`
  - `reporting-boundaries.md`
  - `role-success-contract.md`
  - `standups.md`
  - `last_activity.json`
- Existing cron jobs:
  - `Daily Founder Standup` at 09:00
  - `Novelpedia follow-up + Anvelope call reminder` at 19:00
  - `Home check-in at 21:30`

What is not actually working yet:
- The daily founder standup cron has never run successfully.
- `standups.md` is still just a template.
- `nudge-log.md` is still just a template.
- No employee profile has a real nudge loop running.
- No team-wide missing-standup follow-up exists.
- No same-day escalation pipeline exists.
- No founder brief generation exists.
- No decision log exists.
- Arcsol, Anvelope, and Shubham are not yet onboarded into the system with usable routing metadata.

Conclusion: the system is scaffolded, not operational.

---

## 2. V1 Scope and Non-Goals

### V1 scope

V1 must do these six things well:
1. Send a daily standup prompt to each onboarded person.
2. Detect who has not replied by the deadline.
3. Send a follow-up nudge only when needed.
4. Escalate missing replies and serious blockers to the founder the same day.
5. Maintain a visible audit trail of standups, nudges, blockers, and brief outputs.
6. Produce a concise daily founder brief focused on blockers, slips, risks, and meaningful wins.

### V1 non-goals

Do not do these yet:
- Full raw-transcript mining across all employee profiles
- Automatic sentiment scoring
- Fancy performance scoring or employee ranking
- Full Sheets-first architecture before the workflow is stable
- Autonomous reprimands or public shaming
- AI guessing what someone is doing from silence alone

Blunt rule: first build accountability and visibility, not fake intelligence.

---

## 3. Source-of-Truth Model

The system needs one visible canonical layer per profile plus one founder rollup layer.

### 3.1 Raw sources vs canonical truth

1. Raw source: direct messages with the employee
   Canonical artifact:
   - `workspace/standups.md`
   - `workspace/nudge-state.json`
   - `workspace/nudge-log.md`
   - `workspace/blockers.md`
   Owner: employee profile
   Hermes job: ask, parse, log, chase, escalate
   Founder sees: summarized status, misses, blockers, risks

2. Raw source: onboarding conversations
   Canonical artifact:
   - `workspace/employee-profile.md`
   - `workspace/employee-onboarding-summary.md`
   - `workspace/reporting-boundaries.md`
   Owner: employee profile
   Hermes job: maintain role, responsibilities, help style, visibility boundaries
   Founder sees: only fields marked manager-visible or founder-brief-eligible

3. Raw source: follow-up commitments made in conversation
   Canonical artifact:
   - `workspace/nudge-state.json`
   - `workspace/nudge-log.md`
   Owner: employee profile
   Hermes job: schedule one-off conditional nudges, skip if superseded by later activity, log result
   Founder sees: only if the nudge reveals slippage, missed commitments, or blocker risk

4. Raw source: blocker mentions in standups or ad hoc chat
   Canonical artifact:
   - `workspace/blockers.md`
   - founder brief file for the day
   Owner: employee profile plus founder rollup
   Hermes job: classify blocker severity, ask for owner/dependency/next action, escalate if same-day critical
   Founder sees: yes when execution-relevant

5. Raw source: decisions in chats/meetings
   Canonical artifact:
   - founder workspace `decision-log.md`
   Owner: founder profile
   Hermes job: capture durable decisions with owner/date/impact
   Founder sees: always

### 3.2 Canonical-layer rule

Do not rely on memory alone.
Do not rely on raw chats alone.
Do not rely on markdown-only for machine decisions where conditional logic matters.

For V1:
- Markdown is the human-readable audit trail.
- JSON is the machine-readable state for nudges and deadlines.

---

## 4. Core Data Model

### 4.1 Team member record

Stored primarily in `employee-profile.md` and routing metadata.

Required fields:
- preferred_name
- profile_slug
- role
- team
- direct_manager
- founder_visibility_default
- platform
- user_id
- timezone
- standup_time
- standup_deadline
- reminder_style
- escalation_threshold
- current_ownership_areas
- common_dependencies
- reporting_boundaries

### 4.2 Standup entry

Logged in `standups.md`.

Required fields:
- date
- standup_sent_at
- reply_received_at
- status: sent | answered | nudged | missed | escalated
- done
- blocked
- next
- risks
- confidence_of_parse
- escalation_needed: yes/no
- escalation_reason

### 4.3 Nudge record

Machine state in `nudge-state.json`, audit trail in `nudge-log.md`.

Required fields:
- nudge_id
- created_at
- due_at
- type: standup_followup | commitment_followup | blocker_check | founder_chase
- reason
- message
- skip_if_reply_after
- status: scheduled | sent | skipped | answered | expired | escalated
- sent_at
- resolved_at
- resolution_summary
- linked_context

### 4.4 Blocker record

Stored in `blockers.md`.

Required fields:
- blocker_id
- opened_at
- person
- blocker_summary
- dependency_owner
- severity: low | medium | high | critical
- expected_unblock_date
- next_action
- last_checked_at
- state: open | monitoring | escalated | resolved
- founder_visible: yes/no

### 4.5 Founder brief record

Stored as daily files under founder workspace.

Required sections:
- team blockers needing founder attention now
- silent or slipping people
- growth / momentum movement
- major wins worth reinforcing
- critical dependencies and decisions
- recommended founder actions today

---

## 5. Operating Cadence

Default daily rhythm for active team members:

08:45 - pre-scan
- review open blockers
- review unresolved nudges
- review yesterday's misses
- confirm routing metadata exists

09:00 - daily standup prompt
- send standup DM to each onboarded person
- append stub entry to `standups.md`
- create machine-state record for open standup

11:00 - missing standup chase
- if no reply, send short follow-up nudge
- log nudge to `nudge-log.md`
- update status in `nudge-state.json`

13:00 - missing standup escalation
- if still no reply, mark as missed
- notify founder with person, role, last known context, and risk guess
- do not speculate beyond evidence

14:00 - blocker sweep
- check anyone who reported BLOCKED or RISK
- ask for dependency, owner, and next action if missing
- escalate critical blockers immediately, not at end of day

17:30 - open-loop sweep
- chase unresolved commitments like "waiting on Arcsol" or "will send by evening"
- only fire nudges if no subsequent reply/activity has happened

19:00 - founder brief generation
- one brief for the day
- exception-first, not diary style
- include who is slipping, what is blocked, what moved, and what needs founder action

Urgent triggers
- immediate escalation for critical blockers, launch risks, broken deliverables, investor/outreach misses with same-day impact
- advise first when severity is unclear, then log

---

## 6. Cron and Reminder Design

### 6.1 Jobs to keep

Keep these existing jobs but improve them:
- `Daily Founder Standup`
- `Novelpedia follow-up + Anvelope call reminder`

### 6.2 Jobs to add per onboarded profile

For each employee profile, add:
1. `Daily Standup - <slug>`
2. `Standup Chase - <slug>`
3. `Blocker Sweep - <slug>`

For founder rollup, add:
4. `Daily Founder Brief`
5. `Stale Open Loops Sweep`

### 6.3 Conditional nudge rule

Every nudge must check `workspace/last_activity.json` before sending.

If `last_message_at` is later than `skip_if_reply_after`, skip the nudge silently and log:
- status: skipped
- reason: user replied after the nudge was scheduled

This is the key difference between a useful nudge system and a spam bot.

### 6.4 Routing precondition

Do not create live employee cron jobs until these fields are known:
- platform
- user_id or explicit message target
- timezone
- standup time
- visibility rules

Unknown routing data for Arcsol, Anvelope, and Shubham is a hard blocker for automation.

---

## 7. Folder and File Structure

### 7.1 Per-profile workspace

For each profile under:
`/home/LENOVO/.hermes/novelpedia-profiles/<profile-slug>/workspace/`

Required files:
- `AGENTS.md` existing instruction context
- `employee-profile.md` existing
- `employee-onboarding-summary.md` existing
- `reporting-boundaries.md` existing
- `role-success-contract.md` existing
- `standups.md` existing human-readable log
- `nudge-log.md` existing human-readable log
- `growth-notes.md` existing
- `last_activity.json` existing

Add these:
- `nudge-state.json` machine-readable active/open nudges
- `blockers.md` machine-readable-enough blocker audit trail
- `open-loops.md` visible commitments / waiting-ons / promised follow-ups

### 7.2 Founder workspace

Under:
`/home/LENOVO/.hermes/novelpedia-profiles/karmicdaoist-197440/workspace/`

Keep existing files and add:
- `decision-log.md`
- `team-roster.md`
- `team-rollup.md`
- `founder-briefs/YYYY/MM/YYYY-MM-DD-founder-brief.md`
- `escalations.md`
- `nudge-system-implementation-plan.md` this file

### 7.3 Future canonical sheet

After the flow is stable, add one sheet:
`Novelpedia Founder Ops - Canonical Layer`

Suggested tabs:
- People
- Daily Standups
- Open Nudges
- Open Blockers
- Decisions
- Founder Brief Index
- Growth Snapshot

Do not start here. Earn the sheet after the workflow works locally.

---

## 8. Message and Logging Templates

### 8.1 Daily standup message template

Message:

Daily Novelpedia Standup — [DATE]

Reply in this exact format:

DONE — what got done since last standup?
BLOCKED — what is stuck right now?
NEXT — what are you doing today?
RISKS — what could slip, break, or miss?

Be specific. If something is vague, I will push back.

### 8.2 Missing standup nudge template

Message:

Standup missing. Send the four fields now:
DONE
BLOCKED
NEXT
RISKS

If you're blocked, say on what and by whom. Silence hides problems.

### 8.3 Blocker clarification template

Message:

You marked a blocker.
Reply with:
1. exact blocker
2. who/what it depends on
3. what you already tried
4. what next action you need
5. whether founder help is needed today

### 8.4 Founder escalation template

Message to founder:

Nudge/Escalation — [PERSON] — [TIME]

Issue:
- missed standup / unresolved blocker / broken commitment

Known context:
- last response:
- blocker/dependency:
- risk level:

Recommended founder action:
- [specific action]

### 8.5 Nudge log template

Append to `nudge-log.md`:

## [YYYY-MM-DD HH:MM] [nudge_id]
- Type:
- Reason:
- Due at:
- Skip if reply after:
- Status:
- Sent at:
- Resolved at:
- Outcome:
- Founder-visible:

### 8.6 Standup log template

Append to `standups.md`:

## [YYYY-MM-DD]
- Sent at:
- Reply received at:
- Status:
- DONE:
- BLOCKED:
- NEXT:
- RISKS:
- Escalation needed:
- Escalation reason:

### 8.7 Decision log template

Append to founder `decision-log.md`:

## [YYYY-MM-DD] [short decision title]
- Decision:
- Context:
- Owner:
- Why this was chosen:
- Impacted people/functions:
- Review date:
- Source/provenance:

### 8.8 Blocker report template

Append to `blockers.md`:

## [blocker_id] [YYYY-MM-DD HH:MM]
- Person:
- Summary:
- Dependency owner:
- Severity:
- Next action:
- Expected unblock date:
- Founder-visible:
- State:
- Last checked:

### 8.9 Founder brief template

Daily Founder Brief — [DATE]

1. Immediate attention required
- critical blockers
- missed standups with real risk
- urgent decisions needed today

2. Silent / slipping people
- person
- what is missing
- likely impact
- recommended action

3. Movement today
- meaningful progress
- wins worth reinforcing
- growth or delivery momentum

4. Risks
- execution risk
- dependency risk
- launch or growth risk

5. Recommended founder actions
- action
- owner
- urgency

---

## 9. Reporting and Privacy Rules

1. No silent raw-transcript shipping upward.
2. Founder brief should contain structured summaries, not gossip.
3. Private brainstorming stays private unless it creates an execution-relevant blocker, dependency, or commitment issue.
4. Escalate work risk, not personal drama.
5. If founder/root oversight is used, keep it auditable and scoped.
6. Do not write speculative judgments like "lazy" or "unreliable" as durable facts. Write evidence-backed patterns only.

---

## 10. Implementation Tasks

These tasks are small enough to execute safely and verify in order.

### Task 1: Fix the founder standup cron so it actually runs

Objective: turn the existing dormant cron into a working founder self-standup loop.

Files:
- Check: `/home/LENOVO/.hermes/cron/jobs.json`
- Check: `/home/LENOVO/.hermes/novelpedia-profiles/karmicdaoist-197440/workspace/standups.md`
- Check: `/home/LENOVO/.hermes/novelpedia-profiles/karmicdaoist-197440/logs/`

Actions:
1. Inspect why `Daily Founder Standup` has `last_run_at: null`.
2. Run it manually once.
3. Confirm the DM sends.
4. Confirm the stub entry lands in `standups.md`.
5. If DM fails, write a failure log and correct routing.

Verification:
- founder receives the message
- `standups.md` has a dated entry
- job metadata shows a successful run

### Task 2: Add machine-readable nudge state to founder profile

Objective: stop depending on markdown-only for conditional nudges.

Files:
- Create: `/home/LENOVO/.hermes/novelpedia-profiles/karmicdaoist-197440/workspace/nudge-state.json`
- Modify: `/home/LENOVO/.hermes/novelpedia-profiles/karmicdaoist-197440/workspace/nudge-log.md`

Actions:
1. Create an empty JSON structure for active, sent, skipped, and resolved nudges.
2. Keep `nudge-log.md` as the audit log.
3. Define one schema and reuse it everywhere.

Verification:
- file exists
- schema is valid JSON
- one test nudge can be inserted and read back

### Task 3: Create founder blocker log and decision log

Objective: make blocker and decision capture visible and durable.

Files:
- Create: `/home/LENOVO/.hermes/novelpedia-profiles/karmicdaoist-197440/workspace/blockers.md`
- Create: `/home/LENOVO/.hermes/novelpedia-profiles/karmicdaoist-197440/workspace/decision-log.md`
- Create: `/home/LENOVO/.hermes/novelpedia-profiles/karmicdaoist-197440/workspace/escalations.md`

Actions:
1. Initialize files with templates.
2. Ensure each entry carries timestamp, owner, state, and provenance.

Verification:
- files exist and are readable
- templates are in place

### Task 4: Create founder brief directory and template flow

Objective: make daily founder brief generation concrete instead of vague.

Files:
- Create directory: `/home/LENOVO/.hermes/novelpedia-profiles/karmicdaoist-197440/workspace/founder-briefs/`
- Create example file: `/home/LENOVO/.hermes/novelpedia-profiles/karmicdaoist-197440/workspace/founder-briefs/README.md`

Actions:
1. Define year/month/day file structure.
2. Create a brief template.
3. Make the brief exception-first.

Verification:
- directory exists
- at least one example brief file can be generated

### Task 5: Formalize profile routing metadata

Objective: make automation possible for real team members.

Files:
- Check: `/home/LENOVO/.hermes/novelpedia-profile-map.json`
- Modify/add: founder `team-roster.md`

Actions:
1. Create one row per real person: Mehul, Arcsol, Anvelope, Shubham, Sajid if active.
2. Record profile slug, platform, user_id, timezone, standup time, visibility rules.
3. Mark unknown fields explicitly as blockers.

Verification:
- each active person has a row
- unknown routing fields are visible, not implicit

### Task 6: Complete onboarding for each active employee profile

Objective: convert empty profile templates into usable operating profiles.

Files per employee:
- `employee-profile.md`
- `employee-onboarding-summary.md`
- `reporting-boundaries.md`
- `role-success-contract.md`

Actions:
1. Run onboarding conversation.
2. Capture real responsibilities, deliverables, blockers, reminder style, and privacy rules.
3. Record what is founder-brief-eligible.

Verification:
- no active employee profile remains mostly blank
- routing + reporting rules are explicit

### Task 7: Add per-profile standup jobs

Objective: send daily standups to each onboarded person.

Files:
- `jobs.json` will change via cron creation
- employee `standups.md`

Actions:
1. Create `Daily Standup - <slug>` cron for each onboarded employee.
2. Append stub entry when sent.
3. Track the open standup in `nudge-state.json`.

Verification:
- one test employee receives standup DM
- corresponding `standups.md` entry appears
- state file marks standup as open

### Task 8: Add missing-standup chase jobs

Objective: stop silence from hiding slippage.

Files:
- employee `nudge-state.json`
- employee `nudge-log.md`
- founder `escalations.md`

Actions:
1. Create `Standup Chase - <slug>` jobs.
2. At chase time, read `last_activity.json` and open standup state.
3. Skip if the person has already replied.
4. Send nudge if they have not.
5. Escalate to founder if still missing by hard deadline.

Verification:
- a simulated missed standup produces one chase and one log entry
- no duplicate nudge sends occur

### Task 9: Add blocker clarification and same-day escalation flow

Objective: turn vague BLOCKED lines into actionable escalation.

Files:
- employee `blockers.md`
- founder `escalations.md`
- daily founder brief files

Actions:
1. When BLOCKED or RISKS are non-empty, request clarification if needed.
2. Create blocker record.
3. Escalate high/critical blockers the same day.

Verification:
- blocker record exists with severity and next action
- founder gets an escalation for test critical blocker

### Task 10: Add commitment-follow-up nudges

Objective: support the promised behavior in employee AGENTS files.

Files:
- employee `open-loops.md`
- employee `nudge-state.json`
- employee `nudge-log.md`

Actions:
1. When a user says something like "ping me in 2 hours if I don't hear back," create a one-off conditional nudge.
2. Set `skip_if_reply_after` to the latest message time.
3. Skip the nudge if later activity happened.
4. Log outcome.

Verification:
- one-off nudge can be scheduled
- reply before due time causes skip, not send
- no spam after active conversation

### Task 11: Generate daily founder brief automatically

Objective: give the founder one coherent operating summary instead of scattered logs.

Files:
- founder `founder-briefs/YYYY/MM/YYYY-MM-DD-founder-brief.md`
- founder `team-rollup.md`

Actions:
1. Read the day’s standups, nudges, blockers, and escalations.
2. Summarize only what matters.
3. Recommend founder actions.
4. Keep it short and sharp.

Verification:
- brief file is created
- brief includes blockers, slippage, momentum, and actions

### Task 12: Add weekly synthesis after the daily loop is stable

Objective: avoid daily noise without losing trends.

Files:
- founder workspace weekly summary files under `founder-briefs/weekly/`

Actions:
1. Aggregate response rate, recurring blockers, and repeated misses.
2. Highlight growth and reliability patterns using evidence only.

Verification:
- weekly summary shows trends instead of repeating daily text

---

## 11. Rollout Order

Phase 0: make the founder loop actually work
- fix the dormant founder standup cron
- add founder nudge-state.json
- create blocker, escalation, and decision logs

Phase 1: one-employee pilot
- choose one real employee with reachable routing metadata
- onboard fully
- run standup + chase + blocker flow for one week
- tune wording and timing

Phase 2: team rollout
- add Arcsol, Anvelope, Shubham once routing is known
- enforce consistent daily standup format
- track misses and same-day blockers

Phase 3: founder brief and trend layer
- automate brief generation
- add weekly synthesis
- identify recurring slippage patterns

Phase 4: sheet sync if justified
- sync canonical summaries to a founder ops sheet
- do not replace local artifacts; mirror them

---

## 12. Failure Modes

1. Spam bot failure
Too many nudges with no conditional skip logic. Result: people mute the system.

2. Surveillance failure
Raw transcript leakage upward. Result: trust dies and the data quality collapses.

3. Vague-reporting failure
Standups accept fluff like "working on stuff." Result: no execution visibility.

4. Silent-blocker failure
Blockers are logged but not escalated. Result: false sense of control.

5. Empty-profile failure
Profiles stay half-onboarded. Result: automation runs on garbage inputs.

6. Founder-brief bloat
Daily brief becomes a diary. Result: founder stops reading it.

7. Markdown-only control failure
All logic lives in prose files. Result: conditional nudges become brittle.

8. Unknown-routing failure
Trying to automate people without confirmed message targets. Result: phantom system.

---

## 13. Success Metrics

Operational success for V1 means:
- founder standup job runs successfully 5/5 weekdays
- at least 90% of active users reply to standup before hard deadline after tuning
- every missed standup creates either a chase or an explicit skip reason
- every critical blocker is escalated the same day
- founder brief is generated daily and stays short enough to read in under 3 minutes
- no known privacy breach or raw-transcript spill occurs
- nudge logs show outcomes, not just sends

---

## 14. Immediate Next Decisions Required

Before implementation starts, answer these:
1. Who is in scope for the first pilot employee?
2. What platforms and user IDs do Arcsol, Anvelope, and Shubham use?
3. What is the hard deadline after which silence becomes founder-visible?
4. Should standups go out on weekends or weekdays only?
5. What counts as a critical blocker for same-day founder escalation?
6. Should founder brief delivery go to Telegram, Discord, or both?

---

## 15. Recommended Execution Sequence

If executing immediately, the right order is:
1. Debug and manually run `Daily Founder Standup`
2. Add founder `nudge-state.json`
3. Create founder `blockers.md`, `decision-log.md`, `escalations.md`, and brief directory
4. Pilot one conditional nudge against founder profile using `last_activity.json`
5. Onboard one employee profile fully
6. Create one employee standup + chase flow
7. Add founder brief generation
8. Expand to the rest of the team

Blunt recommendation: do not roll this out company-wide until the founder loop and one employee pilot both survive a real week.
