---
name: posthog-observability
description: Closed-loop observability for Novelpedia's Hermes+PostHog analytics stack. Instruments skill_invoked, skill_completed, skill_errored, and mcp_capability_called events. Builds the agent self-monitoring dashboard. Active once PostHog MCP is configured.
version: 1.0.0
category: novelpedia
metadata:
  novelpedia:
    owner: ai-lead
    review_cadence: weekly
    depends_on: posthog-bridge@1.0.0
---

# PostHog Observability — Agent Self-Monitoring

## Purpose

This skill closes the observability loop: **PostHog monitors itself via the agent.**
Every skill invocation, MCP call, and agent decision is tracked as a PostHog event
so the team can see exactly how the analytics stack is performing.

---

## The Core Insight

> You cannot improve what you cannot measure.
> If the agent queries PostHog but nothing records that query,
> you have a black box. This skill is the audit log.

---

## Events to Instrument

### 1. skill_invoked

Fired immediately when the router selects a skill.

```json
{
  "event": "skill_invoked",
  "properties": {
    "skill_id": "string",
    "skill_version": "string",
    "router_confidence": 0.85,
    "intent_category": "campaign_attribution",
    "trigger": "user_request | timer_triggered | threshold_breach"
  }
}
```

**When to fire:** Router selects a skill → fire immediately before execution.

---

### 2. skill_completed

Fired when a skill finishes successfully.

```json
{
  "event": "skill_completed",
  "properties": {
    "skill_id": "string",
    "skill_version": "string",
    "mcp_calls_made": 2,
    "tokens_consumed": 1840,
    "output_confidence": 0.78,
    "duration_ms": 3400,
    "returned_action": "flag_campaign | no_action | escalate"
  }
}
```

**When to fire:** Skill returns output to router → fire before releasing context.

---

### 3. skill_errored

Fired when a skill fails or escalates.

```json
{
  "event": "skill_errored",
  "properties": {
    "skill_id": "string",
    "skill_version": "string",
    "error_type": "mcp_timeout | mcp_invalid_response | skill_scope_exceeded | no_data",
    "mcp_response_code": 401,
    "escalated_to": "skill_id or null",
    "duration_ms": 1200
  }
}
```

**When to fire:** Skill throws, times out, or escalates → fire immediately.

---

### 4. mcp_capability_called

Fired for each PostHog MCP capability call made by the bridge.

```json
{
  "event": "mcp_capability_called",
  "properties": {
    "capability_name": "get_funnel",
    "skill_id": "binge_reader_funnel_health",
    "cache_hit": false,
    "date_range_used": "-14d",
    "breakdown_used": "utm_source",
    "duration_ms": 890,
    "result_rows": 5,
    "host_scoped": "demo.novelpedia.net"
  }
}
```

**When to fire:** PostHog Bridge executes a capability → fire after response received.

---

### 5. skill_escalated

Fired when one skill hands off to another explicitly.

```json
{
  "event": "skill_escalated",
  "properties": {
    "from_skill": "binge_reader_funnel_health",
    "to_skill": "campaign_attribution_diagnosis",
    "reason": "degraded_health_status",
    "confidence": 0.72
  }
}
```

---

## Implementation Pattern

These events are **not** fired by separate skill calls.
The PostHog Bridge skill (`posthog-bridge`) fires `mcp_capability_called` internally.
The router skill fires `skill_invoked` as part of its routing logic.

For the standalone observability skill: use it to
1. Query the observability events to build the dashboard summary
2. Identify skill drift by analyzing error rates and action rates
3. Run the monthly skill audit query set

---

## Dashboard Queries (for weekly review)

These are pre-built PostHog insight definitions for the observability dashboard.
Use them in PostHog → Insights → New Insight → SQL or Trend.

### Query: Skill usage per day

```sql
SELECT
  date_trunc('day', timestamp) as day,
  countIf(event = 'skill_invoked') as invocations,
  countIf(event = 'skill_completed') as completions,
  countIf(event = 'skill_errored') as errors,
  round(countIf(event = 'skill_errored') / countIf(event = 'skill_invoked') * 100, 1) as error_rate,
  avgIf(duration_ms, event = 'skill_completed') as avg_duration_ms
FROM events
WHERE team_id = :team_id
  AND event IN ['skill_invoked', 'skill_completed', 'skill_errored']
  AND timestamp > now() - interval 30 day
GROUP BY day
ORDER BY day
```

### Query: MCP capability frequency

```sql
SELECT
  properties.capability_name,
  count(*) as call_count,
  avg(properties.duration_ms) as avg_duration_ms,
  countIf(properties.cache_hit = true) as cache_hits,
  round(countIf(properties.cache_hit = true) / count(*) * 100, 1) as cache_hit_rate
FROM events
WHERE team_id = :team_id
  AND event = 'mcp_capability_called'
  AND timestamp > now() - interval 30 day
GROUP BY properties.capability_name
ORDER BY call_count desc
```

### Query: Skill action rate (did recommendations lead to action?)

```sql
SELECT
  properties.skill_id,
  count(*) as invocations,
  countIf(properties.returned_action = 'flag_campaign') as flag_actions,
  countIf(properties.returned_action = 'escalate') as escalations,
  round(countIf(properties.returned_action != 'no_action') / count(*) * 100, 1) as action_rate,
  avg(properties.output_confidence) as avg_confidence
FROM events
WHERE team_id = :team_id
  AND event = 'skill_completed'
  AND timestamp > now() - interval 30 day
GROUP BY properties.skill_id
ORDER BY invocations desc
```

### Query: Skills with highest error rates (skill drift detection)

```sql
SELECT
  properties.skill_id,
  countIf(event = 'skill_errored') as errors,
  countIf(event = 'skill_invoked') as invocations,
  round(countIf(event = 'skill_errored') / countIf(event = 'skill_invoked') * 100, 1) as error_rate,
  countIf(properties.error_type = 'no_data') as no_data_errors,
  countIf(properties.error_type = 'mcp_timeout') as timeouts
FROM events
WHERE team_id = :team_id
  AND event IN ['skill_invoked', 'skill_errored']
  AND timestamp > now() - interval 90 day
GROUP BY properties.skill_id
HAVING countIf(event = 'skill_invoked') > 5
ORDER BY error_rate desc
```

---

## Alert Conditions

Configure PostHog alerts for these conditions:

| Condition | Alert fires when |
|-----------|-----------------|
| Skill error rate spike | `skill_errored` count > 3 in 1 hour |
| No completions despite invocations | `skill_invoked` > 5 but `skill_completed` = 0 in 2 hours |
| MCP latency degradation | avg `duration_ms` on `mcp_capability_called` > 5000ms for 30 min |
| Skill drift signal | Any skill `error_rate` > 30% over 7 days |

---

## Files in This Skill

- `SKILL.md` — this file
- `references/dashboard-queries.md` — all dashboard SQL queries
- `references/alert-configs.md` — PostHog alert threshold configs
