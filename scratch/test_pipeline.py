import os
import sys
import json
import asyncio
from unittest.mock import MagicMock, patch

# Ensure app directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agent import app, ExtractionOutput, EvaluationOutput
from google.adk.runners import InMemoryRunner

# Create dummy JPEG bytes (1x1 pixel)
DUMMY_JPEG = b'\xff\xd8\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xda\x00\x0c\x01\x01\x00\x02\x11\x03\x11\x00?\x00\xbf\x00\xff\xd9'

# Ensure scratch directory exists
os.makedirs("scratch", exist_ok=True)
image_path = "scratch/student_answer.jpg"
with open(image_path, "wb") as f:
    f.write(DUMMY_JPEG)

print(f"Created dummy student answer sheet at: {image_path}")

from google.genai import types

# Helper to mock generate_content response using real SDK class
def create_mock_response(text_content):
    return types.GenerateContentResponse(
        model_version="gemini-2.5-flash",
        candidates=[
            types.Candidate(
                content=types.Content(
                    role="model",
                    parts=[types.Part.from_text(text=text_content)]
                )
            )
        ]
    )

async def run_test_case(name, mock_extractor_json, mock_evaluator_json, mock_reevaluator_json=None):
    print("\n" + "="*50)
    print(f"RUNNING TEST CASE: {name}")
    print("="*50)

    from app.agent import agent_report_generator, save_report_tool
    original_tools = agent_report_generator.tools
    agent_report_generator.tools = [save_report_tool]

    try:
        # We mock the genai.Client
        with patch("app.agent.genai.Client") as mock_client_cls:
            from unittest.mock import AsyncMock
            mock_client = MagicMock()
            mock_client_cls.return_value = mock_client
            
            # Configure sync generate_content side_effect
            responses = [
                create_mock_response(mock_extractor_json),
                create_mock_response(mock_evaluator_json),
            ]
            if mock_reevaluator_json:
                responses.append(create_mock_response(mock_reevaluator_json))
                
            mock_client.models.generate_content.side_effect = responses

            # Configure async generate_content for the report generator agent using real SDK class
            mock_async_resp = create_mock_response("Report generated successfully")
            mock_client.aio = MagicMock()
            mock_client.aio.models = MagicMock()
            mock_client.aio.models.generate_content = AsyncMock(return_value=mock_async_resp)

            # We also mock the McpToolset to prevent trying to start npx server in test
            with patch("app.agent.gdrive_toolset") as mock_toolset:
                # Setup mock tool output if report generator runs
                # The agent report generator will search or call tools
                mock_runner = InMemoryRunner(app=app)
                
                # Start the session run
                # Input to the extractor is the image path
                result = await mock_runner.run_debug(image_path)
                
                # Verify result output
                print(f"Workflow Final Output: {result}")
                return result
    finally:
        agent_report_generator.tools = original_tools

