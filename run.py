import subprocess
import sys
from pathlib import Path

# Helper for the VS Code Run button: feeds input.txt to subset_construction.py
# and also writes output.html next to it
here = Path(__file__).parent
name = sys.argv[1] if len(sys.argv) > 1 else "input.txt"
with open(here / name) as f:
    subprocess.run([sys.executable, str(here / "subset_construction.py"),
                "--html", str(here / "output.html")], stdin=f)
