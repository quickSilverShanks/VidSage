import os
import subprocess

# Set the LLM_MODEL environment variable
os.environ['TEMP_VAR'] = "gemma2:2b"

# Run the bash script
try:
    # The script path is './test.sh' assuming test.sh is in the same directory as test.py
    subprocess.run(["bash", "test.sh"], check=True)
    print("Bash script executed successfully.")
except subprocess.CalledProcessError as e:
    print(f"An error occurred while executing the script: {e}")
