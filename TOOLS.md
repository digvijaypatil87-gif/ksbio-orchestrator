# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## n8n (localhost:5678)
- User: `admin`
- Password: `ksbio_n8n_2026`
- API Key: stored in `memory/n8n-api-key.txt`
- Workflows:
  - `KSBio ETL Pipeline` (gIxkTvOi8O1Jnlgk) — active, daily ETL via FastAPI
  - `KSBio ETL Health Check` (c3c35266-...) — active, every 6h
  - `KSBIO Infrastructure Monitor` (wv9h8L5MyYEWiI6i) — active, every 5 min
  - `KSBio Reconciliation Alert` (73680fc1-...) — inactive, needs fix
  - `ERPNext Health Check` (ce06a4e4-...) — inactive

## ERPNext (localhost:8081 → container 8000)
- Admin: `Administrator` / `admin123`
- API Key: `297d8e3d376107b97613ef1f81974061`
- API Secret: `ksbio-ffee442f21a4af0f7db68361a09f3ee0`
- Docker: `workspace-ksbio-erpnext_app-1`
- Site: `erpnext.local`
- DB: `erpnext_site` / `erpnext` / `erpnext123`
- Data: 239 customers, 206 suppliers, 266 items, 79 accounts
- Company: KSBio

## FastAPI ETL (localhost:8001)
- `POST /api/etl/parse-trial-balance`
- `POST /api/etl/parse-debtors-creditors`
- `GET /api/etl/truth-check`
- `GET /api/etl/status`
- Tally XML: `C:\Users\Digvijay Patil\Desktop\Tally 12-4-2026\Reports\`

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.
