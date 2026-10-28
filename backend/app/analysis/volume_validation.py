def calculate_volume_error(mask_volume_cm3, mesh_volume_cm3):
    """
    Calculate absolute and percentage difference between mask and mesh volume.
    """
    absolute_error = abs(mask_volume_cm3 - mesh_volume_cm3)
    if mask_volume_cm3 == 0:
        percentage_error = 0.0
    else:
        percentage_error = (absolute_error / mask_volume_cm3) * 100.0

    return {
        "mask_volume_cm3": mask_volume_cm3,
        "mesh_volume_cm3": mesh_volume_cm3,
        "absolute_error_cm3": absolute_error,
        "percentage_error": percentage_error
    }
