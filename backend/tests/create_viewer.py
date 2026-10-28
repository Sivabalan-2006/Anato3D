import sys
from pathlib import Path

# Ensure backend package is in python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.visualization.mesh_viewer import create_kidney_viewer

# Resolve path relative to backend root
BASE_DATA = Path(__file__).resolve().parent.parent.parent / "data"

LEFT_MESH = BASE_DATA / "refined_meshes" / "kidney_left_refined.stl"
RIGHT_MESH = BASE_DATA / "refined_meshes" / "kidney_right_refined.stl"
OUTPUT_DIR = BASE_DATA / "viewer"
OUTPUT_FILE = OUTPUT_DIR / "kidney_model.html"

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    create_kidney_viewer(
        str(LEFT_MESH),
        str(RIGHT_MESH),
        str(OUTPUT_FILE)
    )

if __name__ == "__main__":
    main()
