# Household GP Booking Profiles

## Profile schema

For each household booking route, keep these fields:
- member
- clinic label
- city or area
- booking route type
- booking URL
- required triage question set
- language/output notes
- escalation notes if needed

## Active profiles

### Hannah | Liverpool GP via Blinx self-booking

- member: Hannah
- clinic label: Liverpool GP
- city/area: Liverpool
- booking route type: Blinx patient self-booking
- booking URL: https://blinxscheduler.com/patient-self-booking/
- language notes: ask Hannah in simple Chinese by default, allow English if she switches
- workflow: collect the triage answers first, then prepare a booking-ready summary, then send Hannah to the Blinx page

#### Required triage question set (9)
1. 症状描述
2. 是否担心，以及最担心什么
3. 这是新问题还是旧问题复发
4. 持续多久了
5. 之前有没有为这个问题看过医生
6. 已经用过什么缓解方法，效果如何
7. 最近有没有开始新药、补剂或其他明显变化
8. 过敏史
9. 这次最希望得到什么帮助（建议、药、面诊、电话回访等）

#### Practical notes
- If another household member says they also use this same Liverpool GP route, confirm that they want to use the same Blinx self-booking flow before reusing it.
- If the member uses a different clinic, do not reuse this profile blindly.
- If symptoms sound urgent, do not continue as a routine GP booking without warning the user first.

## Add-next profile checklist

When adding another household member or another clinic route later, collect:
- member name
- clinic name
- booking URL
- route type (Blinx / PATCHS / eConsult / NHS App / phone / other)
- exact triage questions if the clinic requires a fixed set
- preferred output language
- any special notes about timing or urgency
