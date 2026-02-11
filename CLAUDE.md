# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python 3.13+ CLI demonstration project for GitHub Actions CI/CD workflows. The codebase is intentionally minimal (single `main.py` entry point) with optional Sentry integration to showcase various automation patterns.

## Development Commands

### Setup
```bash
uv sync --dev          # Install dependencies + dev tools (preferred)
pip install -r requirements.txt  # Alternative using pip
```

### Running
```bash
python main.py         # Run the CLI locally
uv run python main.py  # Run via uv
```

### Testing
```bash
uv run pytest                              # Run all tests
uv run pytest -q                           # Quiet mode
uv run pytest --maxfail=1 --disable-warnings -q  # Fast-fail mode (mirrors CI)
```

### Linting
```bash
uv run pylint $(git ls-files '*.py')      # Run pylint on all Python files
uv run pylint main.py                     # Check specific file
```

## Architecture

### Sentry Integration Pattern
`main.py` conditionally initializes Sentry based on environment detection:
- Checks for `SENTRY_DSN` environment variable
- Loads `.env` file only in local (non-Codespaces) environments using `python-dotenv`
- Performs initialization twice: once at module import, once in `main()` function
- See `_get_sentry_dsn()` in main.py:10-17 for environment detection logic

### Testing Strategy
Tests use a custom `SentryStub` pattern (tests/test_main.py:12-21) to intercept `sentry_sdk.init()` calls without network side effects. The `import_main_fresh()` fixture (tests/test_main.py:35-72) provides:
- Clean environment variable state per test
- Controlled Sentry stub installation
- Fresh module imports to test initialization logic

Always test both DSN-present and DSN-absent scenarios when modifying Sentry integration.

## GitHub Actions Workflows

All workflows are in `.github/workflows/`. Key patterns:
- Python 3.13 is standard across all jobs
- `uv sync --frozen --dev` installs dependencies
- `uv run <command>` executes tools
- Pylint uses `|| true` to prevent CI failures while collecting results
- The `pylint-issue-report.yml` aggregates lint errors into a single tracked issue

When adding workflows, update the table in README.md with the trigger, purpose, and file name.

## Configuration Files

- `pyproject.toml`: Package metadata, dependencies, pytest configuration
- `uv.lock`: Locked dependency versions (commit this file)
- `.env`: Local secrets (never commit); use for `SENTRY_DSN` and `SENTRY_TRACES_SAMPLE_RATE`
- `.python-version`: Specifies Python 3.13 for version managers

## Coding Conventions

- Type hints required for public functions (see `_get_sentry_dsn()` return type)
- Use `logging.getLogger(__name__)` for logging
- F-strings for string interpolation
- 4-space indentation, `lower_snake_case` for functions/variables

## Security Notes

Never commit:
- Real Sentry DSN values
- API keys or tokens
- Contents of `.env` file

Use repository secrets in GitHub Actions for sensitive values.

## Agent Task Logging

When performing multi-step tasks, create log files in `.agents/` directory:
- Naming: `agent_task_YYYYMMDDHHMMSS_<slug>.md`
- Include: user instruction, TODO list, execution log, outcome
- Link the log file in PR descriptions
- Never include secrets in logs
