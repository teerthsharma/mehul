---
name: novelpedia-github-profile-setup
description: Store GitHub credentials (PAT or SSH key) inside a specific Novelpedia employee profile at ~/.hermes/novelpedia-profiles/<profile>/, completely isolated from global Hermes config and other employee profiles. For when you need to configure GitHub auth for a specific Novelpedia team member without leaking credentials to other profiles.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [novelpedia, github, authentication, profiles, security]
    related_skills: [github-auth, novelpedia-employee-onboarding]
---

# Novelpedia GitHub Profile Credential Setup

When a Novelpedia employee needs GitHub access (PAT or SSH), store their credentials **only in their own profile directory** — not in global Hermes config (`~/.hermes/.env`, `~/.git-credentials`, `~/.gitconfig`) and not in other employees' profiles.

## Architecture

Each Novelpedia employee has an isolated profile at:
```
~/.hermes/novelpedia-profiles/<profile-id>/
├── .env              ← API keys isolated here
├── .git-credentials  ← GitHub PAT credentials
├── .gitconfig        ← Git identity + credential helper
├── memories/
├── sessions/
├── skills/
└── ...
```

The profile map (`~/.hermes/novelpedia-profiles-map.json`) maps Discord IDs to profile directories.

## Setup Steps

### Step 1: Identify the Correct Profile

```bash
# Check the profile map
cat ~/.hermes/novelpedia-profiles-map.json

# List all profiles
ls ~/.hermes/novelpedia-profiles/
```

### Step 2: Write GitHub PAT to Profile's .env

```python
import os

profile_base = "/home/LENOVO/.hermes/novelpedia-profiles/<profile-id>"
profile_env = os.path.join(profile_base, ".env")

with open(profile_env) as f:
    existing = f.read()

if "GITHUB_TOKEN" not in existing:
    with open(profile_env, "a") as f:
        f.write(f"\nGITHUB_TOKEN={pat_token}\n")
```

### Step 3: Write Git Credentials to Profile's .git-credentials

```python
import os
os.makedirs(profile_base, exist_ok=True)

creds_path = os.path.join(profile_base, ".git-credentials")
with open(creds_path, "w") as f:
    f.write(f"https://{github_username}:{pat_token}@github.com\n")
os.chmod(creds_path, 0o600)
```

### Step 4: Write Profile .gitconfig

```python
profile_gitconfig = os.path.join(profile_base, ".gitconfig")
with open(profile_gitconfig, "w") as f:
    f.write(f"""[user]
    name = {github_username}
    email = {email}
[credential "https://github.com"]
    helper = store --file {profile_base}/.git-credentials
""")
```

### Step 5: Verify Isolation

```python
import subprocess

# Verify PAT NOT in global .env
with open("/home/LENOVO/.hermes/.env") as f:
    global_has_token = any(
        l.strip().startswith('GITHUB_TOKEN=') and not l.strip().startswith('#')
        for l in f.read().split('\n')
    )
assert not global_has_token, "PAT leaked to global .env!"

# Verify global git-credentials removed
assert not os.path.exists(os.path.expanduser("~/.git-credentials"))

# Verify global credential.helper unset
result = subprocess.run(
    ["git", "config", "--global", "credential.helper"],
    capture_output=True, text=True
)
assert not result.stdout.strip(), "Global credential.helper still active!"

# Verify PAT works from profile
env = os.environ.copy()
env['HOME'] = profile_base
result = subprocess.run(
    ["git", "ls-remote", "https://github.com/NousResearch/hermes-agent.git"],
    capture_output=True, text=True, timeout=15, env=env
)
assert result.returncode == 0, "GitHub auth not working from profile"
```

## Why This Matters

Other Novelpedia employee profiles (Shaan, Sajid, etc.) must NOT have access to your GitHub PAT. The Novelpedia profiles all run as the same Linux user, so machine-level credentials (global `~/.git-credentials`, global `credential.helper`) would be readable by all profiles. Only profile-scoped credentials keep them isolated.

## SSH Key Alternative

If the employee prefers SSH instead of PAT:

```python
# Generate key in profile directory
ssh_dir = os.path.join(profile_base, ".ssh")
os.makedirs(ssh_dir, mode=0o700, exist_ok=True)

# Add public key to GitHub at: https://github.com/settings/keys

# Write SSH config scoped to github.com
ssh_config = os.path.join(ssh_dir, "config")
with open(ssh_config, "w") as f:
    f.write(f"""Host github.com
    HostName github.com
    User git
    IdentityFile {ssh_dir}/id_ed25519
    IdentitiesOnly yes
""")
```
