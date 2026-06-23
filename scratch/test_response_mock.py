from google.genai import types

try:
    resp = types.GenerateContentResponse(
        model_version="gemini-2.5-flash",
        candidates=[
            types.Candidate(
                content=types.Content(
                    role="model",
                    parts=[types.Part.from_text(text="Report generated successfully")]
                )
            )
        ]
    )
    print("GenerateContentResponse instantiated successfully:", resp)
except Exception as e:
    print("Error instantiating GenerateContentResponse:", e)