async def main():
    # ----------------------------------------------------
    # Case 1: Direct Pass (Both scores >= 80)
    # ----------------------------------------------------
    extractor_json_1 = json.dumps({
        "answers": [
            {"question_id": "Q1", "extracted_text": "Worst case complexity is O(n^2). It occurs when pivot is smallest/largest.", "confidence_score": 90},
            {"question_id": "Q2", "extracted_text": "Processes have separate memory spaces, threads share process memory.", "confidence_score": 85}
        ],
        "overall_confidence": 88
    })
    evaluator_json_1 = json.dumps({
        "questions": [
            {
                "question_id": "Q1",
                "evaluations": [
                    {"concept": "worst_case_complexity", "match_level": "full match", "score": 2.0, "feedback": "Correctly states O(n^2)"},
                    {"concept": "pivot_selection_cause", "match_level": "full match", "score": 3.0, "feedback": "Correctly explains pivot selection"}
                ],
                "total_score": 5.0,
                "max_score": 5.0
            },
            {
                "question_id": "Q2",
                "evaluations": [
                    {"concept": "resource_sharing", "match_level": "full match", "score": 2.5, "feedback": "Correct resource sharing description"},
                    {"concept": "overhead_creation", "match_level": "no match", "score": 0.0, "feedback": "Missing overhead details"}
                ],
                "total_score": 2.5,
                "max_score": 5.0
            }
        ],
        "evaluation_confidence_score": 92
    })
    
    await run_test_case("Case 1: Direct Pass", extractor_json_1, evaluator_json_1)

    # ----------------------------------------------------
    # Case 2: Human Review (Any score < 70)
    # ----------------------------------------------------
    extractor_json_2 = json.dumps({
        "answers": [
            {"question_id": "Q1", "extracted_text": "Scribbled answer...", "confidence_score": 50},
            {"question_id": "Q2", "extracted_text": "Process vs thread details", "confidence_score": 80}
        ],
        "overall_confidence": 65  # < 70
    })
    evaluator_json_2 = json.dumps({
        "questions": [
            {
                "question_id": "Q1",
                "evaluations": [],
                "total_score": 0.0,
                "max_score": 5.0
            }
        ],
        "evaluation_confidence_score": 85
    })
    
    await run_test_case("Case 2: Human Review", extractor_json_2, evaluator_json_2)

    # ----------------------------------------------------
    # Case 3: Second Opinion - Agreement (both >= 70, at least one < 80, agreement within 10%)
    # ----------------------------------------------------
    extractor_json_3 = json.dumps({
        "answers": [
            {"question_id": "Q1", "extracted_text": "Quicksort is O(n^2) time.", "confidence_score": 75},
            {"question_id": "Q2", "extracted_text": "Threads share memory, processes do not.", "confidence_score": 78}
        ],
        "overall_confidence": 76  # between 70 and 80
    })
    evaluator_json_3 = json.dumps({
        "questions": [
            {
                "question_id": "Q1",
                "evaluations": [
                    {"concept": "worst_case_complexity", "match_level": "full match", "score": 2.0, "feedback": "Stated O(n^2)"},
                    {"concept": "pivot_selection_cause", "match_level": "no match", "score": 0.0, "feedback": "Missing pivot details"}
                ],
                "total_score": 2.0,
                "max_score": 5.0
            },
            {
                "question_id": "Q2",
                "evaluations": [
                    {"concept": "resource_sharing", "match_level": "full match", "score": 2.5, "feedback": "Correct memory sharing description"},
                    {"concept": "overhead_creation", "match_level": "no match", "score": 0.0, "feedback": "Missing overhead details"}
                ],
                "total_score": 2.5,
                "max_score": 5.0
            }
        ],
        "evaluation_confidence_score": 85
    })
    # Re-evaluator grades it similarly (say, same scores)
    reevaluator_json_3 = evaluator_json_3 # Agreement within 10%
    
    await run_test_case("Case 3: Second Opinion (Agreement)", extractor_json_3, evaluator_json_3, reevaluator_json_3)

    # ----------------------------------------------------
    # Case 4: Second Opinion - Disagreement (both >= 70, at least one < 80, disagreement > 10%)
    # ----------------------------------------------------
    extractor_json_4 = extractor_json_3
    evaluator_json_4 = evaluator_json_3
    # Re-evaluator grades it very differently (score 9.0 instead of 4.5, difference = 4.5/10 = 45% > 10%)
    reevaluator_json_4 = json.dumps({
        "questions": [
            {
                "question_id": "Q1",
                "evaluations": [
                    {"concept": "worst_case_complexity", "match_level": "full match", "score": 2.0, "feedback": "Stated O(n^2)"},
                    {"concept": "pivot_selection_cause", "match_level": "full match", "score": 3.0, "feedback": "Correct explanation of sorted array"}
                ],
                "total_score": 5.0,
                "max_score": 5.0
            },
            {
                "question_id": "Q2",
                "evaluations": [
                    {"concept": "resource_sharing", "match_level": "full match", "score": 2.5, "feedback": "Correct memory sharing description"},
                    {"concept": "overhead_creation", "match_level": "partial match", "score": 1.25, "feedback": "Mentioned lightweight aspect"}
                ],
                "total_score": 3.75,
                "max_score": 5.0
            }
        ],
        "evaluation_confidence_score": 88
    })

    await run_test_case("Case 4: Second Opinion (Disagreement -> Escalation)", extractor_json_4, evaluator_json_4, reevaluator_json_4)

if __name__ == "__main__":
    asyncio.run(main())
