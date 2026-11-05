# Repair status and security boundary

This document tracks the staged repair of Bose2 without replacing existing production work.

## Public factory responsibilities
Bose2 contains reusable production code, content catalogs, media assembly, validation, regression tests, and non-sensitive artifacts. Its core pipeline must work without API credentials or paid services.

## Security boundary
- Do not add API keys, OAuth client secrets, refresh tokens, access tokens, passwords, cookies, or private account data to this repository.
- The optional Gemini enhancement is not required for the free MVP. The production workflow now runs without injecting GEMINI_API_KEY and falls back to the local deterministic script.
- The current manual YouTube and Facebook workflows still reference GitHub Actions secrets in this repository. They are transitional and are scheduled to move to the private Bose control plane. Do not add or rotate publishing credentials here as part of the migration.
- Automatic publishing remains disabled. The existing automatic-publishing.yml job is intentionally guarded by if: false.

## First repair batch
- YouTube channel verification now supports a Google identity with multiple authorized channels, but only if the exact expected handle resolves to a channel ID present in the OAuth identity's authorized channel list.
- Channel mismatches still fail closed.
- OAuth refresh errors now produce a concise diagnostic without exposing credentials.
- Regression tests cover multiple authorized channels and an unauthorized target.
- Draft PR: https://github.com/bosesamer-code/Bose2/pull/20

## Known external blocker
The most recent inspected YouTube test run failed during OAuth token refresh with unauthorized_client, before channel verification and before any video upload. This points to an OAuth client / refresh-token pairing or authorization issue; changing Python channel-selection logic cannot repair a rejected OAuth client. Re-authorize the intended channel with the same OAuth client ID and client secret, then replace the refresh token in the private secret store after the publishing workflow has moved there.

## Release gate
Do not merge the repair PR until CI passes and the private credential migration plan is reviewed. Do not enable automatic publishing.
