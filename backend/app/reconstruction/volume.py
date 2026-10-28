import numpy as np
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
