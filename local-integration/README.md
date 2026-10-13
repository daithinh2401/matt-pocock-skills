# Selected skills for Anni

This fork keeps upstream skills unchanged. The project-specific distribution is built from `selection.json`, exact-match edits in `overrides.json`, and `POLICY.md`. Install this selection, not the full Matt plugin or the upstream global linking script.

| Entry point | Included support | Purpose |
| --- | --- | --- |
| `grill-with-docs` | `grilling`, `domain-modeling` | Clarify unresolved software requirements and record agreed language/decisions |
| `improve-codebase-architecture` | `codebase-design`, `grilling`, `domain-modeling` | Assess architecture and compare candidates before implementation |

All five skills allow implicit invocation. The two entry points have narrower trigger descriptions and both Claude/Codex invocation flags agree. Supporting files travel with their owner. No tracker or full Matt setup is required.

The integration reuses settled answers, keeps existing approval boundaries, preserves project vocabulary and C3 records, follows the local ADR/testing doctrine, and hands implementation to Addy. An architecture proposal never authorizes an automatic refactor. The bundle includes the upstream license and a source/file hash manifest.

## Validate and export

Requires Python 3.9+ and no external packages:

```sh
python3 -m unittest discover -s local-integration -p 'test_*.py' -v
python3 local-integration/export.py
python3 local-integration/export.py /tmp/matt-selected-new
```

The destination must not exist. Export never writes to Anni or a user skill directory. Inspect the result, then explicitly copy the five directories into a project's skill location and retain `manifest.json` and `LICENSE` as provenance. Project routing and discovery adapters belong to the consuming project.

## Upstream maintenance

`Sync upstream for review` runs weekly and on demand. It opens a review branch/PR, never merges main. If selected source files change, validation deliberately fails until the adaptation has been reviewed. Changes outside the selection do not force an Anni update.

1. Review the upstream diff against `selection.json`'s source commit, including new/deleted supporting files.
2. Update exact-match overrides only where needed. Keep source files under `skills/` unchanged.
3. Refresh the selection's `source_commit` and `source_sha256` to the reviewed upstream tree. Hash every file under each selected source directory using SHA-256; added/deleted files must also be accounted for. Do not use hashes to waive a behavior review.
4. Run the tests and export validation, review trigger cases and handoff behavior, then merge the PR.
5. Updating a consumer is a separate, manual operation in this phase. Automatic updates for both Addy and Matt will be designed together in Anni later.

For automatic PR creation with GITHUB_TOKEN, Actions' "Allow GitHub Actions to create and approve pull requests" must be enabled by the owner. The fallback GITHUB_TOKEN can sync ordinary files but cannot push upstream changes to workflow files. Configure `SYNC_APP_ID` and `SYNC_APP_PRIVATE_KEY` using a GitHub App installed on this fork with contents, pull requests, and workflows write permissions for full coverage, as on the Addy fork. Never commit credentials. The three inherited release/issue workflow jobs are guarded to run only on `mattpocock/skills`; the fork only executes its integration workflows. Review newly added upstream workflows during every sync.

The tests verify export integrity, dependencies, real reference links, stale overrides, upstream drift, and refusal to overwrite existing output. They do not prove that a model always selects the right skill; use realistic positive/negative requests and inspect actual invocation separately.
