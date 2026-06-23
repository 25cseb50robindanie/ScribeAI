import os
import sys
import asyncio

# Ensure app directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agent import app
from google.adk.runners import InMemoryRunner

async def main():
    print("="*60)
    print("RUNNING REAL SHEET VERIFICATION (LIVE GEMINI API)")
    print("="*60)
    
    # We will run the pipeline using InMemoryRunner on scratch/real_sheet.jpg
    image_path = "scratch/real_sheet.jpg"
    if not os.path.exists(image_path):
        print(f"Error: {image_path} does not exist!")
        return
        
    runner = InMemoryRunner(app=app)
    
    # Run the workflow with the image path as input
    print(f"Starting workflow execution for {image_path}...")
    result = await runner.run_debug(image_path)
    
    print("\n" + "="*60)
    print("WORKFLOW COMPLETE")
    print("="*60)
    print(f"Final output: {result}")
    
    # Check output directories
    print("\nChecking generated local files:")
    print("extracted/ exists:", os.listdir("extracted"))
    print("evaluations/ exists:", os.listdir("evaluations"))
    print("reports/ exists:", os.listdir("reports"))
    print("spreadsheets/ exists:", os.listdir("spreadsheets"))
    if os.path.exists("spreadsheets/results.csv"):
        with open("spreadsheets/results.csv", "r", encoding="utf-8") as f:
            print("\nCSV Spreadsheet Content:")
            print(f.read())

if __name__ == "__main__":
    asyncio.run(main())
