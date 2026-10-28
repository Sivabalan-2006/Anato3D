import sys
from pathlib import Path

# Add backend directory to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.mesh.marching_cubes import mask_to_mesh
from app.mesh.export import export_mesh

SEGMENTATION_DIR = Path("../data/segmentations")
OUTPUT_DIR = Path("../data/meshes")

def process_kidney(input_filename, output_filename):
    input_path = SEGMENTATION_DIR / input_filename
    
    # Support both .nii.gz and .nii extensions
    if not input_path.exists():
        alt_name = input_filename.replace(".nii.gz", ".nii") if input_filename.endswith(".nii.gz") else input_filename + ".gz"
        input_path = SEGMENTATION_DIR / alt_name

    output_path = OUTPUT_DIR / output_filename
    vertices, faces = mask_to_mesh(str(input_path), str(output_path))
    export_mesh(vertices, faces, str(output_path))

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("\nGenerating LEFT kidney mesh...")
    process_kidney("kidney_left.nii.gz", "kidney_left.stl")

    print("\nGenerating RIGHT kidney mesh...")
    process_kidney("kidney_right.nii.gz", "kidney_right.stl")

if __name__ == "__main__":
    main()
