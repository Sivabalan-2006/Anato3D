from pathlib import Path

check_segmentation_code = '''import sys
from pathlib import Path

# Add backend directory to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import SimpleITK as sitk
import numpy as np

SEGMENTATION_DIR = Path("../data/segmentations")

def inspect_mask(filename):
    path = SEGMENTATION_DIR / filename
    print("\\n" + "=" * 50)
    print(f"Checking: {filename}")
    print("=" * 50)

    if not path.exists():
        print(f"Error: File not found at {path}")
        return

    image = sitk.ReadImage(str(path))
    mask = sitk.GetArrayFromImage(image)

    print(f"Shape: {mask.shape}")
    print(f"Spacing: {image.GetSpacing()}")
    print(f"Origin: {image.GetOrigin()}")
    print(f"Direction: {image.GetDirection()}")

    voxel_count = np.count_nonzero(mask)
    print(f"Mask voxels: {voxel_count}")

    voxel_spacing = image.GetSpacing()
    voxel_volume_mm3 = voxel_spacing[0] * voxel_spacing[1] * voxel_spacing[2]
    volume_cm3 = (voxel_count * voxel_volume_mm3) / 1000.0
    print(f"Volume: {volume_cm3:.2f} cm³")

def main():
    inspect_mask("kidney_left.nii.gz")
    inspect_mask("kidney_right.nii.gz")

if __name__ == "__main__":
    main()
'''

target = Path("backend/tests/check_segmentation.py")
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(check_segmentation_code, encoding="utf-8")
print(f"Created: {target.resolve()}")