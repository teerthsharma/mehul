# Observability Dashboard Queries

Pre-built PostHog insight definitions for the agent self-monitoring dashboard.
Each query is ready to paste into PostHog → Insights → New Insight → SQL mode.

---

## 1. Skill Volume & Health (trend)

**Insight type:** Trend
**Event:** `skill_invoked`, `skill_completed`, `skill_errored`
**Interval:** day
**Date range:** Last 30 days

Shows: daily invocation count, completion count, error count.

---

## 2. Error Rate by Skill (bar chart)

**Insight type:** SQL
```sql
SELECT
  properties.skill_id as skill,
  countIf(event = 'skill_errored') as errors,
  countIf(event = 'skill_invoked') as total,
  round(countIf(event = 'skill_errored') / countIf(event = 'skill_invoked') * 100, 1) as error_rate_pct
FROM events
WHERE team_id = :team_id
  AND event IN ['skill_invoked', 'skill_errored']
  AND timestamp > now() - interval 30 day
GROUP BY skill
HAVING total > 3
ORDER BY error_rate_pct desc
LIMIT 20
```

---

## 3. MCP Capability Usage (bar chart)

**Insight type:** SQL
```sql
SELECT
  properties.capability_name as capability,
  count(*) as call_count,
  round(countIf(properties.cache_hit = true) / count(*) * 100, 1) as cache_hit_rate,
  avg(properties.duration_ms) as avg_duration_ms
FROM events
WHERE team_id = :team_id
  AND event = 'mcp_capability_called'
  AND timestamp > now() - interval 30 day
GROUP BY capability
ORDER BY call_count desc
```

---

## 4. Token Cost by Skill (bar chart)

**Insight type:** SQL
```sql
SELECT
  properties.skill_id as skill,
  avg(properties.tokens_consumed) as avg_tokens,
  max(properties.tokens_consumed) as max_tokens,
  sum(properties.tokens_consumed) as total_tokens,
  count(*) as invocations
FROM events
WHERE team_id = :team_id
  AND event = 'skill_completed'
  AND timestamp > now() - interval 30 day
GROUP BY skill
ORDER BY total_tokens desc
```

---

## 5. Skill Action Rate (did skills drive actions?)

**Insight type:** SQL
```sql
SELECT
  properties.skill_id as skill,
  count(*) as completions,
  countIf(properties.returned_action = 'flag_campaign') as flag_actions,
  countIf(properties.returned_action = 'escalate') as escalations,
  round(countIf(properties.returned_action != 'no_action') / count(*) * 100, 1) as action_rate
FROM events
WHERE team_id = :team_id
  AND event = 'skill_completed'
  AND timestamp > now() - interval 30 day
GROUP BY skill
ORDER BY action_rate asc
```

---

## 6. Routing Confidence Distribution (histogram)

**Insight type:** SQL
```sql
SELECT
  floor(properties.router_confidence * 10) / 10 as confidence_bucket,
  count(*) as count
FROM events
WHERE team_id = :team_id
  AND event = 'skill_invoked'
  AND timestamp > now() - interval 30 day
GROUP BY confidence_bucket
ORDER BY confidence_bucket
```

---

## 7. Average Skill Duration by Skill (bar chart)

**Insight type:** SQL
```sql
SELECT
  properties.skill_id as skill,
  avg(properties.duration_ms) as avg_duration_ms,
  max(properties.duration_ms) as p95_duration_ms,
  count(*) as invocations
FROM events
WHERE team_id = :team_id
  AND event = 'skill_completed'
  AND timestamp > now() - interval 30 day
GROUP BY skill
ORDER BY avg_duration_ms desc
```

---

## 8. Escalation Flow ( sankey / user flow )

**Insight type:** PostHog user flow
**Start point:** `skill_invoked`
**Follow path:** `skill_escalated` → `skill_invoked` (next skill)
**Date range:** Last 30 days

Shows which skills escalate to which other skills and how frequently.
