# GP Booking Output Template

## Confirmation policy

Before using this template as the live final output for a booking flow in the current conversation:
- show the section layout briefly
- ask the user to confirm the format if they have not already approved it
- after approval, reuse the same format without re-asking unless the structure changes

## Standard output format

Use this structure in the final booking-prep reply:

### 1. 预约入口
- Clinic / route
- Booking URL
- If relevant, what the user needs to do next

### 2. 已整理好的中文确认摘要
- 1 short paragraph summarizing the case in Chinese
- Keep it factual, no extra speculation

### 3. 可直接提交的英文内容
Use this exact heading:
`English summary for booking form`

Then provide one clean English block covering:
- symptom description
- concern level / main worry
- new vs ongoing issue
- duration
- previous doctor review
- self-care already tried
- new medicines / supplements / changes
- allergies
- what help is being requested

### 4. 待补充项
- List only unanswered questions
- If nothing is missing, say `无`

### 5. 注意事项
- Keep this very short
- Only include urgent-routing advice if the symptoms justify it

## Preview format for confirmation

Use this short preview before the first live formatted output:

- 预约入口
- 中文确认摘要
- English summary for booking form
- 待补充项
- 注意事项

Ask:
`我先按这个格式给你整理，可以吗？`
