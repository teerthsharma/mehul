---
name: novelpedia-discord-dm-channel
category: novelpedia
description: Discord DM channel issue where bot cannot send proactive DMs even after user initiates. Use channel pings as workaround.
---

# Novelpedia Discord DM Channel — Known Issue & Workaround

## Problem
When a user DM's the bot to initiate a pairing code flow, the bot receives the message but the DM channel is NOT cached for outbound use. Sending `send_message discord:<user_id>` fails with "channel not found" even though the user has an active DM thread with the bot.

This happens because Discord bot DM channels are only cached when the **bot sends** a message to the user — not merely when the user messages the bot.

## Workaround
Until the DM channel is established from the bot side, use public channel pings instead:
- Ping user in `#exec-updates` or `#staff-announcements` using their Discord ID
- Example: `<@378499318396747779>`

## Fix
Have the user DM the bot again. If the bot has `MESSAGE CONTENT INTENT` enabled, it will auto-reply and cache the DM channel on the outbound side. After that, `send_message discord:<user_id>` works.

## Symptoms
- `send_message discord:378499318396747779` → fails "channel not found"
- User clearly has an active DM thread (they got the pairing code through it)
- Profile creation / pairing approval works fine, only outbound DMs fail
