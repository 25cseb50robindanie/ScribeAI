---
name: concept-evaluator
description: Evaluates extracted answers concept by concept against a marking scheme, assigning match levels (full, partial, no match) and calculating scores.
---

# Concept Evaluator Skill

This skill allows the agent to evaluate the correctness of transcribed student answers by comparing them concept-by-concept against a structured marking scheme.

## Instructions

1. **Input Analysis**: Read the extracted answer text and matching question definition in the marking scheme.
2. **Concept-by-Concept Grading**: For each concept listed in the marking scheme for the question:
   - Identify whether the student's answer captures the concept.
   - Assign a `match_level`:
     - `full match`: The student fully explains or mentions the key concept. Assign 100% of the concept's maximum score.
     - `partial match`: The student mentions the concept but with incomplete context, minor errors, or poor explanation. Assign 50% of the concept's maximum score.
     - `no match`: The student does not mention or explain the concept, or explains it completely incorrectly. Assign 0 points.
3. **Feedback Generation**: Provide brief feedback explaining the match level chosen.
4. **Confidence Scoring**: Generate an overall `evaluation_confidence_score` as an integer from 0 to 100 representing how confident you are in the grading accuracy (e.g. clear match is 90-100, ambiguous phrasing is 70-80, completely unclear is < 70).
5. **Output**: Output a structured JSON matching the `EvaluationOutput` Pydantic model.
