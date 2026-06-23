import os
import shutil

def clear_directory_except_gitkeep(directory):
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                if filename != ".gitkeep":
                    os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")
            
    # Ensure .gitkeep is present
    gitkeep_path = os.path.join(directory, ".gitkeep")
    if not os.path.exists(gitkeep_path):
        with open(gitkeep_path, "w") as f:
            pass
    print(f"Cleared directory: {directory}")

def main():
    print("="*60)
    print("RUNNING SCRIPTEAI WORKSPACE CLEANUP")
    print("="*60)
    
    # 1. Clear output directories
    dirs_to_clean = [
        "uploads",
        "extracted",
        "evaluations",
        "reports",
        "spreadsheets",
        "batch_reports"
    ]
    for d in dirs_to_clean:
        clear_directory_except_gitkeep(d)
        
    # 2. Clean scratch directory (remove answer sheets, keep .py scripts)
    scratch_dir = "scratch"
    if os.path.exists(scratch_dir):
        for filename in os.listdir(scratch_dir):
            file_path = os.path.join(scratch_dir, filename)
            ext = os.path.splitext(filename)[1].lower()
            if ext in (".jpg", ".jpeg", ".png", ".webp", ".pdf"):
                try:
                    os.unlink(file_path)
                    print(f"Deleted test answer sheet: {file_path}")
                except Exception as e:
                    print(f"Failed to delete {file_path}: {e}")
            elif os.path.isdir(file_path):
                try:
                    shutil.rmtree(file_path)
                    print(f"Deleted directory: {file_path}")
                except Exception as e:
                    print(f"Failed to delete directory {file_path}: {e}")
                    
        # Ensure .gitkeep in scratch
        gitkeep_path = os.path.join(scratch_dir, ".gitkeep")
        if not os.path.exists(gitkeep_path):
            with open(gitkeep_path, "w") as f:
                pass
                
    print("\nCleanup complete! Workspace is clean and prepared for real grading.")

if __name__ == "__main__":
    main()
