import subprocess
import os
import sys

def check_for_updates():
    repo_path = os.path.dirname(os.path.abspath(__file__))

    try:
        subprocess.run(["git", "-C", repo_path, "fetch"], check=True)
        local = subprocess.check_output(["git", "-C", repo_path, "rev-parse", "HEAD"]).strip()
        remote = subprocess.check_output(["git", "-C", repo_path, "rev-parse", "@{u}"]).strip()

        if local != remote:
            print("Update available.")
            confirm = input("Install update now? (y/N): ").strip().lower()
            if confirm == "y":
                subprocess.run(["git", "-C", repo_path, "pull"], check=True)
                subprocess.run([os.path.join(repo_path, "venv", "bin", "pip"), "install", "-r", os.path.join(repo_path, "requirements.txt")], check=True)
                print("Updated. Please restart the app.")
                sys.exit(0)
            else:
                print("Continuing without update.")
        else:
            print("App is up to date.")
    except Exception as e:
        print(f"Update check failed: {e}")

