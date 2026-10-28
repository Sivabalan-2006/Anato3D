import sys
from pathlib import Path

# Add backend directory to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import SimpleITK as sitk
import matplotlib.pyplot as plt
import numpy as np

VOLUME_PATH = "../data/isotropic_volume.nii.gz"

def main():
    print(f"Loading volume from: {VOLUME_PATH}")
    if not Path(VOLUME_PATH).exists():
        print(f"Error: File not found at {VOLUME_PATH}")
        return

    image = sitk.ReadImage(VOLUME_PATH)
    volume = sitk.GetArrayFromImage(image)
    print(f"Volume array shape (Z, Y, X): {volume.shape}")

    # Center slices along each orthoview plane
    z_center = volume.shape[0] // 2
    y_center = volume.shape[1] // 2
    x_center = volume.shape[2] // 2

    axial = volume[z_center, :, :]
    coronal = volume[:, y_center, :]
    sagittal = volume[:, :, x_center]

    # -----------------------------------------
    # DISPLAY MULTI-PLANAR VIEWS
    # -----------------------------------------
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # Axial Plane
    axes[0].imshow(axial, cmap="gray", origin="lower")
    axes[0].set_title(f"Axial - Slice {z_center}")
    axes[0].axis("off")

    # Coronal Plane
    axes[1].imshow(coronal, cmap="gray", origin="lower")
    axes[1].set_title(f"Coronal - Slice {y_center}")
    axes[1].axis("off")

    # Sagittal Plane
    axes[2].imshow(sagittal, cmap="gray", origin="lower")
    axes[2].set_title(f"Sagittal - Slice {x_center}")
    axes[2].axis("off")

    plt.tight_layout()
    print("Displaying multi-planar reconstruction (MPR)...")
    plt.show()

if __name__ == "__main__":
    main()
