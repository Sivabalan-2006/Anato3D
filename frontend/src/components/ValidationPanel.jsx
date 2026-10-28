import {
  CheckCircle2,
  AlertTriangle,
  Ruler,
  Triangle,
  Activity,
} from "lucide-react";

function KidneyValidation({ title, data }) {
  if (!data) {
    return <div className="validation-empty">No validation data available.</div>;
  }

  const maskVol = data.mask_volume_cm3 ?? data.mask_volume;
  const meshVol = data.volume_cm3 ?? data.mesh_volume_cm3;
  const absError = data.volume_error_cm3;
  const errorPct = data.volume_error_percent;
  const surfaceArea = data.surface_area_cm2;
  const vertices = data.vertices;
  const faces = data.faces;
  const watertight = data.watertight;
  const validVolume = data.valid_volume;
  const winding = data.winding_consistent;

  return (
    <div className="validation-card">
      <div className="validation-card-header">
        <h4>{title}</h4>
        <span className={`status-badge ${watertight ? "pass" : "fail"}`}>
          {watertight ? <CheckCircle2 size={14} /> : <AlertTriangle size={14} />}
          {watertight ? "Watertight Mesh" : "Mesh Issues"}
        </span>
      </div>

      <div className="validation-metrics">
        <div className="metric-row">
          <span className="metric-label"><Activity size={14} /> Mask Volume</span>
          <span className="metric-val">{maskVol != null ? `${Number(maskVol).toFixed(2)} cm³` : "N/A"}</span>
        </div>
        <div className="metric-row">
          <span className="metric-label"><Ruler size={14} /> Mesh Volume</span>
          <span className="metric-val">{meshVol != null ? `${Number(meshVol).toFixed(2)} cm³` : "N/A"}</span>
        </div>
        <div className="metric-row">
          <span className="metric-label"><Activity size={14} /> Abs Volume Error</span>
          <span className="metric-val">{absError != null ? `${Number(absError).toFixed(3)} cm³` : "N/A"}</span>
        </div>
        <div className="metric-row">
          <span className="metric-label"><Activity size={14} /> Volume Error %</span>
          <span className="metric-val highlight">{errorPct != null ? `${Number(errorPct).toFixed(2)}%` : "N/A"}</span>
        </div>
        <div className="metric-row">
          <span className="metric-label"><Ruler size={14} /> Surface Area</span>
          <span className="metric-val">{surfaceArea != null ? `${Number(surfaceArea).toFixed(2)} cm²` : "N/A"}</span>
        </div>
        {vertices != null && (
          <div className="metric-row">
            <span className="metric-label"><Triangle size={14} /> Geometry</span>
            <span className="metric-val">{vertices.toLocaleString()} v / {faces?.toLocaleString()} f</span>
          </div>
        )}
      </div>

      <div className="validation-checks">
        <div className="check-item">
          <span className="check-label">Watertight</span>
          <span className={watertight ? "check-pass" : "check-fail"}>
            {watertight ? "Pass" : "Fail"}
          </span>
        </div>
        <div className="check-item">
          <span className="check-label">Valid Volume</span>
          <span className={validVolume !== false ? "check-pass" : "check-fail"}>
            {validVolume !== false ? "Pass" : "Fail"}
          </span>
        </div>
        <div className="check-item">
          <span className="check-label">Winding</span>
          <span className={winding !== false ? "check-pass" : "check-fail"}>
            {winding !== false ? "Pass" : "Fail"}
          </span>
        </div>
      </div>
    </div>
  );
}

export default function ValidationPanel({ measurements }) {
  if (!measurements) return null;

  return (
    <div className="validation-panel">
      <div className="validation-grid">
        <KidneyValidation title="Left Kidney Validation" data={measurements.left_kidney} />
        <KidneyValidation title="Right Kidney Validation" data={measurements.right_kidney} />
      </div>
    </div>
  );
}