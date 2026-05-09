# Workspace Skill Template

Use this template for every new or refactored local OpenClaw skill.

## Hard requirements

- Skill folder name should match `name`
- `SKILL.md` must start with YAML frontmatter
- Frontmatter must include at least `name` and `description`
- Keep frontmatter values on single lines
- If you use `metadata`, keep it as a single-line JSON object

## Recommended shape

```md
---
name: example-skill
description: One sentence that says what the skill does, when to use it, and the common trigger phrases or request types.
# Optional:
# metadata: {"openclaw":{"requires":{"bins":["python3"]}}}
---

# Example Skill

## Purpose

One short paragraph on the job this skill handles and the source of truth it should trust.

## When to Use

- User asks for ...
- User mentions ...
- User wants to ...

## Workflow

1. Read the required local files or state.
2. Run the primary script or tool.
3. Verify the result.
4. Reply briefly with what changed or what was found.

## Commands

```bash
python3 scripts/example.py arg1 arg2
```

## Rules

- Confirm before destructive actions.
- Keep dates, IDs, and output formats consistent.
- State household-specific assumptions briefly.

## References

- `references/example.md` for detailed schema or edge cases
```

## Writing rules

- Keep `description` precise, because OpenClaw uses it for discovery
- Put only the core workflow in `SKILL.md`
- Move large schemas or long docs into `references/`
- Put deterministic code in `scripts/`
- Prefer short bullet lists over long prose
