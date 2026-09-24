# Changelog

This file records user-visible changes to the Meal Prep Agent skill. Versions follow semantic versioning: patch releases clarify or fix compatible behavior, minor releases add compatible capabilities or schemas, and major releases may require household-data migration.

## 0.1.1 - 2026-09-23

- Put practical usage examples and compelling workflows before installation details in the public README.
- Make example prompts work naturally across Codex, Claude Code, and Claude.ai.
- Explain ChatGPT skill availability, mobile plugin distribution, and the difference between installing a workflow and storing household data.

## 0.1.0 - 2026-09-23

- Add the general-purpose household meal-prep workflow for Codex, Claude Code, and Claude.ai.
- Add modular recipe-library, planning, shopping, cooking, feedback, inventory, and storage guidance.
- Add normalized JSON schemas, examples, and a public starter cookbook.
- Keep private household data outside the installed skill at `~/.meal-prep-agent/` by default.
- Document linked installs, Claude.ai ZIP packaging, updates, and version maintenance.
