from pathlib import Path

FILES = {
    "backend/app/api/studies.py": '''from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(prefix="/api/studies", tags=["Studies"])

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"

LEFT_MESH = DATA_DIR / "refined_meshes" / "kidney_left_refined.stl"
if not LEFT_MESH.exists():
    LEFT_MESH = DATA_DIR / "meshes" / "kidney_left.stl"

RIGHT_MESH = DATA_DIR / "refined_meshes" / "kidney_right_refined.stl"
if not RIGHT_MESH.exists():
    RIGHT_MESH = DATA_DIR / "meshes" / "kidney_right.stl"

ISOTROPIC_VOLUME = DATA_DIR / "isotropic_volume.nii.gz"
VALIDATION_REPORT = DATA_DIR / "reports" / "validation_report.json"

@router.get("/current")
def get_current_study():
    return {
        "study_id": "demo-study",
        "modality": "CT",
        "status": "completed",
        "outputs": {
            "volume": ISOTROPIC_VOLUME.exists(),
            "left_kidney_mesh": LEFT_MESH.exists(),
            "right_kidney_mesh": RIGHT_MESH.exists(),
            "validation_report": VALIDATION_REPORT.exists(),
        },
        "models": {
            "left_kidney": "/api/studies/models/left-kidney",
            "right_kidney": "/api/studies/models/right-kidney",
        }
    }

@router.get("/models/left-kidney")
def get_left_kidney():
    if not LEFT_MESH.exists():
        raise HTTPException(status_code=404, detail="Left kidney mesh not found")
    return FileResponse(LEFT_MESH, media_type="model/stl", filename="kidney_left_refined.stl")

@router.get("/models/right-kidney")
def get_right_kidney():
    if not RIGHT_MESH.exists():
        raise HTTPException(status_code=404, detail="Right kidney mesh not found")
    return FileResponse(RIGHT_MESH, media_type="model/stl", filename="kidney_right_refined.stl")
''',

    "frontend/src/components/KidneyViewer.jsx": '''import { Canvas } from "@react-three/fiber";
import { OrbitControls, Center, Environment } from "@react-three/drei";
import { Suspense } from "react";
import { STLLoader } from "three/examples/jsm/loaders/STLLoader";
import { useLoader } from "@react-three/fiber";

function KidneyModel({ url, color, position }) {
  const geometry = useLoader(STLLoader, url);
  return (
    <mesh geometry={geometry} position={position} scale={[1, 1, 1]}>
      <meshStandardMaterial color={color} roughness={0.65} metalness={0.05} />
    </mesh>
  );
}

export default function KidneyViewer() {
  const backend = "http://localhost:8000";
  return (
    <div style={{
      width: "100%",
      height: "550px",
      background: "#111827",
      borderRadius: "16px",
      overflow: "hidden",
    }}>
      <Canvas camera={{ position: [0, 0, 300], fov: 45 }}>
        <ambientLight intensity={1.5} />
        <directionalLight position={[100, 100, 200]} intensity={3} />
        <Suspense fallback={null}>
          <Center>
            <KidneyModel url={`${backend}/api/studies/models/left-kidney`} color="#34d399" position={[0, 0, 0]} />
            <KidneyModel url={`${backend}/api/studies/models/right-kidney`} color="#fb923c" position={[0, 0, 0]} />
          </Center>
          <Environment preset="studio" />
        </Suspense>
        <OrbitControls enableDamping dampingFactor={0.08} />
      </Canvas>
    </div>
  );
}
''',

    "frontend/src/App.jsx": '''import { useEffect, useState } from "react";
import { Activity, Box, CheckCircle2, FileImage, HeartPulse, Layers3, RefreshCw, Scan } from "lucide-react";
import KidneyViewer from "./components/KidneyViewer";

function App() {
  const [study, setStudy] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

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
        <div className="system-status">
          <span className="status-dot"></span> System Online
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
              <PipelineStep number="03" title="AI Segmentation" description="Automatic anatomical structure segmentation" completed={study.outputs.left_kidney_mesh && study.outputs.right_kidney_mesh} />
              <PipelineStep number="04" title="Mesh Generation" description="Marching Cubes reconstruction and mesh refinement" completed={study.outputs.left_kidney_mesh && study.outputs.right_kidney_mesh} />
              <PipelineStep number="05" title="Validation" description="Geometry and anatomical reconstruction validation" completed={study.outputs.validation_report} />
            </section>

            <section className="viewer-section">
              <div className="section-heading">
                <div>
                  <p className="section-label">3D ANATOMICAL MODEL</p>
                  <h3>Patient-Specific Kidney Reconstruction</h3>
                </div>
              </div>
              <KidneyViewer />
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
''',

    "frontend/src/index.css": '''* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background: #f5f7fa;
  color: #172033;
}

button {
  font-family: inherit;
}

.app {
  min-height: 100vh;
}

.topbar {
  height: 76px;
  background: white;
  border-bottom: 1px solid #e5e9ef;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 42px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 13px;
}

.brand-icon {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 11px;
  background: #172033;
  color: white;
}

.brand h1 {
  margin: 0;
  font-size: 21px;
  letter-spacing: -0.4px;
}

.brand p {
  margin: 2px 0 0;
  color: #7b8494;
  font-size: 12px;
}

.system-status {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #586273;
  font-size: 13px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #24a36a;
}

.container {
  max-width: 1250px;
  margin: auto;
  padding: 42px;
}

.hero {
  min-height: 265px;
  background: #172033;
  color: white;
  border-radius: 20px;
  padding: 42px 48px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  overflow: hidden;
}

.eyebrow,
.section-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 1.5px;
}

.eyebrow {
  color: #9ba8bc;
}

.hero h2 {
  margin: 13px 0;
  font-size: 43px;
  line-height: 1.08;
  letter-spacing: -1.5px;
}

.hero-text {
  max-width: 600px;
  color: #aeb8c8;
  line-height: 1.6;
  font-size: 15px;
}

.hero-icon {
  width: 180px;
  height: 180px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #3c4658;
  border-radius: 50%;
  color: #aeb8c8;
}

.study-header {
  margin-top: 38px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.section-label {
  color: #8a94a4;
  margin-bottom: 7px;
}

.study-header h3,
.section-heading h3 {
  margin: 0;
  font-size: 24px;
}

.completed {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 8px 13px;
  background: #e9f7f0;
  color: #18794e;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
}

.cards {
  margin-top: 22px;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 17px;
}

.card {
  background: white;
  border: 1px solid #e4e8ee;
  border-radius: 13px;
  padding: 22px;
  min-height: 160px;
}

.card-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f3f7;
  border-radius: 8px;
  color: #3c485b;
}

.card-icon svg {
  width: 19px;
}

.card-title {
  margin: 17px 0 5px;
  color: #7c8696;
  font-size: 12px;
  font-weight: 600;
}

.card h4 {
  margin: 0;
  font-size: 19px;
}

.card-description {
  margin: 5px 0 0;
  color: #929aa8;
  font-size: 12px;
}

.missing {
  color: #b34b4b;
}

.pipeline {
  margin-top: 38px;
  background: white;
  border: 1px solid #e4e8ee;
  border-radius: 15px;
  padding: 28px;
}

.section-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.section-heading button {
  display: flex;
  align-items: center;
  gap: 7px;
  border: 1px solid #dce1e8;
  background: white;
  padding: 8px 12px;
  border-radius: 7px;
  cursor: pointer;
  color: #4e5869;
}

.pipeline-step {
  min-height: 75px;
  border-top: 1px solid #edf0f4;
  display: flex;
  align-items: center;
  gap: 18px;
}

.step-number {
  color: #a0a8b5;
  font-size: 12px;
  font-weight: 700;
  width: 30px;
}

.step-content {
  flex: 1;
}

.step-content h4 {
  margin: 0 0 4px;
  font-size: 14px;
}

.step-content p {
  margin: 0;
  color: #8b94a2;
  font-size: 12px;
}

.step-status {
  color: #9aa2ae;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.step-status.done {
  color: #18794e;
  font-weight: 600;
}

.viewer-section {
  margin-top: 38px;
  background: white;
  border: 1px solid #e4e8ee;
  border-radius: 15px;
  padding: 28px;
}

.viewer-section .section-heading {
  margin-bottom: 22px;
}

.message {
  margin-top: 25px;
  background: white;
  border: 1px solid #e4e8ee;
  border-radius: 10px;
  padding: 18px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.message.error {
  color: #b34b4b;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
'''
}

for rel_path, content in FILES.items():
    p = Path(rel_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"Created: {p.resolve()}")

print("\nDashboard & Three.js 3D Viewer files successfully generated!")