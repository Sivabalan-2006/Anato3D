import SimpleITK as sitk

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
