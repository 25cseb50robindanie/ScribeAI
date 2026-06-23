import os
import sys
import asyncio
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agent import app
from google.adk.runners import InMemoryRunner

async def main():
    print("="*60)
    print("VERIFYING ENHANCED PIPELINE ON NEW SCHEMA & PDFs")
    print("="*60)
    
    # We will pass the list of files to process as a batch
    batch_files = [
        "scratch/Student_Somewhat_Correct.pdf",
        "scratch/Student_Cheater_Bad.pdf"
    ]
    
    # Verify both exist
    for f in batch_files:
        if not os.path.exists(f):
            print(f"Error: {f} not found!")
            return
            
    runner = InMemoryRunner(app=app)
    
    # Passing a list to the welcome node triggers the batch logic
    print(f"Starting batch workflow execution for {batch_files}...")
    result = await runner.run_debug(json.dumps(batch_files))
    
    print("\n" + "="*60)
    print("BATCH RUN COMPLETE")
    print("="*60)
    print(f"Final output: {result}")
    
    # Print the CSV contents to inspect the results
    csv_path = "spreadsheets/results.csv"
    if os.path.exists(csv_path):
        with open(csv_path, "r", encoding="utf-8") as f:
            print("\nCSV Spreadsheet ledger:")
            print(f.read())
            
    # Check if reports were generated
    print("\nChecking generated local files:")
    print("extracted/ exists:", os.listdir("extracted"))
    print("evaluations/ exists:", os.listdir("evaluations"))
    print("reports/ exists:", os.listdir("reports"))
    print("spreadsheets/ exists:", os.listdir("spreadsheets"))
    print("batch_reports/ exists:", os.listdir("batch_reports"))

if __name__ == "__main__":
    asyncio.run(main())
