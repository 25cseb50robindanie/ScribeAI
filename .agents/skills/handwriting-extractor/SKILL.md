---
name: handwriting-extractor
description: Extracts handwritten text from student answer sheets using Gemini Vision and outputs structured JSON with integer confidence scores (0-100).
---

# Handwriting Extractor Skill

This skill allows the agent to extract text from scanned images of handwritten student answer sheets and format them into structured JSON.

## Instructions

1. **Multimodal Analysis**: View the student answer sheet image carefully.
2. **Text Transcription**: Transcribe the student's answer for each question exactly as written. Do not correct spelling, grammatical errors, or structural issues.
3. **Question Mapping**: Locate the question identifier (e.g. Q1, Q2) on the sheet and align it with the extracted text.
4. **Confidence Scoring**: Assign a confidence score as an integer from 0 to 100 for each transcription.
   - 90-100: Handwriting is exceptionally clear, print-like, and highly legible.
   - 70-89: Normal handwriting, legible with slight effort or standard variations.
   - 50-69: Messy or partially illegible handwriting, some words guessed.
   - < 50: Mostly illegible, heavily scribbled, or missing answers.
5. **JSON Formatting**: Output a structured JSON matching the `ExtractionOutput` Pydantic model.
