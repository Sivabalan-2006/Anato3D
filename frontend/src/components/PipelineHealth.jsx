import {
  CheckCircle2,
  XCircle,
  Database,
  Layers3,
  Box,
  ShieldCheck,
} from "lucide-react";

function HealthItem({ icon, label, available }) {
  return (
    <div className="health-item">
      <div className="health-item-left">
        <div className="health-icon">
          {icon}
        </div>

        <span>{label}</span>
      </div>

      <div className={available ? "health-pass" : "health-fail"}>
        {available ? (
          <>
            <CheckCircle2 size={16} />
            Ready
          </>
        ) : (
          <>
            <XCircle size={16} />
            Missing
          </>
        )}
      </div>
    </div>
  );
}

export default function PipelineHealth({ health }) {
  if (!health) return null;

  const components = health.components || {};

  return (
    <section className="pipeline-health">

      <div className="pipeline-health-header">
        <div>
          <p className="section-label">SYSTEM DIAGNOSTICS</p>
          <h3>Pipeline Health</h3>
        </div>

        <div
          className={
            health.pipeline_complete
              ? "health-summary complete"
              : "health-summary incomplete"
          }
        >
          {health.pipeline_complete ? (
            <>
              <CheckCircle2 size={16} />
              Pipeline Complete
            </>
          ) : (
            <>
              <XCircle size={16} />
              Pipeline Incomplete
            </>
          )}
        </div>
      </div>

      <div className="health-grid">

        <HealthItem
          icon={<Database size={18} />}
          label="Reconstructed CT Volume"
          available={components.volume?.available}
        />

        <HealthItem
          icon={<Layers3 size={18} />}
          label="Left Kidney Segmentation"
          available={components.left_segmentation?.available}
        />

        <HealthItem
          icon={<Layers3 size={18} />}
          label="Right Kidney Segmentation"
          available={components.right_segmentation?.available}
        />

        <HealthItem
          icon={<Box size={18} />}
          label="Left Kidney Mesh"
          available={components.left_mesh?.available}
        />

        <HealthItem
          icon={<Box size={18} />}
          label="Right Kidney Mesh"
          available={components.right_mesh?.available}
        />

        <HealthItem
          icon={<ShieldCheck size={18} />}
          label="Validation Report"
          available={components.validation_report?.available}
        />

      </div>
    </section>
  );
}