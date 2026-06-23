# ScribeAI Context

ScribeAI is an AI-powered grading assistant that automates the evaluation of student answer sheets. The system uses a multi-agent pipeline designed to digitize handwritten answers, evaluate correctness concept-by-concept against a marking scheme, route papers based on confidence, and produce standardized results.

## Domain Model

1. **Student Answer Sheet**: An image (JPEG/PNG) containing the student's handwritten answers to a set of questions.
2. **Marking Scheme**: A reference guide containing:
   - `question_id`: Unique identifier for the question.
   - `max_score`: Total possible points.
   - `concepts`: A list of key ideas/points required in the answer, with corresponding sub-scores (e.g. concept name, weight, explanation).
3. **Extraction Output**: Structured text output mapping question IDs to the student's handwritten answer text, along with an OCR confidence score (0 to 100).
4. **Evaluation Output**: Concept-by-concept matches ("full match", "partial match", or "no match") for each student answer, along with grading notes, score, and an evaluation confidence score (0 to 100).

## Reference Marking Scheme (Example)

Below is the standard reference marking scheme used for testing:

```json
[
  {
    "question_id": "Q1",
    "description": "What is the time complexity of quicksort in the worst case, and when does it occur?",
    "max_score": 5,
    "concepts": [
      {
        "concept": "worst_case_complexity",
        "max_score": 2,
        "description": "Mentioning O(n^2) or quadratic time complexity."
      },
      {
        "concept": "pivot_selection_cause",
        "max_score": 3,
        "description": "Explaining that it occurs when the pivot is consistently the smallest or largest element (e.g., already sorted array and choosing the first/last element as pivot)."
      }
    ]
  },
  {
    "question_id": "Q2",
    "description": "Explain the difference between a process and a thread.",
    "max_score": 5,
    "concepts": [
      {
        "concept": "resource_sharing",
        "max_score": 2.5,
        "description": "Explaining that processes have separate memory/address spaces, whereas threads of the same process share the memory space."
      },
      {
        "concept": "overhead_creation",
        "max_score": 2.5,
        "description": "Explaining that context switching/creation is heavier/slower for processes compared to threads."
      }
    ]
  }
]
```
