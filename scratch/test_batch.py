import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

from app.agent import app
from google.adk.runners import InMemoryRunner
from google.genai import types

async def main():
    runner = InMemoryRunner(app=app)
    
    # Create session
    session = await runner.session_service.create_session(
        app_name="app", user_id="user_123", session_id="session_batch_test"
    )
    print(f"Created session: {session.id}")
    
    # Target directory path
    target_dir = "sample"
    input_payload = target_dir
    
    print(f"\n--- Running batch evaluation on folder: {target_dir} ---")
    from contextlib import aclosing
    
    async with aclosing(runner.run_async(
        user_id="user_123",
        session_id=session.id,
        new_message=types.UserContent(parts=[types.Part.from_text(text=input_payload)])
    )) as events:
        async for event in events:
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print(f"Text output: {part.text}")
            
            # Print intermediate progress or success/human review events
            if event.output:
                output_data = event.output
                if isinstance(output_data, dict):
                    status = output_data.get("status")
                    student_id = output_data.get("student_id")
                    if student_id:
                        print(f"[PROGRESS] Student: {student_id} | Status: {status} | Score: {output_data.get('final_score')}/{output_data.get('max_score')}")

if __name__ == "__main__":
    asyncio.run(main())
