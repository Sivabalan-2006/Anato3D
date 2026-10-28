import SimpleITK as sitk

def clip_ct(image, minimum=-1000, maximum=2000):
    """
    Clip CT intensity values to a useful Hounsfield Unit range.
    """
    return sitk.Clamp(image, lowerBound=minimum, upperBound=maximum)
