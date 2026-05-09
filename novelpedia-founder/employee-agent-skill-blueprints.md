# Novelpedia Employee-Agent Skill Blueprints

Draft catalog for review.

These are proposed skill blueprints for employee-facing Hermes profiles in a future Novelpedia multi-profile system.

They are intentionally written as draft design artifacts, not installed Hermes skills.

## Design goals for this starter skill set

The starter set should help employees with the conversations they are most likely to have with their AI profiles:
- daily work triage
- blocker clarification
- task clarification
- dependency requests and handoffs
- brainstorming with execution pressure
- follow-up drafting
- status updates
- meeting summary to actions
- retrospective and growth help
- overload recovery

## Shared design rules for all employee-facing skills

Every employee-facing skill should:
- stay execution-focused
- produce a concrete artifact, not just reflection
- separate private coaching from manager-visible execution notes
- avoid raw peer-data leakage
- avoid storing secrets in memory/docs
- prefer visible markdown/doc sync for changing work state
- keep outputs short enough for chat but structured enough to reuse
- identify whether a result is purely private, manager-visible, founder-brief-eligible, or ephemeral

## Shared visibility labels

To keep skill outputs legible and policy-safe, each future skill should be able to mark output or notes as:
- `[private]`
- `[manager-visible]`
- `[founder-brief-eligible]`
- `[ephemeral]`

Default rule:
- if the skill is doing coaching, reflection, or emotional decompression in service of work, default private
- if the skill is producing status, blockers, asks, or evidence needed for coordination, manager-visible may be appropriate
- founder-brief-eligible should be a narrower subset, not a synonym for manager-visible

## Recommended rollout priority

### Tier 1: Must-have early skills
1. `daily-standup-triage`
2. `blocker-diagnosis`
3. `task-clarification`
4. `follow-up-drafting`
5. `status-summarization`
6. `meeting-to-action-extraction`

### Tier 2: High-value collaboration and growth skills
7. `dependency-handoff`
8. `brainstorming-session`
9. `retrospective-capture`
10. `skill-gap-coaching`
11. `decision-log-capture`
12. `overload-reset`

---

## 1. daily-standup-triage

### Purpose

Help the employee quickly turn scattered context into a clear plan for the day:
- top priorities
- blockers
- dependencies
- risks
- next follow-up points

### Trigger conditions

Use when the employee says things like:
- "What should I focus on today?"
- "Let’s do standup"
- "Help me plan the day"
- "I have too much on my plate"
- start-of-day check-in
- pre-founder-brief or pre-manager-sync check-in

### Inputs needed

Minimum:
- current tasks
- deadlines or due-soon items
- blockers
- dependencies / waiting-ons
- yesterday’s commitments if available

Helpful extras:
- available work time today
- meetings today
- manager expectations
- current stress/overload signal translated into execution terms

### Workflow steps

1. Ask for the top current work items.
2. Ask what is due today or most likely to slip next.
3. Separate:
   - must finish today
   - should advance today
   - can wait
4. Identify blockers and dependency waits.
5. Force ranking: no more than one to three true priorities.
6. Suggest the day plan in execution order.
7. Flag whether any blocker/risk is manager-visible or founder-brief-eligible.
8. End with a check-in or follow-up trigger.

### Output format

Preferred format:
- Top priorities
- Today’s concrete targets
- Active blockers
- Waiting on
- Risks / likely slips
- Next check-in

Short version example:
- Priority 1:
- Priority 2:
- Priority 3:
- Blockers:
- Waiting on:
- If nothing changes today, the biggest risk is:

### Pitfalls

- Accepting a laundry list instead of a ranked plan.
- Letting the employee carry too many priorities.
- Treating vague motion as progress.
- Skipping dependency waits.
- Turning standup into journaling instead of planning.

### Privacy notes

- Private frustration should not automatically become manager-visible reporting.
- Upward-ready summaries should only include execution-relevant facts.
- Do not include speculation about peers when summarizing blockers.

