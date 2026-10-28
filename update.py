from pathlib import Path

FILES = {
    "backend/app/reconstruction/volume.py": '''import numpy as np
import SimpleITK as sitk
from app.dicom.ordering import calculate_slice_spacing

def dicom_to_hu(dataset):
    """
    Convert DICOM stored pixel values to Hounsfield Units.
    """
    image = dataset.pixel_array.astype(np.float32)
    slope = float(getattr(dataset, "RescaleSlope", 1.0))
    intercept = float(getattr(dataset, "RescaleIntercept", 0.0))
    return image * slope + intercept

def get_direction_cosines(dataset):
    """
    Build the 3D direction matrix from ImageOrientationPatient.
    """
    orientation = np.asarray(dataset.ImageOrientationPatient, dtype=float)
    row_direction = orientation[:3]
    column_direction = orientation[3:]

    # Direction perpendicular to image plane
    slice_direction = np.cross(row_direction, column_direction)
    direction_matrix = np.column_stack(
        (row_direction, column_direction, slice_direction)
    )
    return tuple(direction_matrix.flatten())

def create_volume(datasets):
    """
    Create a spatially aware 3D volume from ordered DICOM datasets.
    """
    if not datasets:
        raise ValueError("No DICOM datasets supplied.")

    # Convert all slices to HU
    slices = [dicom_to_hu(dataset) for dataset in datasets]
    volume_array = np.stack(slices, axis=0)
    image = sitk.GetImageFromArray(volume_array)

    # -----------------------------------------
    # SPACING
    # -----------------------------------------
    pixel_spacing = [float(value) for value in datasets[0].PixelSpacing]
    if len(datasets) > 1:
        spacing_values = calculate_slice_spacing(datasets)
        slice_spacing = float(np.median(np.abs(spacing_values)))
    else:
        slice_spacing = float(getattr(datasets[0], "SliceThickness", 1.0))

    image.SetSpacing((pixel_spacing[1], pixel_spacing[0], slice_spacing))

    # -----------------------------------------
    # ORIGIN
    # -----------------------------------------
    origin = tuple(float(value) for value in datasets[0].ImagePositionPatient)
    image.SetOrigin(origin)

    # -----------------------------------------
    # DIRECTION
    # -----------------------------------------
    direction = get_direction_cosines(datasets[0])
    image.SetDirection(direction)

    return image
''',

    "backend/app/reconstruction/resampling.py": '''import SimpleITK as sitk

def resample_isotropic(image, target_spacing=(1.0, 1.0, 1.0)):
    """
    Resample a 3D medical image to isotropic spacing.
    """
    original_spacing = image.GetSpacing()
    original_size = image.GetSize()

    # Calculate new image dimensions
    new_size = [
        int(round(original_size[i] * original_spacing[i] / target_spacing[i]))
        for i in range(3)
    ]

    resampler = sitk.ResampleImageFilter()
    resampler.SetOutputSpacing(target_spacing)
    resampler.SetSize(new_size)
    resampler.SetOutputDirection(image.GetDirection())
    resampler.SetOutputOrigin(image.GetOrigin())

    # Preserve physical extent
    resampler.SetTransform(sitk.Transform())

    # CT intensity interpolation
    resampler.SetInterpolator(sitk.sitkLinear)

    # Default pixel value for background (Air HU)
    resampler.SetDefaultPixelValue(-1024)

    return resampler.Execute(image)
''',

    "backend/app/reconstruction/preprocessing.py": '''import SimpleITK as sitk

def clip_ct(image, minimum=-1000, maximum=2000):
    """
    Clip CT intensity values to a useful Hounsfield Unit range.
    """
    return sitk.Clamp(image, lowerBound=minimum, upperBound=maximum)
''',

    "backend/tests/test_reconstruction.py": '''import sys
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
    print("\\nSlice ordering completed.")

    # 4. CHECK SPACING
    spacing = calculate_slice_spacing(datasets)
    print("\\nSlice spacing:")
    print(f"Minimum: {spacing.min():.4f} mm")
    print(f"Maximum: {spacing.max():.4f} mm")
    print(f"Median:  {np.median(abs(spacing)):.4f} mm")

    # 5. CREATE ORIGINAL VOLUME
    volume = create_volume(datasets)
    print("\\nOriginal 3D Volume")
    print("=" * 40)
    print(f"Size: {volume.GetSize()}")
    print(f"Spacing: {volume.GetSpacing()}")
    print(f"Origin: {volume.GetOrigin()}")
    print(f"Direction: {volume.GetDirection()}")

    # 6. SAVE ORIGINAL VOLUME
    original_path = "../data/original_volume.nii.gz"
    sitk.WriteImage(volume, original_path)
    print(f"\\nOriginal volume saved to:\\n{original_path}")

    # 7. CLIP CT
    processed = clip_ct(volume)

    # 8. RESAMPLE
    print("\\nResampling to 1 x 1 x 1 mm...")
    isotropic = resample_isotropic(processed, target_spacing=(1.0, 1.0, 1.0))

    print("\\nResampled Volume")
    print("=" * 40)
    print(f"Size: {isotropic.GetSize()}")
    print(f"Spacing: {isotropic.GetSpacing()}")
    print(f"Origin: {isotropic.GetOrigin()}")

    # 9. SAVE RESAMPLED VOLUME
    output_path = "../data/isotropic_volume.nii.gz"
    sitk.WriteImage(isotropic, output_path)
    print(f"\\nIsotropic volume saved to:\\n{output_path}")

if __name__ == "__main__":
    main()
'''
}

for rel_path, content in FILES.items():
    p = Path(rel_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"Updated: {p.resolve()}")

print("\nAll files successfully updated!")