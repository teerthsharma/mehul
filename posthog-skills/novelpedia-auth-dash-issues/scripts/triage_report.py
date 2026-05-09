#!/usr/bin/env python3
"""
Inkosei/auth-dash Issue Triage Report
Run this to get a quick health check on the issue board.

Usage: python3 triage_report.py
"""
import subprocess
import json
import urllib.request
from collections import Counter

def get_token():
    env_path = '/home/LENOVO/.hermes/novelpedia-profiles/karmicdaoist-197440/.env'
    result = subprocess.run(
        ['sed', '-n', 's/^GITHUB_TOKEN=//p', env_path],
        capture_output=True, text=True
    )
    return result.stdout.strip()

def gh_api(path):
    token = get_token()
    url = f'https://api.github.com{path}'
    req = urllib.request.Request(url, headers={'Authorization': f'token {token}'})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())

print("=" * 60)
print("Inkosei/auth-dash Issue Triage Report")
print("=" * 60)

# 1. Open issues summary
issues = gh_api('/repos/Inkosei/auth-dash/issues?state=open&per_page=200')
open_issues = [i for i in issues if 'pull_request' not in i]
print(f"\n[1] OPEN ISSUES: {len(open_issues)} total (excl PRs)")

# 2. Priority breakdown
p_count = Counter()
type_count = Counter()
area_count = Counter()
unassigned = 0
no_type_or_priority = 0

for i in open_issues:
    labels = [l['name'] for l in i['labels']]
    has_type = any(l.startswith('type:') for l in labels)
    has_priority = any(l.startswith('P:') for l in labels)
    if not has_type or not has_priority:
        no_type_or_priority += 1
    if not i.get('assignees'):
        unassigned += 1
    for l in labels:
        if l.startswith('P:'):
            p_count[l] += 1
        if l.startswith('type:'):
            type_count[l] += 1
        if l.startswith('area:'):
            area_count[l] += 1

print(f"\n[2] PRIORITY BREAKDOWN")
for p, c in sorted(p_count.items(), key=lambda x: x[0][3]):
    print(f"    {p}: {c}")

print(f"\n[3] TYPE BREAKDOWN")
for t, c in sorted(type_count.items(), key=lambda x: -x[1]):
    print(f"    {t}: {c}")

print(f"\n[4] AREA BREAKDOWN")
for a, c in sorted(area_count.items(), key=lambda x: -x[1]):
    print(f"    {a}: {c}")

print(f"\n[5] TRIAGE HEALTH")
print(f"    Unassigned: {unassigned}")
print(f"    Missing type OR priority label: {no_type_or_priority}")

# 3. Critical bugs
bugs = [i for i in open_issues
        if 'type:bug' in [l['name'] for l in i['labels']]]
critical_bugs = [i for i in bugs
                 if 'P:0 Critical' in [l['name'] for l in i['labels']]]
print(f"\n[6] CRITICAL BUGS")
print(f"    Open bugs: {len(bugs)}")
print(f"    P:0 Critical bugs: {len(critical_bugs)}")
for i in critical_bugs[:5]:
    print(f"      #{i['number']} {i['title'][:50]}")

# 4. No-status items on project board (untriaged in board)
print(f"\n[7] ITEMS NOT ON PROJECT BOARD")
print(f"    These items have no Status column in the board:")
print(f"    #9, #59, #22, #7 -- verify if these are still active")

print("\n" + "=" * 60)
print("DONE")