---

## 2. blocker-diagnosis

### Purpose

Turn "I’m stuck" into a clear blocker diagnosis, a next unblock action, and an escalation path if needed.

### Trigger conditions

Use when the employee says things like:
- "I’m blocked"
- "I don’t know how to move this"
- "I’m waiting on someone"
- "This keeps failing"
- "I’m spinning on this"

### Inputs needed

Minimum:
- blocked objective
- current obstacle
- what has already been tried
- evidence or symptoms

Helpful extras:
- screenshots / logs / notes
- relevant stakeholders
- deadline / impact
- fallback options

### Workflow steps

1. Restate the exact goal that is blocked.
2. Classify the blocker:
   - missing context
   - technical failure
   - decision gap
   - dependency delay
   - access/resource gap
   - overload/scope problem
3. Ask what has already been tried.
4. Extract evidence from facts, not vibes.
5. Generate the smallest plausible unblock options.
6. Recommend the next best step.
7. Define an escalation trigger if the next step fails or stalls.
8. If useful, draft the escalation or dependency ask.

### Output format

Preferred format:
- Blocked goal
- Likely blocker type
- Evidence
- What has already been tried
- Recommended next step
- Escalate if / when
- Draft ask (optional)

### Pitfalls

- Jumping straight to advice without defining the blocker.
- Confusing emotional frustration with root cause.
- Recommending escalation too late.
- Giving broad brainstorming when a specific ask is needed.

### Privacy notes

- Keep blame out of the output.
- Describe peer-caused issues factually and minimally.
- Avoid storing unverified judgments about someone else’s reliability.

---

## 3. task-clarification

### Purpose

Convert a vague assignment, founder request, or manager ask into an executable task with a definition of done.

### Trigger conditions

Use when the employee says things like:
- "I’m not sure what they actually want"
- "Can you help me scope this?"
- "This ask is vague"
- "What does done even look like here?"
- "Turn this into a plan"

### Inputs needed

Minimum:
- original ask
- who requested it
- rough deadline

Helpful extras:
- current context / related project
- examples of similar deliverables
- constraints
- what the requester probably cares about most

### Workflow steps

1. Rewrite the ask in plain language.
2. Identify the actual deliverable.
3. Separate knowns from assumptions.
4. Define what success / done looks like.
5. Identify open questions that matter.
6. Suggest a first-pass scope.
7. Break the work into immediate next steps.
8. If needed, draft clarification questions back to the requester.

### Output format

Preferred format:
- Objective
- Deliverable
- Definition of done
- Assumptions
- Open questions
- Proposed scope
- First steps
- Clarification message (optional)

### Pitfalls

- Treating assumptions as approved facts.
- Overbuilding before clarifying the core outcome.
- Making the plan too detailed before the ask is stable.
- Missing who the final judge is.

### Privacy notes

- Share only the context needed to clarify the work.
- Avoid reprinting large chunks of private messages when a short paraphrase is enough.

---

## 4. dependency-handoff

### Purpose

Help the employee ask another person for input, approval, files, decisions, or execution help with minimal back-and-forth.

### Trigger conditions

Use when the employee says things like:
- "I need something from X"
- "Help me ask engineering/design/growth"
- "Draft a handoff"
- "I need approval before I can continue"
- "Can you package this dependency clearly?"

### Inputs needed

Minimum:
- what is needed
- from whom
- why it matters
- desired timing

Helpful extras:
- current status
- relevant links or evidence
- fallback options
- tone requirements

### Workflow steps

1. Define the exact ask.
2. Clarify why the other person should care.
3. Compress the context to the minimum necessary.
4. Specify owner, deadline, and expected response.
5. Add fallback options if possible.
6. Draft the message.
7. Define a follow-up time if no reply comes.

### Output format

Preferred format:
- Dependency summary
- Why it matters
- Needed by
- Draft message
- Follow-up trigger

### Pitfalls

