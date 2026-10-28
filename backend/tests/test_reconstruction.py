import sys
from pathlib import Path

# Add backend directory to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import SimpleITK as sitk
from app.dicom.loader import find_dicom_files, load_dicom_file
from app.dicom.ordering import sort_slices, calculate_slice_spacing
from app.reconstruction.volume import create_volume
from app.reconstruction.resampling import resample_isotropic
from app.reconstruction.preprocessing import clip_ct

DICOM_DIR = "../data/dicom/sample"

def main():
    # 1. FIND DICOM FILES
    files = find_dicom_files(DICOM_DIR)
    print(f"DICOM files found: {len(files)}")

    # 2. LOAD CT DATASETS
    datasets = []
    for file_path in files:
        try:
            dataset = load_dicom_file(file_path)
            if getattr(dataset, "Modality", None) == "CT":
                datasets.append(dataset)
        except Exception as error:
            print(f"Skipping {file_path}: {error}")

    print(f"CT slices loaded: {len(datasets)}")

    # 3. SORT SLICES
    datasets = sort_slices(datasets)
    print("\nSlice ordering completed.")

    # 4. CHECK SPACING
    spacing = calculate_slice_spacing(datasets)
    print("\nSlice spacing:")
    print(f"Minimum: {spacing.min():.4f} mm")
    print(f"Maximum: {spacing.max():.4f} mm")
    print(f"Median:  {np.median(abs(spacing)):.4f} mm")

    # 5. CREATE ORIGINAL VOLUME
    volume = create_volume(datasets)
    print("\nOriginal 3D Volume")
    print("=" * 40)
    print(f"Size: {volume.GetSize()}")
    print(f"Spacing: {volume.GetSpacing()}")
    print(f"Origin: {volume.GetOrigin()}")
    print(f"Direction: {volume.GetDirection()}")

    # 6. SAVE ORIGINAL VOLUME
    original_path = "../data/original_volume.nii.gz"
    sitk.WriteImage(volume, original_path)
    print(f"\nOriginal volume saved to:\n{original_path}")

    # 7. CLIP CT
    processed = clip_ct(volume)

    # 8. RESAMPLE
    print("\nResampling to 1 x 1 x 1 mm...")
    isotropic = resample_isotropic(processed, target_spacing=(1.0, 1.0, 1.0))

    print("\nResampled Volume")
    print("=" * 40)
    print(f"Size: {isotropic.GetSize()}")
    print(f"Spacing: {isotropic.GetSpacing()}")
    print(f"Origin: {isotropic.GetOrigin()}")

    # 9. SAVE RESAMPLED VOLUME
    output_path = "../data/isotropic_volume.nii.gz"
    sitk.WriteImage(isotropic, output_path)
    print(f"\nIsotropic volume saved to:\n{output_path}")

if __name__ == "__main__":
    main()
