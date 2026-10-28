import numpy as np

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
