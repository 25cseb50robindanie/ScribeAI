import os
import sys
import json
import pytest

# Ensure app directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agent import (
    identify_student,
    calculate_max_score,
    apply_choice_rules,
    DEFAULT_MARKING_SCHEME
)

def test_identify_student_metadata():
    # Test that name and roll number are extracted from metadata
    extraction = {
        "student_name": "Alice Index",
        "roll_number": "12345"
    }
    name, roll, student_id = identify_student("scratch/Student_A.pdf", extraction)
    assert name == "Alice Index"
    assert roll == "12345"
    assert student_id == "Alice_Index_12345"

def test_identify_student_filename_fallback():
    # Test that name and roll number fall back to filename parsing
    extraction = {}
    name, roll, student_id = identify_student("scratch/Robin_Danie_56789.jpg", extraction)
    assert name == "Robin Danie"
    assert roll == "56789"
    assert student_id == "Robin_Danie_56789"

def test_identify_student_unknown_fallback():
    # Test that unknown inputs use the default fallback values
    extraction = {}
    name, roll, student_id = identify_student("scratch/unknown_paper.png", extraction)
    assert name == "unknown paper"
    assert roll == "Unknown Roll"
    assert student_id == "unknown_paper"

def test_calculate_max_score():
    # Test max score calculation with DEFAULT_MARKING_SCHEME (should be 20, because Part B only allows 2 out of 3 of the 5-mark questions)
    assert calculate_max_score(DEFAULT_MARKING_SCHEME) == 20.0

    # Test flat marking scheme (list of questions)
    flat_scheme = DEFAULT_MARKING_SCHEME["questions"]
    assert calculate_max_score(flat_scheme) == 25.0

def test_apply_choice_rules_disregard_third():
    # Student attempts Q6, Q7, and Q8 in that order
    extraction_output = {
        "answers": [
            {"question_id": "Q1", "extracted_text": "Definition"},
            {"question_id": "Q6", "extracted_text": "Inheritance explanation..."},
            {"question_id": "Q7", "extracted_text": "Encapsulation advantages..."},
            {"question_id": "Q8", "extracted_text": "Compile-time vs Run-time..."}
        ]
    }

    # Initial evaluation output from LLM (where all get graded)
    evaluation_output = {
        "questions": [
            {
                "question_id": "Q1",
                "total_score": 2.0,
                "max_score": 2.0,
                "evaluations": [
                    {"concept": "encapsulation_definition", "match_level": "full match", "score": 1.0, "feedback": "Good"},
                    {"concept": "data_hiding_control", "match_level": "full match", "score": 1.0, "feedback": "Good"}
                ]
            },
            {
                "question_id": "Q6",
                "total_score": 5.0,
                "max_score": 5.0,
                "evaluations": [
                    {"concept": "inheritance_concept", "match_level": "full match", "score": 1.5, "feedback": "Good"},
                    {"concept": "access_specifiers", "match_level": "full match", "score": 1.0, "feedback": "Good"},
                    {"concept": "code_example", "match_level": "full match", "score": 1.5, "feedback": "Good"},
                    {"concept": "example_explanation", "match_level": "full match", "score": 1.0, "feedback": "Good"}
                ]
            },
            {
                "question_id": "Q7",
                "total_score": 5.0,
                "max_score": 5.0,
                "evaluations": [
                    {"concept": "data_hiding_security", "match_level": "full match", "score": 2.0, "feedback": "Good"},
                    {"concept": "getters_setters_control", "match_level": "full match", "score": 1.5, "feedback": "Good"},
                    {"concept": "maintainability_modularity", "match_level": "full match", "score": 1.5, "feedback": "Good"}
                ]
            },
            {
                "question_id": "Q8",
                "total_score": 5.0,
                "max_score": 5.0,
                "evaluations": [
                    {"concept": "compile_time_explanation", "match_level": "full match", "score": 1.0, "feedback": "Good"},
                    {"concept": "run_time_explanation", "match_level": "full match", "score": 1.0, "feedback": "Good"},
                    {"concept": "key_differences", "match_level": "full match", "score": 1.0, "feedback": "Good"},
                    {"concept": "compile_time_example", "match_level": "full match", "score": 1.0, "feedback": "Good"},
                    {"concept": "run_time_example", "match_level": "full match", "score": 1.0, "feedback": "Good"}
                ]
            }
        ],
        "evaluation_confidence_score": 95
    }

    # Apply choice rules programmatically
    apply_choice_rules(evaluation_output, extraction_output, DEFAULT_MARKING_SCHEME)

    # Q1, Q6, Q7 should be unchanged
    assert evaluation_output["questions"][0]["total_score"] == 2.0
    assert evaluation_output["questions"][1]["total_score"] == 5.0
    assert evaluation_output["questions"][2]["total_score"] == 5.0

    # Q8 was the third attempted question, so it must be disregarded (0 marks)
    q8_eval = evaluation_output["questions"][3]
    assert q8_eval["total_score"] == 0.0
    for concept in q8_eval["evaluations"]:
        assert concept["match_level"] == "no match"
        assert concept["score"] == 0.0
        assert "disregarded" in concept["feedback"]

def test_apply_choice_rules_two_attempts():
    # Student only attempts Q6 and Q8
    extraction_output = {
        "answers": [
            {"question_id": "Q6", "extracted_text": "Inheritance explanation..."},
            {"question_id": "Q8", "extracted_text": "Compile-time vs Run-time..."}
        ]
    }

    evaluation_output = {
        "questions": [
            {
                "question_id": "Q6",
                "total_score": 5.0,
                "max_score": 5.0,
                "evaluations": [
                    {"concept": "inheritance_concept", "match_level": "full match", "score": 1.5, "feedback": "Good"},
                    {"concept": "access_specifiers", "match_level": "full match", "score": 1.0, "feedback": "Good"},
                    {"concept": "code_example", "match_level": "full match", "score": 1.5, "feedback": "Good"},
                    {"concept": "example_explanation", "match_level": "full match", "score": 1.0, "feedback": "Good"}
                ]
            },
            {
                "question_id": "Q8",
                "total_score": 5.0,
                "max_score": 5.0,
                "evaluations": [
                    {"concept": "compile_time_explanation", "match_level": "full match", "score": 1.0, "feedback": "Good"},
                    {"concept": "run_time_explanation", "match_level": "full match", "score": 1.0, "feedback": "Good"},
                    {"concept": "key_differences", "match_level": "full match", "score": 1.0, "feedback": "Good"},
                    {"concept": "compile_time_example", "match_level": "full match", "score": 1.0, "feedback": "Good"},
                    {"concept": "run_time_example", "match_level": "full match", "score": 1.0, "feedback": "Good"}
                ]
            }
        ],
        "evaluation_confidence_score": 95
    }

    apply_choice_rules(evaluation_output, extraction_output, DEFAULT_MARKING_SCHEME)

    # Both Q6 and Q8 should retain their full score since total attempts is 2 (<= limit 2)
    assert evaluation_output["questions"][0]["total_score"] == 5.0
    assert evaluation_output["questions"][1]["total_score"] == 5.0
