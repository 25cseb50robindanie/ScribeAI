# ScribeAI Agent Definitions and Routing Rules

This document outlines the four agents in the ScribeAI pipeline and the criteria for routing papers through the evaluation workflow.

## 1. Agent 1: Handwriting Extractor (agent_extractor)
- **Role**: Handwriting & OCR Specialist
- **Input**: Student answer sheet image file path.
- **Model**: `gemini-2.5-flash` (or compatible multimodal model).
- **Output**: JSON payload conforming to the `ExtractionOutput` schema, containing extracted text for each question and `confidence_score` (integer, 0 to 100) per answer, plus an `overall_confidence` score (integer, 0 to 100).
- **Instructions**: Transcribe student answers accurately without altering grammar or phrasing. If handwriting is illegible, assign a low confidence score to that question.

## 2. Agent 2: Concept Evaluator (agent_evaluator)
- **Role**: Grading & Subject Matter Expert
- **Input**: Structured extraction from Agent 1, plus the reference marking scheme.
- **Model**: `gemini-2.5-flash`.
- **Output**: JSON payload conforming to the `EvaluationOutput` schema. For each question, evaluates each concept defined in the marking scheme as:
  - `full match` (assigns 100% of concept max score)
  - `partial match` (assigns 50% of concept max score)
  - `no match` (assigns 0% of concept max score)
- Calculates a total score per question and output an overall `evaluation_confidence_score` (integer, 0 to 100).

## 3. Agent 3: Router Agent (router_node)
- **Role**: Quality Controller & Router
- **Input**: `overall_confidence` (from Agent 1) and `evaluation_confidence_score` (from Agent 2).
- **Rules**:
  - **Direct Pass (`DIRECT`)**: Both scores are $\ge 80$. The paper bypasses re-evaluation and goes straight to Agent 4's final report generation and storage.
  - **Human Review (`HUMAN_REVIEW`)**: Either score is $< 70$. The paper escalates immediately to a human supervisor.
  - **Second Opinion (`SECOND_OPINION`)**: Both scores are $\ge 70$, but at least one score is $< 80$ (i.e. medium confidence/discrepancy). The paper is routed to Agent 4 for re-evaluation.

## 4. Agent 4: Re-evaluator and Report Generator (agent_reevaluator / agent4_report_node)
- **Role**: Senior Evaluator & Report Writer
- **Inputs**:
  - Original evaluation from Agent 2.
  - Re-evaluation output (for second opinion path).
  - Target Google Drive folder ID (optional, via MCP).
- **Behavior**:
  - If routed via `DIRECT`:
    - Generates a PDF or markdown report with student grades and feedback.
    - Saves the report locally to the `reports/` directory using the `save_report_locally` tool.
    - (Optional) Saves the report to Google Drive using the `create_file` tool if requested.
  - If routed via `SECOND_OPINION`:
    - Independently grades the answers again.
    - Compares the total score of this second opinion against the original score from Agent 2.
    - If the disagreement is within 10% (relative difference $\le 10\%$ of max score, or absolute difference $\le 0.5$ points):
      - Averages the original and second opinion scores.
      - Generates the final report and saves it locally using the `save_report_locally` tool (and optionally to Google Drive).
    - If the disagreement is $> 10\%$:
      - Escalates to Human Review.

