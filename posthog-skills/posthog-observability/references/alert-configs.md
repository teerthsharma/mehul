# PostHog Alert Configurations

Configure these alerts in `app.posthog.com/settings/alerts`.

---

## Alert 1: Skill Error Rate Spike

**Trigger:** More than 3 `skill_errored` events in any 60-minute window.
**Action:** Send Slack/Discord webhook to #analytics-alerts.
**Purpose:** Catches MCP outages or skill definition breakage early.

```json
{
  "name": "Skill Error Rate Spike",
  "condition": "count of skill_errored > 3",
  "window": "60 minutes",
  "target": "app.posthog.com/settings/alerts",
  "action_webhook": "https://discord.com/api/webhooks/..."
}
```

---

## Alert 2: Skill Drift Detection

**Trigger:** Any skill with error_rate > 30% over rolling 7 days.
**Action:** Write to #skill-audit Slack channel.
**Purpose:** Identifies skills whose metric references or PostHog queries are broken.

Note: This is a scheduled PostHog insight alert, not a real-time alert.
Set it on the "Error Rate by Skill" insight.

---

## Alert 3: MCP Latency Degradation

**Trigger:** Average `duration_ms` on `mcp_capability_called` > 5000ms for 30 minutes.
**Action:** Write to #analytics-alerts.
**Purpose:** PostHog API degradation affecting all skills.

---

## Alert 4: North-Star Metric Critical Breach

**Trigger:** `chapter_activation_rate < 15%` (critical threshold).
**Action:** Page founder directly (urgent Slack DM).
**Purpose:** Core business metric breach requires immediate attention.

---

## Alert 5: No Skill Completions Despite Invocations

**Trigger:** `skill_invoked > 5` but `skill_completed = 0` in any 2-hour window.
**Action:** Write to #analytics-alerts.
**Purpose:** Catches a stuck skill loop or complete MCP failure.
