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
