import os
import sys
import asyncio

# Ensure app directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agent import app
from google.adk.runners import InMemoryRunner

async def main():
    print("="*60)
    print("RUNNING LIVE SCRIBED ANSWER SHEET BATCH EVALUATION")
    print("="*60)
    
    sample_dir = "sample"
    if not os.path.exists(sample_dir):
        print(f"Error: {sample_dir} does not exist!")
        return
        
    files = os.listdir(sample_dir)
    print(f"Found files in {sample_dir}: {files}")
    
    runner = InMemoryRunner(app=app)
    
    # Run the workflow with the sample directory path as input
    print(f"Starting workflow execution on directory '{sample_dir}'...")
    result = await runner.run_debug(sample_dir)
    
    print("\n" + "="*60)
    print("WORKFLOW COMPLETE")
    print("="*60)
    print(f"Final output: {result}")
    
    # Check output directories
    print("\nChecking generated local files:")
    if os.path.exists("extracted"):
        print("extracted/ exists:", os.listdir("extracted"))
    if os.path.exists("evaluations"):
        print("evaluations/ exists:", os.listdir("evaluations"))
    if os.path.exists("reports"):
        print("reports/ exists:", os.listdir("reports"))
    if os.path.exists("spreadsheets"):
        print("spreadsheets/ exists:", os.listdir("spreadsheets"))
    if os.path.exists("batch_reports"):
        print("batch_reports/ exists:", os.listdir("batch_reports"))
        
    if os.path.exists("spreadsheets/results.csv"):
        with open("spreadsheets/results.csv", "r", encoding="utf-8") as f:
            print("\nCSV Spreadsheet Content:")
            print(f.read())

if __name__ == "__main__":
    asyncio.run(main())
