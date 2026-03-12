import subprocess
import sys

if __name__ == "__main__":
    print("🚀 Starting Adaptive Learning Coach...")
    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        "streamlit_app.py",
        "--server.port=8502",
        "--server.headless=false"
    ])
