from pathlib import Path
import numpy as np
import pydicom

from app.dicom.loader import find_dicom_files


def collect_dicom_metadata(directory: str):
    directory_path = Path(directory)

    datasets = []

    for file_path in find_dicom_files(directory):
        try:
            dataset = pydicom.dcmread(
                file_path,
                stop_before_pixels=True,
                force=False,
            )

            if getattr(dataset, "Modality", None) != "CT":
                continue

            if not hasattr(dataset, "ImagePositionPatient"):
                continue

            if not hasattr(dataset, "ImageOrientationPatient"):
                continue

            datasets.append(dataset)

        except Exception:
            continue

    if not datasets:
        raise ValueError("No valid CT DICOM series found.")

    # Calculate slice positions
    positions = []

    orientation = np.asarray(
        datasets[0].ImageOrientationPatient,
        dtype=float,
    )

    row_direction = orientation[:3]
    column_direction = orientation[3:]

    slice_direction = np.cross(
        row_direction,
        column_direction,
    )

    for dataset in datasets:
        position = np.asarray(
            dataset.ImagePositionPatient,
            dtype=float,
        )

        positions.append(
            float(np.dot(position, slice_direction))
        )

    # Sort spatially
    datasets = [
        dataset
        for _, dataset in sorted(
            zip(positions, datasets),
            key=lambda item: item[0],
        )
    ]

    positions = sorted(positions)

    if len(positions) > 1:
        spacing_values = np.diff(positions)
        slice_spacing = float(
            np.median(np.abs(spacing_values))
        )
    else:
        slice_spacing = float(
            getattr(
                datasets[0],
                "SliceThickness",
                1.0,
            )
        )

    first = datasets[0]

    pixel_spacing = [
        float(value)
        for value in first.PixelSpacing
    ]

    return {
        "modality": getattr(
            first,
            "Modality",
            "CT",
        ),

        "slices": len(datasets),

        "rows": int(
            getattr(first, "Rows", 0)
        ),

        "columns": int(
            getattr(first, "Columns", 0)
        ),

        "pixel_spacing": pixel_spacing,

        "slice_thickness": float(
            getattr(
                first,
                "SliceThickness",
                slice_spacing,
            )
        ),

        "slice_spacing": slice_spacing,

        "image_orientation": [
            float(value)
            for value in first.ImageOrientationPatient
        ],

        "origin": [
            float(value)
            for value in first.ImagePositionPatient
        ],

        "patient_position": getattr(
            first,
            "PatientPosition",
            None,
        ),
    }