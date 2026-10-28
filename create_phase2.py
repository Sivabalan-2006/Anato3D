from pathlib import Path

FILES = {
    "backend/app/dicom/ordering.py": '''import numpy as np

def get_slice_position(dataset):
    """
    Calculate the physical position of a DICOM slice.
    Uses ImagePositionPatient and ImageOrientationPatient
    to determine the slice coordinate in 3D space.
    """
    position = np.asarray(dataset.ImagePositionPatient, dtype=float)
    orientation = np.asarray(dataset.ImageOrientationPatient, dtype=float)
    row_direction = orientation[:3]
    column_direction = orientation[3:]

    # Slice direction is perpendicular to the image plane
    slice_direction = np.cross(row_direction, column_direction)

    # Project the image position onto the slice direction
    slice_coordinate = np.dot(position, slice_direction)
    return slice_coordinate

def sort_slices(datasets):
    """
    Sort DICOM datasets according to their physical
    position rather than their filename.
    """
    slices_with_positions = []
    for dataset in datasets:
        position = get_slice_position(dataset)
        slices_with_positions.append((position, dataset))

    slices_with_positions.sort(key=lambda item: item[0])
    return [dataset for _, dataset in slices_with_positions]

def calculate_slice_spacing(datasets):
    """
    Calculate the physical distance between
    consecutive DICOM slices.
    """
    positions = [get_slice_position(dataset) for dataset in datasets]
    positions = np.asarray(positions)
    if len(positions) < 2:
        return []
    return np.diff(positions)
''',

    "backend/app/reconstruction/volume.py": '''import numpy as np
import SimpleITK as sitk

def dicom_to_hu(dataset):
    """
    Convert DICOM pixel values to Hounsfield Units.
    """
    image = dataset.pixel_array.astype(np.float32)
    slope = float(getattr(dataset, "RescaleSlope", 1.0))
    intercept = float(getattr(dataset, "RescaleIntercept", 0.0))
    hu = image * slope + intercept
    return hu

def create_volume(datasets):
    """
    Create a 3D volume from ordered DICOM datasets.
    """
    slices = [dicom_to_hu(dataset) for dataset in datasets]
    volume_array = np.stack(slices, axis=0)
    image = sitk.GetImageFromArray(volume_array)

    # Pixel spacing
    pixel_spacing = [float(x) for x in datasets[0].PixelSpacing]

    # Slice spacing
    if len(datasets) > 1:
        from app.dicom.ordering import calculate_slice_spacing
        spacing_values = calculate_slice_spacing(datasets)
        slice_spacing = float(np.median(np.abs(spacing_values)))
    else:
        slice_spacing = float(getattr(datasets[0], "SliceThickness", 1.0))

    # SimpleITK spacing order is: X, Y, Z
    image.SetSpacing((pixel_spacing[1], pixel_spacing[0], slice_spacing))
    return image
''',

    "backend/tests/test_reconstruction.py": '''import sys
from pathlib import Path

# Add backend directory to Python search path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import SimpleITK as sitk
from app.dicom.loader import find_dicom_files, load_dicom_file
from app.dicom.ordering import sort_slices, calculate_slice_spacing
from app.reconstruction.volume import create_volume

DICOM_DIR = "../data/dicom/sample"

def main():
    # Find files
    files = find_dicom_files(DICOM_DIR)
    print(f"DICOM files found: {len(files)}")

    # Load datasets
    datasets = []
    for file_path in files:
        try:
            dataset = load_dicom_file(file_path)
            if getattr(dataset, "Modality", None) == "CT":
                datasets.append(dataset)
        except Exception as error:
            print(f"Skipping {file_path}: {error}")

    print(f"CT slices loaded: {len(datasets)}")

    # Sort slices spatially
    datasets = sort_slices(datasets)
    print("\\nSlice ordering completed.")

    # Calculate spacing
    spacing = calculate_slice_spacing(datasets)
    print("\\nSlice spacing:")
    print(f"Minimum: {spacing.min():.4f} mm")
    print(f"Maximum: {spacing.max():.4f} mm")
    print(f"Median: {np.median(abs(spacing)):.4f} mm")

    # Create volume
    volume = create_volume(datasets)
    print("\\n3D Volume")
    print("=" * 40)
    print(f"Size: {volume.GetSize()}")
    print(f"Spacing: {volume.GetSpacing()}")
    print(f"Origin: {volume.GetOrigin()}")
    print(f"Direction: {volume.GetDirection()}")

    # Save volume
    output_path = "../data/reconstructed_volume.nii.gz"
    sitk.WriteImage(volume, output_path)
    print(f"\\nVolume saved to: {output_path}")

if __name__ == "__main__":
    main()
'''
}

for rel_path, content in FILES.items():
    p = Path(rel_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"Created: {p.resolve()}")

print("\nPhase 2 files successfully created!")