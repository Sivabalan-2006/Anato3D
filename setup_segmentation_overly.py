from pathlib import Path

FILES = {
    "backend/app/api/studies.py": '''import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse

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
LEFT_MASK = DATA_DIR / "segmentations" / "kidney_left.nii.gz"
RIGHT_MASK = DATA_DIR / "segmentations" / "kidney_right.nii.gz"

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
            "left_kidney_segmentation": LEFT_MASK.exists(),
            "right_kidney_segmentation": RIGHT_MASK.exists(),
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

@router.get("/report")
def get_report():
    if not VALIDATION_REPORT.exists():
        raise HTTPException(status_code=404, detail="Validation report not found")
    with open(VALIDATION_REPORT, "r", encoding="utf-8") as f:
        data = json.load(f)
    return JSONResponse(content=data)

@router.get("/segmentations/left-kidney")
def get_left_kidney_mask():
    if not LEFT_MASK.exists():
        raise HTTPException(status_code=404, detail="Left kidney segmentation not found")
    return FileResponse(LEFT_MASK, media_type="application/gzip", filename="kidney_left.nii.gz")

@router.get("/segmentations/right-kidney")
def get_right_kidney_mask():
    if not RIGHT_MASK.exists():
        raise HTTPException(status_code=404, detail="Right kidney segmentation not found")
    return FileResponse(RIGHT_MASK, media_type="application/gzip", filename="kidney_right.nii.gz")
''',

    "frontend/src/components/SegmentationOverlay.jsx": '''import { useEffect, useRef, useState } from "react";
import * as nifti from "nifti-reader-js";

function getTypedArray(header, image) {
  switch (header.datatypeCode) {
    case nifti.NIFTI1.TYPE_INT16:
      return new Int16Array(image);
    case nifti.NIFTI1.TYPE_FLOAT32:
      return new Float32Array(image);
    case nifti.NIFTI1.TYPE_UINT16:
      return new Uint16Array(image);
    case nifti.NIFTI1.TYPE_INT32:
      return new Int32Array(image);
    case nifti.NIFTI1.TYPE_UINT8:
      return new Uint8Array(image);
    case nifti.NIFTI1.TYPE_INT8:
      return new Int8Array(image);
    default:
      return new Int16Array(image);
  }
}

async function loadNifti(url) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to load ${url}`);
  }
  const arrayBuffer = await response.arrayBuffer();
  let data = arrayBuffer;
  if (nifti.isCompressed(data)) {
    data = nifti.decompress(data);
  }
  if (!nifti.isNIFTI(data)) {
    throw new Error("Invalid NIfTI file");
  }
  const header = nifti.readHeader(data);
  const image = nifti.readImage(header, data);
  return {
    header,
    image,
    width: header.dims[1],
    height: header.dims[2],
    depth: header.dims[3],
  };
}

export default function SegmentationOverlay() {
  const canvasRef = useRef(null);
  const [ct, setCt] = useState(null);
  const [leftMask, setLeftMask] = useState(null);
  const [rightMask, setRightMask] = useState(null);
  const [slice, setSlice] = useState(214);
  const [showLeft, setShowLeft] = useState(true);
  const [showRight, setShowRight] = useState(true);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      setLoading(true);
      const [ctData, leftData, rightData] = await Promise.all([
        loadNifti("http://localhost:8000/api/studies/volume"),
        loadNifti("http://localhost:8000/api/studies/segmentations/left-kidney"),
        loadNifti("http://localhost:8000/api/studies/segmentations/right-kidney"),
      ]);
      setCt(ctData);
      setLeftMask(leftData);
      setRightMask(rightData);
      setSlice(Math.floor(ctData.depth / 2));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (!ct || !leftMask || !rightMask || !canvasRef.current) {
      return;
    }
    renderOverlay();
  }, [ct, leftMask, rightMask, slice, showLeft, showRight]);

  function renderOverlay() {
    const canvas = canvasRef.current;
    const width = ct.width;
    const height = ct.height;
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext("2d");
    const imageData = ctx.createImageData(width, height);

    const ctArray = getTypedArray(ct.header, ct.image);
    const leftArray = getTypedArray(leftMask.header, leftMask.image);
    const rightArray = getTypedArray(rightMask.header, rightMask.image);

    const slope = ct.header.scl_slope !== 0 ? ct.header.scl_slope : 1;
    const intercept = Number.isFinite(ct.header.scl_inter) ? ct.header.scl_inter : 0;

    const windowCenter = 40;
    const windowWidth = 400;
    const min = windowCenter - windowWidth / 2;
    const max = windowCenter + windowWidth / 2;

    const sliceOffset = slice * width * height;

    for (let y = 0; y < height; y++) {
      const sourceY = height - 1 - y;
      for (let x = 0; x < width; x++) {
        const voxelIndex = sliceOffset + sourceY * width + x;
        const canvasIndex = (y * width + x) * 4;

        const raw = ctArray[voxelIndex] || 0;
        const hu = raw * slope + intercept;

        let gray = ((hu - min) / (max - min)) * 255;
        gray = Math.max(0, Math.min(255, gray));

        let red = gray;
        let green = gray;
        let blue = gray;

        const left = leftArray[voxelIndex] > 0;
        const right = rightArray[voxelIndex] > 0;

        if (showLeft && left) {
          red = 220;
          green = 70;
          blue = 90;
        }
        if (showRight && right) {
          red = 70;
          green = 150;
          blue = 240;
        }

        imageData.data[canvasIndex] = red;
        imageData.data[canvasIndex + 1] = green;
        imageData.data[canvasIndex + 2] = blue;
        imageData.data[canvasIndex + 3] = 255;
      }
    }
    ctx.putImageData(imageData, 0, 0);
  }

  if (loading) {
    return <div className="ct-placeholder">Loading CT and kidney segmentation...</div>;
  }

  if (error) {
    return <div className="ct-placeholder error">{error}</div>;
  }

  return (
    <div className="overlay-viewer">
      <div className="overlay-header">
        <div>
          <p className="section-label">AI SEGMENTATION</p>
          <h3>Kidney Segmentation Overlay</h3>
        </div>
        <span>
          Axial Slice {slice + 1} / {ct.depth}
        </span>
      </div>
      <div className="overlay-content">
        <div className="overlay-canvas">
          <canvas ref={canvasRef} />
        </div>
        <div className="overlay-controls">
          <label>
            <input
              type="checkbox"
              checked={showLeft}
              onChange={(e) => setShowLeft(e.target.checked)}
            />
            <span className="legend left">Left Kidney</span>
          </label>
          <label>
            <input
              type="checkbox"
              checked={showRight}
              onChange={(e) => setShowRight(e.target.checked)}
            />
            <span className="legend right">Right Kidney</span>
          </label>
          <div className="overlay-slider">
            <span>Slice</span>
            <input
              type="range"
              min="0"
              max={ct.depth - 1}
              value={slice}
              onChange={(e) => setSlice(Number(e.target.value))}
            />
            <span>{slice + 1}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
''',

    "frontend/src/App.jsx": '''import { useEffect, useState } from "react";
import { Activity, Box, CheckCircle2, FileImage, HeartPulse, Layers3, RefreshCw, Scan } from "lucide-react";
import KidneyViewer from "./components/KidneyViewer";
import CTViewer from "./components/CTViewer";
import ReportPanel from "./components/ReportPanel";
import SegmentationOverlay from "./components/SegmentationOverlay";

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
                  <p className="section-label">ANATOMICAL METRICS</p>
                  <h3>Quantitative Validation Report</h3>
                </div>
              </div>
              <ReportPanel />
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

css_file = Path("frontend/src/index.css")
overlay_css = '''

/* OVERLAY VIEWER STYLES */
.overlay-viewer {
  margin-top: 20px;
  background: #111827;
  border-radius: 16px;
  padding: 22px;
  color: white;
}

.overlay-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.overlay-header h3 {
  margin: 0;
  font-size: 20px;
}

.overlay-header > span {
  color: #9ca3af;
  font-size: 13px;
}

.overlay-content {
  display: grid;
  grid-template-columns: 1fr 230px;
  gap: 20px;
}

.overlay-canvas {
  background: #000;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.overlay-canvas canvas {
  max-width: 100%;
  max-height: 650px;
  width: auto;
  height: auto;
  image-rendering: pixelated;
}

.overlay-controls {
  background: #030712;
  border: 1px solid #1f2937;
  border-radius: 10px;
  padding: 18px;
  align-self: start;
}

.overlay-controls label {
  display: flex;
  align-items: center;
  gap: 9px;
  margin-bottom: 16px;
  font-size: 13px;
}

.legend {
  font-weight: 600;
}

.legend.left {
  color: #dc465a;
}

.legend.right {
  color: #4696f0;
}

.overlay-slider {
  border-top: 1px solid #1f2937;
  padding-top: 18px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  color: #9ca3af;
  font-size: 12px;
}

.overlay-slider input {
  width: 100%;
}

@media (max-width: 800px) {
  .overlay-content {
    grid-template-columns: 1fr;
  }
}
'''

for rel_path, content in FILES.items():
    p = Path(rel_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"Updated: {p.resolve()}")

if css_file.exists():
    existing_css = css_file.read_text(encoding="utf-8")
    if ".overlay-viewer" not in existing_css:
        css_file.write_text(existing_css + overlay_css, encoding="utf-8")
        print(f"Appended Overlay CSS to: {css_file.resolve()}")
