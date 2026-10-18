import os
import subprocess
import sys


def run():
    """CLI launcher for the OneProcess Streamlit dashboard."""
    print("\n" + "=" * 55)
    print("OneProcess Data Processing & Analytics Toolkit")
    print("Launching Data Processing Tool...")
    print("=" * 55 + "\n")

    # Locate app.py in the same directory as this cli.py
    current_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(current_dir, "app.py")

    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", app_path])
    except KeyboardInterrupt:
        print("\nOneProcess stopped.")


if __name__ == "__main__":
    run()