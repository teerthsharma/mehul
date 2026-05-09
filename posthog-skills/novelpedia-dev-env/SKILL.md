---
name: novelpedia-dev-env
description: Development environment paths and setup for Novelpedia's hermes-agent and related repos.
---

# Novelpedia Dev Environment

## Key Directories

| Tool | Path |
|------|------|
| Git | `/usr/bin/git` v2.34.1 |
| Node/npm | `/home/LENOVO/.hermes/node/bin/{node,npm}` |
| Python 3.11 venv | `hermes-agent/venv/bin/python3` |
| `repo` (AOSP) | **NOT installed** |

### Novelpedia Source Code
**Location:** `~/novelpedia-profiles/<profile-id>/workspace/auth-dash/`

The Novelpedia codebase (auth-dash monorepo) lives as a **workspace subdirectory inside a user profile directory** — NOT at a top-level project path. Auth-dash is the main repo containing:
- `apps/author-dashboard/` — Author-facing React frontend
- `apps/reader-app/` — Reader-facing React frontend
- `backend/` — Django backend (apps/authors, apps/users, etc.)

To find it from any profile:
```python
import os
profiles = '/home/LENOVO/.hermes/novelpedia-profiles/'
for pid in os.listdir(profiles):
    workspace = os.path.join(profiles, pid, 'workspace', 'auth-dash')
    if os.path.exists(workspace):
        print(f"Found auth-dash at {workspace}")
        break
```

Common profile IDs: `karmicdaoist-197440` (founder/Mehul).

### Other Paths
- **Hermes agent repo**: `/home/LENOVO/.hermes/hermes-agent/` (git repo, branch `main`, clean)
- **Honcho repo**: `/home/LENOVO/.hermes/services/honcho/` (git repo)
- **Novelpedia profiles**: `/home/LENOVO/novelpedia-profiles/`
- **Novelpedia config**: `/home/LENOVO/.novelpedia/`
- **Setup script**: `/home/LENOVO/.hermes/hermes-agent/setup-hermes.sh`
| Novelpedia profiles | `/home/LENOVO/novelpedia-profiles/` |
| Novelpedia config | `/home/LENOVO/.novelpedia/` |
| Setup script | `/home/LENOVO/.hermes/hermes-agent/setup-hermes.sh` |

## Novelpedia Source Code Structure

The codebase at `auth-dash/` is a monorepo with these key areas:

| Layer | Path Pattern |
|---|---|
| Frontend (React) | `apps/author-dashboard/` (author) / `apps/reader-app/` (reader) |
| Backend (Django) | `backend/apps/{authors,users,content}/` |
| Shared types | `packages/shared-types/src/` |
| Zod schemas | Inline in `components/**/ProfileEditForm.tsx` |

## Investigating Field-Level Bugs (e.g., character limit)

For bugs involving a specific form field (like the author bio), trace through ALL layers:

1. **Frontend validation** — `apps/author-dashboard/components/dashboard/ProfileEditForm.tsx` (Zod schema, `.max(N)`)
2. **Frontend API call** — `apps/author-dashboard/lib/server/user-actions.ts` (what gets sent)
3. **API serializer** — `backend/apps/authors/serializers.py` (Django REST Framework validation)
4. **Django model** — `backend/apps/authors/models.py` (DB-level `max_length` or lack thereof)
5. **Django view** — `backend/apps/authors/views.py` (how the field is handled in PATCH)

> ⚠️ **Common bug pattern**: Zod limit (e.g., 500) is LOWER than model limit (e.g., 2000 or unlimited TextField). The backend would accept it, but the frontend silently blocks saving without a clear error message or character counter.

## NovelStats / Rating Architecture

Key files for rating-related bugs:

| Concern | Path |
|---|---|
| NovelStats model (denormalized `rating_average`, `rating_count`) | `backend/apps/content/models.py` |
| Review model (soft-delete via `is_active`, `deleted_at`) | `backend/apps/community/models.py` |
| Review signal handlers (post_save — updates NovelStats on create/update) | `backend/apps/content/signals.py` |
| User ban + activity purge (soft-deletes reviews, does NOT recalc stats) | `backend/apps/moderation/views.py` (`_purge_user_activity`) |
| Serializer that includes `rating_count` for recommended novels | `backend/apps/content/serializers.py` (`RecommendedNovelSerializer`) |

**Critical gap discovered (2026-04-30):**
- `post_delete` signal on `Review` was MISSING — hard-deleted reviews never triggered NovelStats recalculation
- `_purge_user_activity()` collected affected novel IDs and soft-deleted reviews, but never called any recalculation — ratings remained inflated
- Both are now fixed on branch `fix/rating`

**Signal chain for ratings:**
1. Review created/updated → `post_save` signal → `update_novel_rating_on_review` → aggregates active reviews → writes `rating_average`, `rating_count` to NovelStats
2. Review deleted (hard) → `post_delete` signal → `update_novel_rating_on_review_delete` (NEW — added 2026-04-30)
3. Ban purge → `_purge_user_activity` → pre-collects novel IDs, soft-deletes reviews → calls `_refresh_novel_rating_stats` per novel (NEW — added 2026-04-30)

## GitHub Access in This Environment

**`gh` CLI is not installed.** `gh` is absent from `$PATH` and not found at any common location (`/usr/local/bin/gh`, `/usr/bin/gh`, `~/.local/bin/gh`).

**GitHub API via `curl` requires a token.** The `GITHUB_TOKEN` exists (masked as `***`) in:
- `/home/LENOVO/.hermes/novelpedia-profiles/karmicdaoist-197440/.env` — `GITHUB_TOKEN=***`

To use GitHub API via `curl` for filing issues, managing PRs, etc.:
```bash
# Extract token first
TOKEN=$(grep GITHUB_TOKEN ~/.hermes/novelpedia-profiles/karmicdaoist-197440/.env | cut -d= -f2)
# Then use with curl:
curl -s -H "Authorization: token $TOKEN" https://api.github.com/...
```

**For GitHub operations in this environment:**
- Use `curl` with a token (not `gh`)
- The token is at `~/.hermes/novelpedia-profiles/karmicdaoist-197440/.env`
- Read it with `python3` or `grep -a` (not `cat` — output is masked/redacted)

## Author Dashboard Tiptap Editor — Paste Architecture

The chapter editor (`apps/author-dashboard/components/editor/TiptapEditor.tsx`) uses a custom paste pipeline at `apps/author-dashboard/lib/editor/paste/`:

| File | Purpose | Status |
|------|---------|--------|
| `paste-extension.ts` | ProseMirror plugin registering `handlePaste` | Works for Google Docs only |
| `paste-handler.ts` | Intercepts paste events; only handles Google Docs, returns `false` for all others | **Bug: non-Google Docs pastes lose all formatting** |
| `google-docs-normalizer.ts` | Strips Google Docs noise (colors, fonts, margins); removes `font-style` and `text-decoration` | **Bug: italics and underline stripped even for Google Docs** |
| `table-converter.ts` | Converts HTML `<table>` to Tiptap table nodes | **Bug: never called from paste-handler** |

When filing paste/formatting bugs: check `paste-handler.ts` first — it gates all paste handling and is the single point of control for what gets preserved.

## Installing repo

If `repo` (Google's AOSP manifest tool) is needed:
```bash
curl https://storage.googleapis.com/git-repo-downloads/repo > ~/bin/repo
chmod a+x ~/bin/repo
```

If cloning a git repository instead, ask which URL.

## Setup hermes-agent

Run `./setup-hermes.sh` inside `/home/LENOVO/.hermes/hermes-agent/` to set up the Python venv and dependencies.
