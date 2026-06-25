---
name: gp-booking
description: Collect GP appointment triage details for household members, prepare booking-ready summaries, and guide them through linked clinic booking routes such as Liverpool GP self-booking via Blinx. Use when a household member asks to book a GP, see a doctor, fill a symptom form, prepare answers for online triage, or standardize a repeatable clinic-booking workflow.
---

# GP Booking

## Purpose

Handle repeatable household GP booking flows: identify the right member and clinic route, collect the required triage details, prepare a clean booking-ready summary, and guide the user to the correct booking link.

## Workflow

1. Read `references/clinic-profiles.md` to find the member and booking route.
2. If the member or clinic route is unclear, ask one short clarifying question first.
3. Ask only the missing triage questions required by that profile.
4. Draft the booking output using `references/output-template.md`.
5. Before giving the final formatted output for live use, show the format briefly and ask the user to confirm it if that format has not already been approved in the current conversation.
6. After confirmation, fill the template and give the booking link or next action.

## Rules

- Default to the clinic/member profile in `references/clinic-profiles.md`; do not guess a new clinic route.
- If another household member wants to use the same clinic flow, confirm they use the same GP/booking route before reusing the profile.
- If no matching profile exists, collect the clinic name, booking URL, and required question set first, then propose adding a new profile.
- Keep medical wording factual and concise; do not improvise diagnosis.
- If the symptoms sound urgent or dangerous, pause the routine booking flow and tell the user to use urgent care routes instead.
- Do not submit forms on the user's behalf unless they explicitly ask and the required tool/workflow exists.

## References

- `references/clinic-profiles.md` for active household clinic routes and question sets
- `references/output-template.md` for the standard booking output format and confirmation policy
