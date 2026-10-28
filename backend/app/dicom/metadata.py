def extract_metadata(dataset):
    """Extract spatial and image metadata for 3D reconstruction."""
    def get_value(attribute, default=None):
        return getattr(dataset, attribute, default)

    return {
        "modality": get_value("Modality"),
        "study_instance_uid": get_value("StudyInstanceUID"),
        "series_instance_uid": get_value("SeriesInstanceUID"),
        "sop_instance_uid": get_value("SOPInstanceUID"),
        "rows": get_value("Rows"),
        "columns": get_value("Columns"),
        "pixel_spacing": get_value("PixelSpacing"),
        "slice_thickness": get_value("SliceThickness"),
        "spacing_between_slices": get_value("SpacingBetweenSlices"),
        "image_position_patient": get_value("ImagePositionPatient"),
        "image_orientation_patient": get_value("ImageOrientationPatient"),
        "patient_position": get_value("PatientPosition"),
        "rescale_slope": get_value("RescaleSlope", 1.0),
        "rescale_intercept": get_value("RescaleIntercept", 0.0),
    }
