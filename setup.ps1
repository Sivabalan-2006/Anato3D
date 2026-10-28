# 1. Create Directory Tree
$directories = @(
    "Anato3D/frontend",
    "Anato3D/data/dicom/sample",
    "Anato3D/models",
    "Anato3D/notebooks",
    "Anato3D/scripts",
    "Anato3D/docs",
    "Anato3D/backend/app/dicom",
    "Anato3D/backend/app/reconstruction",
    "Anato3D/backend/app/quality",
    "Anato3D/backend/app/segmentation",
    "Anato3D/backend/app/mesh",
    "Anato3D/backend/app/analysis",
    "Anato3D/backend/tests"
)

foreach ($dir in $directories) {
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
}

Set-Location Anato3D/backend

# 2. Setup Virtual Environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Install Dependencies & Freeze
pip install pydicom SimpleITK numpy scipy scikit-image matplotlib
pip freeze > requirements.txt

# 4. Create Empty __init__.py Files
$initPaths = @(
    "app/__init__.py",
    "app/dicom/__init__.py",
    "app/reconstruction/__init__.py",
    "app/quality/__init__.py",
    "app/segmentation/__init__.py",
    "app/mesh/__init__.py",
    "app/analysis/__init__.py",
    "app/main.py",
    "app/dicom/series.py",
    "app/dicom/ordering.py",
    "app/reconstruction/volume.py",
    "app/reconstruction/resampling.py",
    "app/reconstruction/preprocessing.py",
    "app/quality/metadata_checks.py",
    "app/quality/spacing_checks.py"
)

foreach ($file in $initPaths) {
    New-Item -ItemType File -Path $file -Force | Out-Null
}

# 5. Populate Modules
@'
from pathlib import Path
import pydicom

def find_dicom_files(directory: str) -> list[Path]:
    """Find all files that can potentially contain DICOM data."""
    directory_path = Path(directory)
    if not directory_path.exists():
        raise FileNotFoundError(f"DICOM directory does not exist: {directory}")
    if not directory_path.is_dir():
        raise NotADirectoryError(f"Expected a directory: {directory}")
    return [file_path for file_path in directory_path.rglob("*") if file_path.is_file()]

def load_dicom_file(file_path: str):
    """Read a single DICOM file."""
    return pydicom.dcmread(file_path, force=False)
'@ | Set-Content -Path "app/dicom/loader.py"

@'
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
'@ | Set-Content -Path "app/dicom/metadata.py"

@'
from app.dicom.loader import find_dicom_files, load_dicom_file
from app.dicom.metadata import extract_metadata

DICOM_DIR = "../data/dicom/sample"

def main():
    files = find_dicom_files(DICOM_DIR)
    print(f"DICOM files found: {len(files)}")
    if not files:
        print("No files found.")
        return

    print("\nReading first DICOM file...")
    dataset = load_dicom_file(files[0])
    metadata = extract_metadata(dataset)

    print("\nDICOM Metadata")
    print("=" * 40)
    for key, value in metadata.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    main()
'@ | Set-Content -Path "tests/test_dicom.py"

Write-Host "`nAnato3D setup completed successfully!" -ForegroundColor Green