# ZPE-Music Lane Restart Prompt

## Lane

`ZPE-Music`

## Purpose

Use this prompt to restart the music lane from **remote state only** after full local deletion.

## Startup Prompt

You are the lane agent for `ZPE-Music`.

Assume **all previous local state is gone**. You must rely only on:

- GitHub repo: `https://github.com/Zer0pa/ZPE-Music.git`
- GitHub PR: `https://github.com/Zer0pa/ZPE-Music/pull/6`
- GitHub branch archive: `archive/geogram4-split-snapshot`
- GitHub historical branch: `chore/novelty-card-backfill-2026-04-22`
- GitHub tag: `geogram4-l3-music-bounded-v0.1.0`
- Hugging Face dataset archive: `Architect-Prime/zpe-music-lane-archive`

### Read in this order

1. PR `#6` on `codex/h1-lane-hygiene-music`
   - This is the current **keeper** Wave 1 lane-hygiene PR.
   - It is already **ready for review**.
   - Do **not** recreate or duplicate it.
   - If it is still open, treat it as the active continuation branch.
   - If it has already merged, continue from updated `origin/main`.

2. `origin/main`
   - `README.md`
   - `pyproject.toml`
   - `CITATION.cff`
   - `SECURITY.md`
   - `docs/SCOPE.md`
   - `proofs/manifests/CURRENT_AUTHORITY_PACKET.md`

3. `origin/chore/novelty-card-backfill-2026-04-22`
   - `geogram5/report/L3_FINAL_REPORT.md`
   - `geogram5/run_geogram5_eval.py`
   - `geogram6/l3-expression-followup/report/L3_FINAL_REPORT.md`
   - `geogram6/l3-expression-followup/run_geogram6_eval.py`

4. `origin/archive/geogram4-split-snapshot`
   - `docs/L3_FINAL_REPORT.md`
   - `scripts/l3_music_geogram4_eval.py`
   - `artifacts/l3_music_geogram4.json`

5. Hugging Face dataset `Architect-Prime/zpe-music-lane-archive`
   - Use this as the redundant archive surface for restart materials and historical lane artifacts.

### Current lane truth

- Public earned scope: canonical symbolic score plus bounded note-local expression refinement.
- Out of scope: waveform/audio understanding, performer-state modeling, pedal/sustain, continuous expressive curves.
- Active operational state: Wave 1 lane-hygiene PR `#6` is the live review surface.
- Historical preservation:
  - Geogram 4 machine artifact preserved on GitHub archive branch and tag.
  - Geogram 5/6 reports and eval scripts preserved on the historical GitHub branch.

### Known caveat

PR `#6` documents a packaging caveat:

- current `setuptools` cannot cleanly satisfy both
  - `project.license = "LicenseRef-Zer0pa-SAL-7.0"` and
  - the `License :: Other/Proprietary License` classifier
  during editable install
- do **not** silently break fresh install just to force that classifier
- if this must be resolved later, treat it as a packaging-backend decision, not a cosmetic metadata tweak

### Restart commands

```bash
git clone https://github.com/Zer0pa/ZPE-Music.git
cd ZPE-Music
git fetch --all --tags
gh pr view 6 --repo Zer0pa/ZPE-Music
git fetch origin codex/h1-lane-hygiene-music:refs/remotes/origin/codex/h1-lane-hygiene-music
git fetch origin chore/novelty-card-backfill-2026-04-22:refs/remotes/origin/chore/novelty-card-backfill-2026-04-22
git fetch origin archive/geogram4-split-snapshot:refs/remotes/origin/archive/geogram4-split-snapshot
```

If PR `#6` is still open, continue from:

```bash
git switch --track origin/codex/h1-lane-hygiene-music
```

If PR `#6` is merged, continue from:

```bash
git switch main
git pull --ff-only
```

### Mission on restart

- Rebuild context from the remote surfaces above only.
- Do not assume any deleted local research folders still exist.
- Treat GitHub as authoritative for code/PR history.
- Treat Hugging Face as redundant restart/archive storage.
- Preserve the current scientific boundary and avoid widening claims.

## Status At Time Of Writing

- PR `#6` ready for review
- duplicate PR `#5` closed
- Geogram 4 archive branch pushed
- Geogram 4 tag pushed
- HF archive mirrored at `Architect-Prime/zpe-music-lane-archive`
