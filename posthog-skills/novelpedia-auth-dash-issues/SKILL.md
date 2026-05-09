---
name: novelpedia-auth-dash-issues
description: "Issue tracker operations for Inkosei/auth-dash -- labels, project board (GitHub Projects V2), triage workflow, creation, and updates. Repo: github.com/Inkosei/auth-dash. Project board: github.com/orgs/Inkosei/projects/2"
category: novelpedia
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [Novelpedia, Inkosei, auth-dash, GitHub Issues, GitHub Projects, Triage]
    related_skills: [github-issues, github-pr-workflow, auth-dash-git-sync]
---

# Inkosei/auth-dash -- Issue Tracker Guide

Repository: `Inkosei/auth-dash`
Remote: `https://github.com/Inkosei/auth-dash.git`
Project Board: https://github.com/orgs/Inkosei/projects/2 (org-level, 270 items)
GraphQL Project ID: `PVT_kwDODORZhc4BJ9cJ`
Legacy Projects API: `https://api.github.com/orgs/Inkosei/projects/2`

**Important:** Do NOT use `novelpedia/auth-dash` -- the repo is under the `Inkosei` org, not `novelpedia`.

---

## Labels Reference

### Priority Labels (P:x)
Always apply alongside a `type:*` label.

| Label | Color | Use For |
|-------|-------|---------|
| `P:0 Critical` | red #b60205 | Production broken, data loss, security breach |
| `P:1 High` | orange #d93f0b | Important for next release, blocks core flows |
| `P:2 Medium` | green #0e8a16 | Standard priority, planned work |
| `P:3 Low` | light green #c2e0c6 | Minor issues, nice-to-haves |

### Area Labels (area:)
Marks which part of the stack is affected.

| Label | Color | Use For |
|-------|-------|---------|
| `area:backend` | purple #5319e7 | Django/API/server-side code |
| `area:frontend` | blue #1d76db | React/reader/author dashboard UI |
| `area:infra` | coral #f9d0c4 | DevOps, Docker, AWS, CI/CD |

### Type Labels (type:)
| Label | Color | Use For |
|-------|-------|---------|
| `type:bug` | red #d73a4a | Something isn't working as expected |
| `type:feature` | cyan #a2eeef | New functionality |
| `type:chore` | green #c2e0c6 | Maintenance, dependencies, setup |
| `type:design` | gray-blue #bfdadc | UI/UX design tasks |
| `type:epic` | dark blue #3E4B9E | High-level roadmap item (multi-issue) |
| `enhancement` | gray #ededed | Improvement to existing feature |

### Status Labels
| Label | Color | Use For |
|-------|-------|---------|
| `status:blocked` | black #000000 | Cannot proceed, waiting on something |
| `status:needs-design` | light blue #bfdadc | Waiting on design decisions |

### Other Labels
| Label | Color | Use For |
|-------|-------|---------|
| `onboarding` | brown #c27530 | Onboarding-related tasks |
| `reader-app` | gray #ededed | Reader application feature |

---

## Milestones (10 Phases)

Issues are organized into 10 delivery phases:

| Milestone | Scope | Items |
|-----------|-------|-------|
| Phase 1: Foundation MVP | Core auth, reader/author basics | COMPLETE (31/32 done) |
| Phase 2: Reader Engagement | Reading experience, discovery, karma/ranking | ACTIVE -- #533 karma ranking filed |
| Phase 3: Monetization V1 | Subscription, payments, gating | ~24 |
| Phase 4: Advanced Discovery | Search, recommendations, filters | ~37 |
| Phase 5: Governance | Moderation, reporting, abuse | ~61 |
| Phase 6: Analytics | Dashboards, metrics, insights | ~69 |
| Phase 7: Automation | Notifications, emails, bots | ~57 |
| Phase 8: Advanced Monetization | Dynamic pricing, affiliate, tiered | ~29 |
| Phase 9: Global Expansion | i18n, localization, regional compliance | ~23 |
| Phase 10: Production Hardening | Security, monitoring, resilience | ~8 |

Set the milestone when creating an issue. Phase 1 is essentially complete -- do not add new items there.

---

## Project Board

**Board URL:** https://github.com/orgs/Inkosei/projects/2

**Status Column Options:**

| Column | Color | When to Move |
|--------|-------|-------------|
| Todo | green | Issue is triaged and ready to work on |
| In Progress | yellow | Someone is actively working it |
| Done | purple | Implementation complete, merged/deployed |

**Other Project Fields:** `Assignees`, `Repository` (defaults to `auth-dash`), `Milestone`, `Priority` (Critical/High/Medium -- separate from P:x labels)

