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