- Vague asks with no deadline.
- Sending too much context.
- Hidden blame or passive aggression.
- No plan for silence.

### Privacy notes

- Minimal disclosure only.
- Do not include private coaching commentary in the outgoing handoff.
- Avoid relaying unrelated internal frustrations.

---

## 5. brainstorming-session

### Purpose

Help the employee explore options without drifting into endless ideation, and land on a next experiment or recommendation.

### Trigger conditions

Use when the employee says things like:
- "Brainstorm with me"
- "Give me options"
- "What are some ways to approach this?"
- "I need ideas for this problem"
- "Pressure-test this concept"

### Inputs needed

Minimum:
- problem or opportunity
- goal
- constraints

Helpful extras:
- audience / customer / stakeholder
- current hypothesis
- available resources
- timing / urgency

### Workflow steps

1. Frame the problem tightly.
2. Clarify success criteria and constraints.
3. Generate options across a few categories, for example:
   - low-risk / immediate
   - moderate / leverage-building
   - bold / experimental
4. Compare tradeoffs.
5. Reject obviously weak ideas.
6. Recommend one next move or test.
7. Convert the chosen direction into an action or message.

### Output format

Preferred format:
- Problem frame
- Constraints
- Options
- Pros / cons
- Recommendation
- Next experiment

### Pitfalls

- Producing a long idea list without judgment.
- Treating novelty as value.
- Ignoring execution cost.
- Failing to choose a next move.

### Privacy notes

- Do not use peer-sensitive details as casual brainstorming material.
- Keep examples generalized unless specific disclosure is necessary and appropriate.

---

## 6. follow-up-drafting

### Purpose

Draft short, effective follow-ups that increase the chance of response and reduce awkwardness or delay.

### Trigger conditions

Use when the employee says things like:
- "Draft a follow-up"
- "Nudge them for me"
- "Help me ask again"
- "Write a concise reminder"
- "How do I chase this without sounding annoying?"

### Inputs needed

Minimum:
- recipient
- goal of the follow-up
- context of the original thread

Helpful extras:
- relationship / seniority dynamics
- tone preference
- urgency
- exact call to action

### Workflow steps

1. Clarify what outcome the follow-up should produce.
2. Identify the minimal context reminder needed.
3. Choose tone:
   - neutral
   - warm
   - direct
   - urgent
4. Write one or more versions.
5. Make the ask explicit.
6. Include a response deadline only if useful.
7. Suggest when to follow up again.

### Output format

Preferred format:
- Ultra-short version
- Standard version
- Firm version (optional)
- Suggested send timing
- Next follow-up if no response

### Pitfalls

- Vague nudges with no ask.
- Guilt-heavy wording.
- Overexplaining history.
- Escalating tone too early.

### Privacy notes

- Do not leak internal commentary about the recipient.
- Keep sensitive context out unless necessary.
- Avoid auto-sending without user approval or approved automation.

---

## 7. status-summarization

### Purpose

Turn messy work activity into a clean update for async communication, manager check-ins, or founder-facing summaries.

### Trigger conditions

Use when the employee says things like:
- "Help me write an update"
- "Summarize my progress"
- "Turn this into a status report"
- "What should I send in standup?"
- "Compress this for leadership"

### Inputs needed

Minimum:
- completed work
- in-progress work
- blockers / risks
- next steps

Helpful extras:
- audience
- target length
- metrics / evidence
- decisions made

### Workflow steps

1. Separate done from in-progress.
2. Highlight outcomes, not just activity.
3. Pull out blockers and risks clearly.
4. Identify what help is needed, if any.
5. Rewrite to fit the target audience.
6. Remove noise.
7. Mark if any line is leadership-relevant.

### Output format

Preferred format:
- Done
- In progress
- Blocked / risk
- Next
- Help needed

Alternative short format:
- Progress
- Risks
- Ask

### Pitfalls

- Burying blockers inside progress bullets.
- Listing activity with no outcome.
- Oversharing irrelevant details.
- Writing the same update for every audience.

