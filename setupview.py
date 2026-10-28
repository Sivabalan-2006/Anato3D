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

@router.get("/volume")
def get_volume():
    if not ISOTROPIC_VOLUME.exists():
        raise HTTPException(status_code=404, detail="Isotropic CT volume not found")
    return FileResponse(ISOTROPIC_VOLUME, media_type="application/gzip", filename="isotropic_volume.nii.gz")
''',

    "frontend/src/components/CTViewer.jsx": '''import { useEffect, useState, useRef } from "react";
import * as nifti from "nifti-reader-js";

export default function CTViewer() {
  const [volume, setVolume] = useState(null);
  const [slice, setSlice] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const canvasRef = useRef(null);

  useEffect(() => {
    loadVolume();
  }, []);

  async function loadVolume() {
    try {
      setLoading(true);
      const response = await fetch("http://localhost:8000/api/studies/volume");
      if (!response.ok) {
        throw new Error("Unable to load CT volume");
      }
      const arrayBuffer = await response.arrayBuffer();
      let data = arrayBuffer;
      if (nifti.isCompressed(data)) {
        data = nifti.decompress(data);
      }
      if (!nifti.isNIFTI(data)) {
        throw new Error("Invalid NIfTI volume");
      }
      const header = nifti.readHeader(data);
      const image = nifti.readImage(header, data);

      const width = header.dims[1];
      const height = header.dims[2];
      const depth = header.dims[3];

      setVolume({
        header,
        image,
        width,
        height,
        depth,
      });
      setSlice(Math.floor(depth / 2));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (!volume || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    const { image, width, height, header } = volume;

    const typedArray = nifti.Utils.toTypedArray(header, image);
    const imageData = ctx.createImageData(width, height);

    const windowCenter = 40;
    const windowWidth = 400;
    const min = windowCenter - windowWidth / 2;
    const max = windowCenter + windowWidth / 2;

    const sliceOffset = slice * width * height;

    for (let i = 0; i < width * height; i++) {
      const voxel = typedArray[sliceOffset + i];
      let value = ((voxel - min) / (max - min)) * 255;
      value = Math.max(0, Math.min(255, value));

      imageData.data[i * 4] = value;
      imageData.data[i * 4 + 1] = value;
      imageData.data[i * 4 + 2] = value;
      imageData.data[i * 4 + 3] = 255;
    }

    canvas.width = width;
    canvas.height = height;
    ctx.putImageData(imageData, 0, 0);
  }, [volume, slice]);

  if (loading) {
    return <div className="ct-placeholder">Loading CT volume...</div>;
  }

  if (error) {
    return <div className="ct-placeholder error">{error}</div>;
  }

  return (
    <div className="ct-viewer">
      <div className="ct-header">
        <div>
          <p className="section-label">CT VOLUME</p>
          <h3>Axial Slice</h3>
        </div>
        <span>Slice {slice + 1} / {volume.depth}</span>
      </div>
      <div className="ct-image-container">
        <canvas ref={canvasRef} />
      </div>
      <div className="slice-control">
        <input
          type="range"
          min="0"
          max={volume.depth - 1}
          value={slice}
          onChange={(e) => setSlice(Number(e.target.value))}
        />
        <span>{slice + 1}</span>
      </div>
    </div>
  );
}
''',

    "frontend/src/App.jsx": '''import { useEffect, useState } from "react";
import { Activity, Box, CheckCircle2, FileImage, HeartPulse, Layers3, RefreshCw, Scan } from "lucide-react";
import KidneyViewer from "./components/KidneyViewer";
import CTViewer from "./components/CTViewer";

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
                  <p className="section-label">MEDICAL IMAGE</p>
                  <h3>Reconstructed CT Volume</h3>
                </div>
              </div>
              <CTViewer />
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
'''
}

# Append CSS for CT Viewer
index_css_path = Path("frontend/src/index.css")
ct_css_content = '''

/* CT VIEWER STYLES */
.ct-viewer {
  margin-top: 20px;
  background: #111827;
  border-radius: 16px;
  padding: 20px;
  color: white;
}

.ct-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}

.ct-header h3 {
  margin: 0;
  font-size: 20px;
}

.ct-header span {
  color: #9ca3af;
  font-size: 13px;
}

.ct-image-container {
  display: flex;
  justify-content: center;
  align-items: center;
  background: #000;
  border-radius: 10px;
  overflow: hidden;
}

.ct-image-container canvas {
  max-width: 100%;
  max-height: 520px;
  width: auto;
  height: auto;
  image-rendering: pixelated;
}

.slice-control {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-top: 18px;
}

.slice-control input {
  flex: 1;
}

.slice-control span {
  min-width: 45px;
  text-align: right;
  color: #d1d5db;
}

.ct-placeholder {
  height: 500px;
  background: #111827;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #9ca3af;
}

.ct-placeholder.error {
  color: #f87171;
}
'''

for rel_path, content in FILES.items():
    p = Path(rel_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"Updated/Created: {p.resolve()}")

if index_css_path.exists():
    existing_css = index_css_path.read_text(encoding="utf-8")
    if ".ct-viewer" not in existing_css:
        index_css_path.write_text(existing_css + ct_css_content, encoding="utf-8")
        print(f"Updated CSS: {index_css_path.resolve()}")

print("\nCT Viewer integration complete!")