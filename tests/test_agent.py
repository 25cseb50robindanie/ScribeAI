import os
import sys
import json
import pytest

# Ensure app directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agent import identify_student

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