### Privacy notes

- Manager-visible and founder-visible summaries should be more scoped than private notes.
- Avoid including private emotional commentary.
- Do not attribute blame unless evidence and need are both clear.

---

## 8. retrospective-capture

### Purpose

Help the employee learn from a finished task, a rough week, or a miss without turning the conversation into self-criticism theater.

### Trigger conditions

Use when the employee says things like:
- "Let’s do a retro"
- "Why did this slip?"
- "Help me learn from this"
- "What should I change next time?"
- after a deliverable, miss, or sprint

### Inputs needed

Minimum:
- intended outcome
- actual outcome
- what went well / badly

Helpful extras:
- timeline
- contributing factors
- dependencies
- prior similar patterns

### Workflow steps

1. Restate the goal and actual result.
2. Identify what worked.
3. Identify what slipped.
4. Separate causes:
   - ambiguity
   - planning
   - dependency
   - skill gap
   - execution discipline
   - overload
5. Extract one or two actionable lessons.
6. Convert lessons into process changes.
7. Optionally update growth notes or manager-visible notes.

### Output format

Preferred format:
- Goal
- Outcome
- What worked
- What slipped
- Root causes
- Process change for next time
- Growth note

### Pitfalls

- Drifting into vague self-blame.
- Capturing too many lessons.
- Treating every miss as a character flaw.
- Missing systemic causes.

### Privacy notes

- Default private unless there is a clear manager-visible execution takeaway.
- Private coaching notes should stay separate from shareable status summaries.

---

## 9. skill-gap-coaching

### Purpose

Translate repeated friction in the work into a focused development plan for one concrete skill or capability.

### Trigger conditions

Use when the employee says things like:
- "What should I get better at?"
- "Why do I keep struggling with this?"
- "Help me improve here"
- "What skill is missing?"
- after repeated misses in the same pattern

### Inputs needed

Minimum:
- target skill area or repeated failure mode
- one recent example
- current role context

Helpful extras:
- expected level for role
- time horizon
- available practice opportunities
- manager expectations

### Workflow steps

1. Define the skill gap in work terms.
2. Use evidence from recent examples.
3. Narrow the gap to one specific subskill.
4. Recommend a small practice plan.
5. Tie the practice to current work.
6. Define what progress would look like.
7. Optionally capture a capability note for the employee profile.

### Output format

Preferred format:
- Skill gap statement
- Evidence
- Why it matters in role
- Next practice target
- How to apply it this week
- Evidence of progress

### Pitfalls

- Giving generic career advice.
- Making the target too broad.
- Confusing confidence issues with skill issues.
- No real proof condition for improvement.

### Privacy notes

- Growth coaching should default private unless the employee explicitly wants it packaged for a manager conversation.
- Capability updates should be evidence-based, not vibes-based.

---

## 10. meeting-to-action-extraction

### Purpose

Convert meeting notes, transcripts, or rough recollections into decisions, action items, owners, open questions, and follow-ups.

### Trigger conditions

Use when the employee says things like:
- "Summarize this meeting"
- "What are the action items?"
- "Turn these notes into something usable"
- "Extract owners and next steps"
- after calls, syncs, reviews, or planning meetings

### Inputs needed

Minimum:
- notes or transcript
- meeting topic
- attendees if known

Helpful extras:
- desired audience for summary
- relevant project
- existing commitments or prior notes

### Workflow steps

1. Extract the main topic and decisions discussed.
2. Separate:
   - decisions made
   - actions agreed
   - unresolved questions
   - informational discussion only
3. Identify owners and deadlines where explicit.
4. Mark ambiguities when owners or dates were not actually stated.
5. Draft a clean summary.
6. Optionally draft follow-up messages for missing owners or confirmations.

### Output format

Preferred format:
- Summary
- Decisions
- Action items
- Open questions
- Follow-ups to send

If possible, action items should include:
- owner
- task
- due date or timing
- dependency / note

### Pitfalls

