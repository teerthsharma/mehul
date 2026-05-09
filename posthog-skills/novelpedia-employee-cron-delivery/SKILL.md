---
name: novelpedia-employee-cron-delivery
description: Set up cron job delivery to Novelpedia employee profiles (not origin/founder chat)
---

# Novelpedia Employee Cron Delivery

## Problem
Cron jobs for Novelpedia employees were delivering to the founder's chat (`origin`) instead of the employee's profile channel.

## Solution
1. Find employee profile: `ls ~/novelpedia-profiles/` — profiles named `{slug}-{id}`
2. Read profile: `cat ~/novelpedia-profiles/{slug}-{id}/profile.json` — contains `delivery_channel`, `platform`, and platform-specific IDs (e.g. `discord_user_id`)
3. Update cron job delivery: `honcho job update {job_id} --delivery {platform}:{id}` (e.g. `discord:1320668958893801504`)

## Known Profiles
- FateEscaper: slug `fateescaper-801504`, Discord user ID `1320668958893801504`

## Pitfall
Discord API blocks proactive DMs. Employee must have messaged the bot first to open the DM channel. If delivery fails, fall back to a Discord channel ping instead.
