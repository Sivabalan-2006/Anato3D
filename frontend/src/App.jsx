import { useEffect, useState } from "react";
import { Activity, Box, CheckCircle2, FileImage, HeartPulse, Layers3, RefreshCw, Scan } from "lucide-react";
import KidneyViewer from "./components/KidneyViewer";
import CTViewer from "./components/CTViewer";
import SegmentationOverlay from "./components/SegmentationOverlay";
import ValidationPanel from "./components/ValidationPanel";
import StudyMetadata from "./components/StudyMetadata";
import PipelineHealth from "./components/PipelineHealth";

function App() {
  const [study, setStudy] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [systemHealthy, setSystemHealthy] = useState(false);
  const [health, setHealth] = useState(null);

  const fetchStudy = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch("http://localhost:8000/api/studies/current");
          if (!response.ok) {
            throw new Error("Failed to connect to Anato3D API");
          }
          const data = await response.json();
          setStudy(data);
          const healthResponse = await fetch(
      "http://localhost:8000/api/health"
    );

if (healthResponse.ok) {
  const health = await healthResponse.json();
  setHealth(healthData);
  setSystemHealthy(health.pipeline_complete === true);
} else {
   setHealth(null);
  setSystemHealthy(false);
}
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStudy();
  }, []);

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <div className="brand-icon">
            <Scan size={25} />
          </div>
          <div>
            <h1>Anato3D</h1>
            <p>Patient-Specific Anatomical Reconstruction</p>
          </div>
        </div>
            <div className={`system-status ${systemHealthy ? "online" : "offline"}`}>
      <span className="status-dot"></span>
      {systemHealthy ? "System Online" : "System Incomplete"}
    </div>
      </header>

      <main className="container">
        <section className="hero">
          <div>
            <p className="eyebrow">MEDICAL IMAGING PLATFORM</p>
            <h2>3D Anatomical <br /> Reconstruction</h2>
            <p className="hero-text">
              Convert DICOM imaging data into spatially accurate, patient-specific 3D anatomical models.
            </p>
          </div>
          <div className="hero-icon">
            <HeartPulse size={90} strokeWidth={1} />
          </div>
        </section>

        {loading && (
          <div className="message">
            <RefreshCw className="spin" size={20} /> Loading study...
          </div>
        )}

        {error && (
          <div className="message error">
            <Activity size={20} /> {error}
          </div>
        )}

        {study && (
          <>
            <section className="study-header">
              <div>
                <p className="section-label">CURRENT STUDY</p>
                <h3>{study.study_id}</h3>
              </div>
              <div className="completed">
                <CheckCircle2 size={18} /> {study.status}
              </div>
            </section>

            <section className="cards">
              <InfoCard icon={<FileImage />} title="Imaging" value={study.modality} description="DICOM CT study" />
              <InfoCard icon={<Layers3 />} title="3D Volume" value={study.outputs.volume ? "Ready" : "Missing"} description="Isotropic reconstruction" success={study.outputs.volume} />
              <InfoCard icon={<Box />} title="Left Kidney" value={study.outputs.left_kidney_mesh ? "Ready" : "Missing"} description="Patient-specific mesh" success={study.outputs.left_kidney_mesh} />
              <InfoCard icon={<Box />} title="Right Kidney" value={study.outputs.right_kidney_mesh ? "Ready" : "Missing"} description="Patient-specific mesh" success={study.outputs.right_kidney_mesh} />
            </section>

            <StudyMetadata metadata={study.metadata} />
            <PipelineHealth health={health} />
            <section className="pipeline">
              <div className="section-heading">
                <div>
                  <p className="section-label">PROCESSING PIPELINE</p>
                  <h3>Reconstruction Status</h3>
                </div>
                <button onClick={fetchStudy}>
                  <RefreshCw size={16} /> Refresh
                </button>
              </div>
              <PipelineStep number="01" title="DICOM Ingestion" description="Read and validate medical imaging data" completed={true} />
              <PipelineStep number="02" title="3D Volume Reconstruction" description="Spatially ordered CT slices converted into isotropic volume" completed={study.outputs.volume} />
              <PipelineStep
                number="03"
                title="AI Segmentation"
                description="Automatic anatomical structure segmentation"
                completed={
                  study.outputs.left_kidney_segmentation &&
                  study.outputs.right_kidney_segmentation
                }
              />
              <PipelineStep number="04" title="Mesh Generation" description="Marching Cubes reconstruction and mesh refinement" completed={study.outputs.left_kidney_mesh && study.outputs.right_kidney_mesh} />
              <PipelineStep number="05" title="Validation" description="Geometry and anatomical reconstruction validation" completed={study.outputs.validation_report} />
            </section>

            <section className="viewer-section">
              <div className="section-heading">
                <div>
                  <p className="section-label">MEDICAL IMAGE</p>
                  <h3>Reconstructed CT Volume</h3>
                </div>
              </div>
              <CTViewer />
            </section>

            <section className="viewer-section">
              <div className="section-heading">
                <div>
                  <p className="section-label">AI VALIDATION</p>
                  <h3>CT / Segmentation Alignment</h3>
                </div>
              </div>
              <SegmentationOverlay />
            </section>

            <section className="viewer-section">
              <div className="section-heading">
                <div>
                  <p className="section-label">3D ANATOMICAL MODEL</p>
                  <h3>Patient-Specific Kidney Reconstruction</h3>
                </div>
              </div>
              <KidneyViewer measurements={study.measurements} />
            </section>

            <section className="viewer-section">
              <div className="section-heading">
                <div>
                  <p className="section-label">QUALITY CONTROL</p>
                  <h3>Reconstruction Validation</h3>
                </div>
              </div>
              <ValidationPanel measurements={study.measurements} />
            </section>
          </>
        )}
      </main>
    </div>
  );
}

function InfoCard({ icon, title, value, description, success }) {
  return (
    <div className="card">
      <div className="card-icon">{icon}</div>
      <p className="card-title">{title}</p>
      <h4 className={success === false ? "missing" : ""}>{value}</h4>
      <p className="card-description">{description}</p>
    </div>
  );
}

function PipelineStep({ number, title, description, completed }) {
  return (
    <div className="pipeline-step">
      <div className="step-number">{number}</div>
      <div className="step-content">
        <h4>{title}</h4>
        <p>{description}</p>
      </div>
      <div className={completed ? "step-status done" : "step-status"}>
        {completed ? (
          <>
            <CheckCircle2 size={18} /> Complete
          </>
        ) : (
          "Pending"
        )}
      </div>
    </div>
  );
}

export default App;