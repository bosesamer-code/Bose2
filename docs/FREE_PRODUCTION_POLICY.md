# Free Production Policy

## Project Law

**Bose2 must remain capable of producing a useful handmade-content package without a paid subscription.**

This repository is the public production factory. It must never contain API keys, tokens, passwords, or private account data.

## Production Principles

- Free/open-source tooling is the default.
- FFmpeg is the default video assembly layer.
- Provider adapters must be replaceable.
- Mock/local providers must exist for tests and dry runs.
- A paid provider must never be required for CI or the free MVP.
- Missing external services must fail safely and preserve the job.
- Invalid media must never become a publishable package.
- Publishing requires validation and the project's human gate.
- Heavy or recurring workloads should not be forced into private GitHub Actions when a safe public-repository workflow can handle them.

## Required Pipeline

Idea -> Script -> Assets -> Audio -> Video -> Validation -> Publishing Package

The production factory must expose a stable contract so that real providers can be added later without replacing the orchestration layer.

## Security

Never commit:

- API keys
- access tokens
- passwords
- cookies
- OAuth refresh tokens
- private account identifiers
- unpublished personal data

## Cost Rule

If a future component needs money, it must be optional and documented. It cannot silently become a required dependency.

The project is being built to create income, so **mandatory recurring spend before income is prohibited by design**.
