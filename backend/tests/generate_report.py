import sys
from pathlib import Path

# Add backend directory to Python search path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.analysis.report import generate_report

if __name__ == "__main__":
    generate_report()
