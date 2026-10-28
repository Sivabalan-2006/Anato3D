import {
  Scan,
  Layers3,
  Ruler,
  MapPin,
  Rotate3D,
  Database,
} from "lucide-react";

function MetadataRow({ icon, label, value }) {
  return (
    <div className="metadata-row">
      <div className="metadata-label">
        {icon}
        <span>{label}</span>
      </div>

      <span className="metadata-value">
        {value}
      </span>
    </div>
  );
}

export default function StudyMetadata({ metadata }) {
  if (!metadata) {
    return (
      <div className="metadata-empty">
        No study metadata available.
      </div>
    );
  }

  const original = metadata.original || {};
  const reconstructed = metadata.reconstructed || {};

  return (
    <section className="metadata-panel">
      <div className="metadata-header">
        <div>
          <p className="section-label">DICOM / SPATIAL METADATA</p>
          <h3>Study Reconstruction Information</h3>
        </div>

        <div className="metadata-status">
          <Database size={16} />
          Metadata Verified
        </div>
      </div>

      <div className="metadata-grid">

        {/* Original DICOM */}
        <div className="metadata-card">
          <div className="metadata-card-header">
            <div className="metadata-icon">
              <Scan size={20} />
            </div>

            <div>
              <h4>Original DICOM Series</h4>
              <p>Source CT acquisition</p>
            </div>
          </div>

          <MetadataRow
            icon={<Layers3 size={15} />}
            label="Slices"
            value={`${original.slices ?? "N/A"}`}
          />

          <MetadataRow
            icon={<Ruler size={15} />}
            label="Image Resolution"
            value={
              original.rows && original.columns
                ? `${original.rows} × ${original.columns}`
                : "N/A"
            }
          />

          <MetadataRow
            icon={<Ruler size={15} />}
            label="Pixel Spacing"
            value={
              original.pixel_spacing
                ? `${original.pixel_spacing[0]} × ${original.pixel_spacing[1]} mm`
                : "N/A"
            }
          />

          <MetadataRow
            icon={<Layers3 size={15} />}
            label="Slice Thickness"
            value={
              original.slice_thickness != null
                ? `${original.slice_thickness} mm`
                : "N/A"
            }
          />

          <MetadataRow
            icon={<Scan size={15} />}
            label="Modality"
            value={original.modality ?? "N/A"}
          />
        </div>

        {/* Reconstructed */}
        <div className="metadata-card">
          <div className="metadata-card-header">
            <div className="metadata-icon">
              <Rotate3D size={20} />
            </div>

            <div>
              <h4>Reconstructed Volume</h4>
              <p>Spatially normalized volume</p>
            </div>
          </div>

          <MetadataRow
            icon={<Layers3 size={15} />}
            label="Volume Size"
            value={
              reconstructed.size
                ? reconstructed.size.join(" × ")
                : "N/A"
            }
          />

          <MetadataRow
            icon={<Ruler size={15} />}
            label="Voxel Spacing"
            value={
              reconstructed.spacing_mm
                ? `${reconstructed.spacing_mm.join(" × ")} mm`
                : "N/A"
            }
          />

          <MetadataRow
            icon={<MapPin size={15} />}
            label="Origin"
            value={
              reconstructed.origin
                ? reconstructed.origin
                    .map((value) => Number(value).toFixed(2))
                    .join(", ")
                : "N/A"
            }
          />

          <MetadataRow
            icon={<Rotate3D size={15} />}
            label="Direction"
            value={
              reconstructed.direction
                ? "Identity / Axial-aligned"
                : "N/A"
            }
          />

          <MetadataRow
            icon={<Scan size={15} />}
            label="Target Spacing"
            value="1 × 1 × 1 mm"
          />
        </div>
      </div>
    </section>
  );
}