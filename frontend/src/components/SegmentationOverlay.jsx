import { useEffect, useRef, useState } from "react";
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