---
name: auth-dash-issues
description: "Issue tracker and project board conventions for Inkosei/auth-dash — Novelpedia's auth-dash repo. Documents the GitHub Projects V2 board (Issue Tracker), full label schema, 10-phase milestone system, triage workflow, and Python/GraphQL queries for auditing."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [Novelpedia, auth-dash, Issue Tracker, Triage, GitHub Projects]
prerequisites:
  env_vars: [GITHUB_TOKEN]
  commands: [python3]
---

# auth-dash Issue Tracker — Conventions & Triage

## Repo Identity

- **Repo:** `Inkosei/auth-dash` (under Inkosei org, NOT novelpedia org)
- **Remote:** `https://github.com/Inkosei/auth-dash.git`
- **Default branch:** `main`
- **Workspace:** `/home/LENOVO/.hermes/novelpedia-profiles/karmicdaoist-197440/workspace/auth-dash`
- **Issue Tracker:** https://github.com/orgs/Inkosei/projects/2 (GitHub Projects V2)

> **Note:** `terminal()` fails in the auth-dash workspace. Use `execute_code` with Python `subprocess` instead. See `auth-dash-git-sync` skill for the workaround pattern.

## Project Board: Issue Tracker (Projects V2)

- **Project ID:** `PVT_kwDODORZhc4BJ9cJ`
- **Type:** GitHub Projects V2 (org-level, under Inkosei org)
- **Total items:** 270

### Status Columns

| Column | Color | Option ID |
|--------|-------|-----------|
| Todo | GREEN | `f75ad846` |
| In Progress | YELLOW | `47fc9ee4` |
| Done | PURPLE | `98236657` |

### Project Custom Fields

| Field | Type |
|-------|------|
| Assignees | User (multi-select) |
| Repository | Text (always "auth-dash") |
| Milestone | Milestone (linked to GitHub milestones) |
| Status | Single-select (Todo/In Progress/Done) |
| Priority | Single-select (Critical/High/Medium) |

**Priority field options:** Critical, High, Medium

## Label Schema (20 labels)

### Priority Labels (P:x prefix)

| Label | Color | Hex | Description |
|-------|-------|-----|-------------|
| `P:0 Critical` | red | `#b60205` | Urgent, production broken |
| `P:1 High` | orange | `#d93f0b` | Important for next release |
| `P:2 Medium` | green | `#0e8a16` | Standard priority |
| `P:3 Low` | light green | `#c2e0c6` | Minor issue, low priority |

### Area Labels (area: prefix)

| Label | Color | Hex | Description |
|-------|-------|-----|-------------|
| `area:backend` | purple | `#5319e7` | Server-side/API code |
| `area:frontend` | blue | `#1d76db` | Client-side code |
| `area:infra` | coral | `#f9d0c4` | DevOps, Docker, AWS |

### Type Labels (type: prefix)

| Label | Color | Hex | Description |
|-------|-------|-----|-------------|
| `type:bug` | red | `#d73a4a` | Something isn't working |
| `type:feature` | cyan | `#a2eeef` | New functionality |
| `type:chore` | green | `#c2e0c6` | Maintenance, dependencies, setup |
| `type:design` | gray | `#bfdadc` | UI/UX design tasks |
| `type:epic` | dark blue | `#3E4B9E` | High-level roadmap item |

### Status Labels

| Label | Color | Description |
|-------|-------|-------------|
| `status:blocked` | black | Blocked on something |
| `status:needs-design` | light blue | Needs design input |

### Other Labels

- `enhancement`
- `onboarding`
- `reader-app`

## Milestones (10 Phases)

All phases are open unless noted.

| # | Phase | Open | Closed |
|---|-------|------|--------|
| 1 | Phase 1: Foundation MVP | 1 | 34 |
| 2 | Phase 2: Reader Engagement | 33 | 0 |
| 3 | Phase 3: Monetization V1 | 22 | 2 |
| 4 | Phase 4: Advanced Discovery | 25 | 0 |
| 5 | Phase 5: Governance | 31 | 0 |
| 6 | Phase 6: Analytics | 35 | 0 |
| 7 | Phase 7: Automation | 29 | 0 |
| 8 | Phase 8: Advanced Monetization | 30 | 0 |
| 9 | Phase 9: Global Expansion | 23 | 4 |
| 10 | Phase 10: Production Hardening | 8 | 3 |

## Team Members

Known assignees from project items:
- `ArcSol23` — ArcSol (lead dev)
- `KarmicDaoist` — Mehul (founder)
- `Heavens-Daoist`
- `Debyte404`

## Triage Queries

### Find triage candidates (unassigned + no P:x label)

```python
import subprocess, json, urllib.request

TOKEN = subprocess.run(
    ['sed', '-n', 's/^GITHUB_TOKEN=//p',
     '/home/LENOVO/.hermes/novelpedia-profiles/karmicdaoist-197440/.env'],
    capture_output=True, text=True
).stdout.strip()

url = 'https://api.github.com/repos/Inkosei/auth-dash/issues?state=open&per_page=100'
req = urllib.request.Request(url, headers={'Authorization': f'token {TOKEN}'})
issues = json.loads(urllib.request.urlopen(req).read())

triage = [i for i in issues if 'pull_request' not in i
          and not i.get('assignee')
          and not any(l['name'].startswith('P:') for l in i['labels'])]
print(f"Triage candidates: {len(triage)}")
for i in triage:
    print(f"  #{i['number']}  {i['title'][:60]}")
```

### Count by Status column (project board — see github-projects-v2 skill for full query)

The project board GraphQL query pattern is documented in the `github-projects-v2` skill.

## Creating Issues That Populate the Board

When creating an issue, these map to project fields:
- **Milestone** — link to one of the 10 phases
- **Labels** — P:x, area:, type: labels
- **Assignee** — maps to Assignees field in project

The `Priority` project field (Critical/High/Medium) is **separate** from P:x labels — keep them in sync manually.

## Known Issues (May 2026)

1. **0 items in "In Progress"** — the board is either Todo or Done. Either nothing is actively being worked, or the team does not update Status during work.
2. **4 orphan items** with no Status — not on the board workflow.
3. **229 issues in Phases 4-10** all marked Todo — appears to be a roadmap backlog rather than sprintable work.
4. **Phase 1 is essentially complete** — 31/32 done.
5. **~147 open issues not in project** — only ~96 of 243 open issues are in the project board. Rest live as raw GitHub issues.

## Python Query Boilerplate

```python
import subprocess, json, urllib.request

TOKEN = subprocess.run(
    ['sed', '-n', 's/^GITHUB_TOKEN=//p',
     '/home/LENOVO/.hermes/novelpedia-profiles/karmicdaoist-197440/.env'],
    capture_output=True, text=True
).stdout.strip()

def gh_api(path):
    url = f'https://api.github.com{path}'
    req = urllib.request.Request(url, headers={'Authorization': f'token {TOKEN}'})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())

def gh_gql(query):
    url = 'https://api.github.com/graphql'
    data = json.dumps({'query': query}).encode()
    req = urllib.request.Request(url, data=data, headers={
        'Authorization': f'token {TOKEN}',
        'Content-Type': 'application/json'
    })
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())

OWNER = 'Inkosei'
REPO = 'auth-dash'
PROJECT_ID = 'PVT_kwDODORZhc4BJ9cJ'
```