- Inventing owners or dates.
- Treating discussion as decision.
- Keeping too much transcript noise.
- Missing unresolved questions.

### Privacy notes

- Preserve meeting confidentiality boundaries.
- Do not lift side comments or emotional subtext into formal summaries unless operationally necessary.

---

## 11. decision-log-capture

### Purpose

Turn a real decision into a durable short record with rationale, owner, and implications.

### Trigger conditions

Use when the employee says things like:
- "Document this decision"
- "Capture why we chose this"
- "Add this to the log"
- after a meaningful product, growth, or execution choice

### Inputs needed

Minimum:
- decision taken
- owner
- rationale

Helpful extras:
- options considered
- expected impact
- affected workstreams
- links to source discussion

### Workflow steps

1. Restate the decision in one sentence.
2. Identify the owner.
3. Capture why the decision was made now.
4. Note tradeoffs or rejected alternatives.
5. Record expected impact.
6. Record follow-up actions if any.
7. Mark what docs or tasks should update.

### Output format

Preferred format:
- Decision
- Date
- Owner
- Why
- Tradeoffs
- Expected impact
- Follow-up actions
- Source links / notes

### Pitfalls

- Capturing unresolved debate as a decision.
- Omitting rationale.
- Writing a novel when a durable short record would do.
- Forgetting downstream actions.

### Privacy notes

- Focus on the decision, not private interpersonal commentary around it.
- Keep rationale factual and organization-appropriate.

---

## 12. overload-reset

### Purpose

Help an employee recover when too many open loops, unclear priorities, and silent dependencies are causing thrash.

### Trigger conditions

Use when the employee says things like:
- "I’m overwhelmed"
- "I don’t know where to start"
- "Everything feels urgent"
- "I keep context-switching"
- "Help me reset"

### Inputs needed

Minimum:
- current open items
- deadlines
- current blockers

Helpful extras:
- available work time
- meetings / interruptions
- who can help or absorb work
- previous commitments

### Workflow steps

1. Inventory all open loops.
2. Group into:
   - must do now
   - should schedule
   - should delegate / ask for help
   - should drop or defer
3. Rank by consequence, not anxiety.
4. Surface hidden dependencies and stale follow-ups.
5. Recommend a reduced plan for today.
6. Draft any de-scope, delay, or help-request messages.
7. Set a reset checkpoint.

### Output format

Preferred format:
- Must do now
- Schedule next
- Delegate / ask
- Drop / defer
- Messages to send
- End-of-day checkpoint

### Pitfalls

- Rewriting the entire todo list without reducing it.
- Confusing urgency with importance.
- Refusing to cut scope.
- Missing the communication burden created by deferral.

### Privacy notes

- Keep emotional framing private unless the employee wants to share it.
- If overload creates a real delivery risk, report the execution impact rather than private feelings.

---

## Recommended blueprint conventions if these become real Hermes skills later

If these are later turned into actual Hermes skills, each should probably:
- prefer short, structured outputs
- explicitly ask whether the result is private, manager-visible, or founder-brief-eligible
- update maintained markdown/docs instead of relying on memory alone
- avoid cross-peer reads by default
- refuse to include secrets or private peer content in outgoing drafts

## Recommended first implementation order

1. `daily-standup-triage`
2. `blocker-diagnosis`
3. `task-clarification`
4. `follow-up-drafting`
5. `status-summarization`
6. `meeting-to-action-extraction`
7. `dependency-handoff`
8. `overload-reset`
9. `retrospective-capture`
10. `skill-gap-coaching`
11. `decision-log-capture`
12. `brainstorming-session`

## Bottom line

This starter catalog is designed to make employee-facing Hermes profiles useful in the actual Novelpedia work conversations that are likely to matter:
- what should I do today?
- what is blocking me?
- what did they actually ask for?
- how do I ask for what I need?
- how do I summarize this clearly?
- what should I learn from this?

That keeps the system grounded in execution rather than generic chat.