**Critical Rule:** The `Status` column (Todo/In Progress/Done) is the PRIMARY workflow state. Keep it in sync with reality. The `Priority` project field (Critical/High/Medium) should match the P:x label.

---

## How to Create an Issue

### Bug Report Template
```
**Description:** What's broken and what should happen instead.

**Steps to Reproduce:**
1.
2.
3.

**Actual Behavior:** What actually happens

**Expected Behavior:** What should happen

**Environment:**
- OS/Browser:
- Version:
```

### Feature Request Template
```
**Feature:** What you want built

**Motivation:** Why this matters for users or the business

**Proposed Solution:** How you imagine it working

**Alternatives Considered:** Other approaches
```

### Required Labels (minimum)
Every issue should have:
- At minimum: one `type:*` label (`type:bug`, `type:feature`, `type:chore`, `type:design`)
- At minimum: one `P:x` priority label (if it's real work, it has a priority)
- Optional: `area:*` label to mark the affected stack

### Optional but Recommended
- `Milestone` set to the appropriate phase
- `Assignee` if the owner is known
- **Status: Todo** in the project board (must be set manually after creation)

### Via GitHub API (curl)
```bash
# Get token first
TOKEN=$(sed -n 's/^GITHUB_TOKEN=//p' ~/.hermes/novelpedia-profiles/karmicdaoist-197440/.env)

# Create issue
curl -s -X POST \
  -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  https://api.github.com/repos/Inkosei/auth-dash/issues \
  -d '{
    "title": "fix: description of the bug",
    "body": "**Description:** ...\n\n**Steps to Reproduce:**\n1. ...\n\n**Expected:** ...\n**Actual:** ...",
    "labels": ["type:bug", "P:1 High", "area:frontend"],
    "milestone": 2
  }' | python3 -c "import sys,json; i=json.load(sys.stdin); print(f\"Created: #{i['number']} {i['html_url']}\")"
```

### Via GitHub CLI (if installed)
```bash
gh issue create \
  --title "fix: description" \
  --body "..." \
  --label "type:bug,P:1 High,area:frontend" \
  --milestone "Phase 2: Reader Engagement" \
  --repo Inkosei/auth-dash
```

---

## Adding Issues to the Project Board

After creating an issue, you must manually add it to the project board. The project board does NOT auto-populate from issue creation.

### Via GraphQL (recommended for automation)
```bash
TOKEN=$(sed -n 's/^GITHUB_TOKEN=//p' ~/.hermes/novelpedia-profiles/karmicdaoist-197440/.env)

# Add issue to project by its GitHub node_id
curl -s -X POST https://api.github.com/graphql \
  -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { addProjectV2ItemById(input: {projectId: \"PVT_kwDODORZhc4BJ9cJ\", itemId: \"$(curl -s -H \"Authorization: token $TOKEN\" https://api.github.com/repos/Inkosei/auth-dash/issues/'$ISSUE_NUM' | python3 -c \"import sys,json; print(json.load(sys.stdin)['\"'node_id'\"'])\")\" }) { item { id } } }"
  }'
```

### Via Browser (fastest)
1. Open the issue at `https://github.com/Inkosei/auth-dash/issues/<N>`
2. Right sidebar -> Projects -> select "Issue Tracker"
3. Set Status to `Todo`

---

## Updating Issue Status

### Moving a Project Card (via GraphQL)
Updates the board column. Get the item ID from the GraphQL query first.

```bash
TOKEN=$(sed -n 's/^GITHUB_TOKEN=//p' ~/.hermes/novelpedia-profiles/karmicdaoist-197440/.env)

# Status field option IDs
TODO_ID="f75ad846"
IN_PROGRESS_ID="47fc9ee4"
DONE_ID="98236657"

# Move issue to In Progress
curl -s -X POST https://api.github.com/graphql \
  -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { updateProjectV2ItemFieldValue(input: {projectId: \"PVT_kwDODORZhc4BJ9cJ\", itemId: \"$ITEM_ID\", fieldId: \"PVTSSF_lADODORZqc4BJ9cJzg5-DZc\", value: {singleSelectOptionId: \"'$IN_PROGRESS_ID'\"} }) { project { id } } }"
  }'
```

### Updating Labels (via REST API)
```bash
TOKEN=$(sed -n 's/^GITHUB_TOKEN=//p' ~/.hermes/novelpedia-profiles/karmicdaoist-197440/.env)

# Replace all labels
curl -s -X POST \
  -H "Authorization: token $TOKEN" \
  https://api.github.com/repos/Inkosei/auth-dash/issues/461/labels \
  -d '{"labels": ["type:bug", "P:0 Critical", "area:backend"]}' | python3 -c "import sys,json; print('Labels:', [l['name'] for l in json.load(sys.stdin)])"

# Add single label
curl -s -X POST \
  -H "Authorization: token $TOKEN" \
  https://api.github.com/repos/Inkosei/auth-dash/issues/461/labels \
  -d '{"labels": ["status:blocked"]}'

# Remove label
curl -s -X DELETE \
  -H "Authorization: token $TOKEN" \
  https://api.github.com/repos/Inkosei/auth-dash/issues/461/labels/status:needs-design
```

### Updating Assignee
```bash
TOKEN=$(sed -n 's/^GITHUB_TOKEN=//p' ~/.hermes/novelpedia-profiles/karmicdaoist-197440/.env)

# Assign
curl -s -X POST \
  -H "Authorization: token $TOKEN" \
  https://api.github.com/repos/Inkosei/auth-dash/issues/461/assignees \
  -d '{"assignees": ["ArcSol23"]}'

# Unassign
curl -s -X DELETE \
  -H "Authorization: token $TOKEN" \
  https://api.github.com/repos/Inkosei/auth-dash/issues/461/assignees \
  -d '{"assignees": ["ArcSol23"]}'
```

### Updating Milestone
```bash
TOKEN=$(sed -n 's/^GITHUB_TOKEN=//p' ~/.hermes/novelpedia-profiles/karmicdaoist-197440/.env)

# List milestones to get ID
curl -s -H "Authorization: token $TOKEN" \
  https://api.github.com/repos/Inkosei/auth-dash/milestones | \
  python3 -c "import sys,json; [print(f\"#{m['number']} {m['title']}\") for m in json.load(sys.stdin)]"

# Set milestone (N = milestone number)
curl -s -X PATCH \
  -H "Authorization: token $TOKEN" \
  https://api.github.com/repos/Inkosei/auth-dash/issues/461 \
  -d '{"milestone": 3}'
```

### Closing an Issue
```bash
TOKEN=$(sed -n 's/^GITHUB_TOKEN=//p' ~/.hermes/novelpedia-profiles/karmicdaoist-197440/.env)
curl -s -X PATCH \
  -H "Authorization: token $TOKEN" \
  https://api.github.com/repos/Inkosei/auth-dash/issues/461 \
  -d '{"state": "closed", "state_reason": "completed"}'
```

---

## Triage Workflow

### Triage Definition
An issue is **triaged** when it has ALL of:
1. A `type:*` label
2. A `P:x` priority label (or explicitly marked P:3 Low)
3. A `Milestone` assigned
4. An `Assignee` (or labeled unassigned but explicitly routed)
5. **Status = Todo** in the project board

### Triage Commands

**Find completely untriaged issues** (no type, no priority, no milestone):
```bash
TOKEN=$(sed -n 's/^GITHUB_TOKEN=//p' ~/.hermes/novelpedia-profiles/karmicdaoist-197440/.env)

curl -s -H "Authorization: token $TOKEN" \
  "https://api.github.com/repos/Inkosei/auth-dash/issues?state=open&per_page=100" | \
  python3 -c "
import sys, json
issues = [i for i in json.load(sys.stdin) if 'pull_request' not in i]
untriaged = []
for i in issues:
    labels = [l['name'] for l in i['labels']]
    has_type = any(l.startswith('type:') for l in labels)
    has_priority = any(l.startswith('P:') for l in labels)
    has_milestone = i.get('milestone')
    if not (has_type and has_priority and has_milestone):
        untriaged.append(f\"  #{i['number']}  {i['title'][:60]}  labels={[l for l in labels if l.startswith('type:') or l.startswith('P:')]}\")
print(f'Untriaged: {len(untriaged)}/{len(issues)}')
for u in untriaged[:20]:
    print(u)
"
```

**Find issues not on the project board** (no Status field set):
```bash
# These 4 items currently have no Status in the board:
# #9, #59, #22, #7 -- all older issues needing review
```

**Find all open `type:bug` bugs**:
```bash
TOKEN=$(sed -n 's/^GITHUB_TOKEN=//p' ~/.hermes/novelpedia-profiles/karmicdaoist-197440/.env)

curl -s -H "Authorization: token $TOKEN" \
  "https://api.github.com/repos/Inkosei/auth-dash/issues?state=open&labels=type:bug&per_page=100" | \
  python3 -c "
import sys, json
issues = json.load(sys.stdin)
print(f'Open bugs: {len(issues)}')
for i in issues:
    labels = [l['name'] for l in i['labels']]
    priority = [l for l in labels if l.startswith('P:')]
    assignee = (i.get('assignee') or {}).get('login', 'unassigned')
    print(f\"  #{i['number']}  {i['title'][:55]}  {priority}  @{assignee}\")
"
```

**Find all `P:0 Critical` open issues**:
```bash
TOKEN=$(sed -n 's/^GITHUB_TOKEN=//p' ~/.hermes/novelpedia-profiles/karmicdaoist-197440/.env)

curl -s -H "Authorization: token $TOKEN" \
  "https://api.github.com/repos/Inkosei/auth-dash/issues?state=open&labels=P:0%20Critical&per_page=100" | \
  python3 -c "
import sys, json
issues = json.load(sys.stdin)
print(f'Critical open: {len(issues)}')
for i in issues:
    labels = [l['name'] for l in i['labels']]
    types = [l for l in labels if l.startswith('type:')]
    print(f\"  #{i['number']}  {i['title'][:55]}  {types}\")
"
```

**Find all unassigned open issues**:
```bash
TOKEN=$(sed -n 's/^GITHUB_TOKEN=//p' ~/.hermes/novelpedia-profiles/karmicdaoist-197440/.env)

curl -s -H "Authorization: token $TOKEN" \
  "https://api.github.com/repos/Inkosei/auth-dash/issues?state=open&per_page=100" | \
  python3 -c "
import sys, json
issues = [i for i in json.load(sys.stdin) if 'pull_request' not in i]
unassigned = [i for i in issues if not i.get('assignees')]
print(f'Unassigned: {len(unassigned)}/{len(issues)}')
for i in unassigned[:15]:
    labels = [l['name'] for l in i['labels'][:3]]
    print(f\"  #{i['number']}  {i['title'][:55]}  {labels}\")
"
```

**Full project board triage report** (via GraphQL):
```bash
TOKEN=$(sed -n 's/^GITHUB_TOKEN=//p' ~/.hermes/novelpedia-profiles/karmicdaoist-197440/.env)

curl -s -X POST https://api.github.com/graphql \
  -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ node(id: \"PVT_kwDODORZhc4BJ9cJ\") { ... on ProjectV2 { title items(first: 100) { totalCount nodes { id type content { ... on Issue { number title state assignees(first: 3) { nodes { login } } labels(first: 5) { nodes { name } } } } fieldValues(first: 10) { nodes { __typename ... on ProjectV2ItemFieldSingleSelectValue { field { name } name } ... on ProjectV2ItemFieldMilestoneValue { field { name } milestone { title } } } } } } } } }"}' | \
  python3 -c "
import sys, json
from collections import Counter
resp = json.load(sys.stdin)
proj = resp['data']['node']
items = proj['items']['nodes']
status = Counter()
no_status = 0
for i in items:
    fvs = i.get('fieldValues', {}).get('nodes', [])
    s = 'no-status'
    for fv in fvs:
        if fv['__typename'] == 'ProjectV2ItemFieldSingleSelectValue':
            fname = (fv.get('field') or {}).get('name', '')
            if fname == 'Status':
                s = fv.get('name', 'no-status')
    status[s] += 1
print(f'Project: {proj[\"title\"]} -- {proj[\"items\"][\"totalCount\"]} total items')
for k, v in sorted(status.items(), key=lambda x: -x[1]):
    print(f'  {k}: {v}')
"
```

---

## Quick Reference: Token Setup

All API calls require a GitHub PAT. The token is stored at:
```
~/.hermes/novelpedia-profiles/karmicdaoist-197440/.env
```
Variable: `GITHUB_TOKEN=ghp_...`

Extract it with:
```bash
TOKEN=$(sed -n 's/^GITHUB_TOKEN=//p' ~/.hermes/novelpedia-profiles/karmicdaoist-197440/.env)
```

---

## Common Team Members (for assignee lookups)
Known active assignees on this repo:
- `KarmicDaoist` -- founder/lead
- `ArcSol23` -- lead backend developer
- `Heavens-Daoist` -- frontend/reader app
- `Debyte404` -- design

---

## Anti-Patterns to Avoid

1. **Creating issues without `type:*` label** -- makes triage impossible
2. **Setting `P:0 Critical` on non-production issues** -- dilutes the meaning
3. **Leaving Status = Todo forever** -- move to In Progress when working, Done when shipped
4. **Adding items to milestones 1-3** -- Phase 1 is COMPLETE; Phase 2 is active; dont add roadmap items to phases 1-2 anymore -- use Phase 3+ for new work
5. **Using `enhancement` instead of `type:feature`** -- `enhancement` is legacy; prefer `type:feature`
6. **Not adding issues to the project board** -- the board is the sprint view; orphaned issues are invisible
