---
name: report-generator
description: Generates final grading reports, averages scores if second opinion disagreement is within 10%, and saves them locally or in Google Drive.
---

# Report Generator Skill

This skill allows the agent to compile student evaluation results, perform averages if needed, format the final report in Markdown, and save it.

## Instructions

1. **Score Verification**:
   - For direct passes: Use the original evaluation scores directly.
   - For second opinion cases:
     - Compare the total score of the re-evaluation with the original score.
     - Calculate the disagreement percent as:
       $$\text{Disagreement} = \frac{|S_1 - S_2|}{\text{Max Score}} \times 100$$
     - If the disagreement is $\le 10\%$:
       - Calculate the final score for each concept/question by averaging the original and second-opinion scores.
     - If the disagreement is $> 10\%$:
       - Mark the paper for immediate human escalation. Do not save results.
2. **Report Structuring**:
   - Generate a clean Markdown report with the student's ID, question-by-question final scores, concept breakdown, match levels, feedback, and final grade.
3. **Report Storage**:
   - **Local Storage (Primary)**:
     - Invoke the `save_report_locally` tool to save the Markdown report.
     - Specify the `title` (e.g. `report_{student_id}.md`).
     - Pass the report `content`.
   - **Google Drive Storage (Secondary/Optional)**:
     - If requested, invoke the `create_file` tool to save the report to Google Drive.
     - Specify the title, textContent, contentMimeType="text/markdown", parentId (if provided), and disableConversionToGoogleType=True.

