from pathlib import Path

view_seg_code = '''import sys
from pathlib import Path

# Add backend directory to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import SimpleITK as sitk
import matplotlib.pyplot as plt
import numpy as np

CT_PATH = "../data/isotropic_volume.nii.gz"
SEG_DIR = Path("../data/segmentations")

def find_mask_file(base_name):
    """Finds mask file supporting both .nii and .nii.gz extensions."""
    for ext in [".nii.gz", ".nii"]:
        p = SEG_DIR / f"{base_name}{ext}"
        if p.exists():
            return p
    return None

def main():
    print("Loading CT volume...")
    if not Path(CT_PATH).exists():
        print(f"Error: CT volume not found at {CT_PATH}")
        return

    ct_image = sitk.ReadImage(CT_PATH)
    ct = sitk.GetArrayFromImage(ct_image)

    left_path = find_mask_file("kidney_left")
    right_path = find_mask_file("kidney_right")

    if not left_path or not right_path:
        print(f"Error: Mask files not found in {SEG_DIR}")
        return

    print(f"Loading left kidney mask:  {left_path.name}")
    print(f"Loading right kidney mask: {right_path.name}")

    left_image = sitk.ReadImage(str(left_path))
    right_image = sitk.ReadImage(str(right_path))

    left = sitk.GetArrayFromImage(left_image)
    right = sitk.GetArrayFromImage(right_image)

    # Locate slices containing kidney voxels
    kidney_mask = (left > 0) | (right > 0)
    z_indices = np.where(kidney_mask.any(axis=(1, 2)))[0]

    if len(z_indices) == 0:
        print("Error: No kidney voxels found in masks.")
        return

    # Select the middle slice along the Z-axis where kidneys appear
    z = z_indices[len(z_indices) // 2]
    print(f"Displaying axial slice z = {z}...")

    ct_slice = ct[z]
    left_slice = left[z] > 0
    right_slice = right[z] > 0

    # Apply soft-tissue CT windowing (-150 to 300 HU)
    window_min, window_max = -150, 300
    display_slice = np.clip(ct_slice, window_min, window_max)

    # Plot comparison figures
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    # Panel 1: Original CT
    axes[0].imshow(display_slice, cmap="gray", origin="lower")
    axes[0].set_title(f"CT - Axial Slice {z}")
    axes[0].axis("off")

    # Panel 2: Left Kidney Mask
    axes[1].imshow(display_slice, cmap="gray", origin="lower")
    axes[1].imshow(np.ma.masked_where(~left_slice, left_slice), cmap="Greens", alpha=0.5, origin="lower")
    axes[1].set_title("Left Kidney Overlay")
    axes[1].axis("off")

    # Panel 3: Both Kidney Masks
    axes[2].imshow(display_slice, cmap="gray", origin="lower")
    axes[2].imshow(np.ma.masked_where(~left_slice, left_slice), cmap="Greens", alpha=0.4, origin="lower")
    axes[2].imshow(np.ma.masked_where(~right_slice, right_slice), cmap="Oranges", alpha=0.4, origin="lower")
    axes[2].set_title("Both Kidneys Overlay")
    axes[2].axis("off")

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
'''

target = Path("backend/tests/view_segmentation.py")
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(view_seg_code, encoding="utf-8")
print(f"Created: {target.resolve()}")