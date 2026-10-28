import { useEffect, useRef, useState } from "react";
import * as nifti from "nifti-reader-js";

function getTypedArray(header, image) {
  if (header.datatypeCode === nifti.NIFTI1.TYPE_INT16) {
    return new Int16Array(image);
  }
  if (header.datatypeCode === nifti.NIFTI1.TYPE_FLOAT32) {
    return new Float32Array(image);
  }
  if (header.datatypeCode === nifti.NIFTI1.TYPE_UINT16) {
    return new Uint16Array(image);
  }
  if (header.datatypeCode === nifti.NIFTI1.TYPE_INT32) {
    return new Int32Array(image);
  }
  if (header.datatypeCode === nifti.NIFTI1.TYPE_UINT8) {
    return new Uint8Array(image);
  }
  if (header.datatypeCode === nifti.NIFTI1.TYPE_INT8) {
    return new Int8Array(image);
  }
  return new Int16Array(image);
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

export default function CTViewer() {
  const [volume, setVolume] = useState(null);
  const [axialSlice, setAxialSlice] = useState(0);
  const [coronalSlice, setCoronalSlice] = useState(0);
  const [sagittalSlice, setSagittalSlice] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const axialCanvas = useRef(null);
  const coronalCanvas = useRef(null);
  const sagittalCanvas = useRef(null);

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
      setAxialSlice(Math.floor(depth / 2));
      setCoronalSlice(Math.floor(height / 2));
      setSagittalSlice(Math.floor(width / 2));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (!volume) return;
    renderAxial();
    renderCoronal();
    renderSagittal();
  }, [volume, axialSlice, coronalSlice, sagittalSlice]);

  function getVoxel(typedArray, x, y, z) {
    const { width, height } = volume;
    return typedArray[z * width * height + y * width + x];
  }

  function convertToPixel(rawVoxel) {
    const { header } = volume;
    const slope = header.scl_slope !== 0 ? header.scl_slope : 1.0;
    const intercept = Number.isFinite(header.scl_inter) ? header.scl_inter : 0.0;
    const hu = rawVoxel * slope + intercept;
    const windowCenter = 40;
    const windowWidth = 400;
    const min = windowCenter - windowWidth / 2;
    const max = windowCenter + windowWidth / 2;
    return clamp(((hu - min) / (max - min)) * 255, 0, 255);
  }

  function renderAxial() {
    const canvas = axialCanvas.current;
    if (!canvas) return;
    const { width, height, header, image } = volume;
    const typedArray = getTypedArray(header, image);
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext("2d");
    const imageData = ctx.createImageData(width, height);

    for (let y = 0; y < height; y++) {
      const sourceY = height - 1 - y;
      for (let x = 0; x < width; x++) {
        const voxel = getVoxel(typedArray, x, sourceY, axialSlice);
        const value = convertToPixel(voxel);
        const index = (y * width + x) * 4;
        imageData.data[index] = value;
        imageData.data[index + 1] = value;
        imageData.data[index + 2] = value;
        imageData.data[index + 3] = 255;
      }
    }
    ctx.putImageData(imageData, 0, 0);
  }

  function renderCoronal() {
    const canvas = coronalCanvas.current;
    if (!canvas) return;
    const { width, depth, header, image } = volume;
    const typedArray = getTypedArray(header, image);
    canvas.width = width;
    canvas.height = depth;
    const ctx = canvas.getContext("2d");
    const imageData = ctx.createImageData(width, depth);

    for (let z = 0; z < depth; z++) {
      for (let x = 0; x < width; x++) {
        const voxel = getVoxel(typedArray, x, coronalSlice, z);
        const value = convertToPixel(voxel);
        const displayY = depth - 1 - z;
        const index = (displayY * width + x) * 4;
        imageData.data[index] = value;
        imageData.data[index + 1] = value;
        imageData.data[index + 2] = value;
        imageData.data[index + 3] = 255;
      }
    }
    ctx.putImageData(imageData, 0, 0);
  }

  function renderSagittal() {
    const canvas = sagittalCanvas.current;
    if (!canvas) return;
    const { height, depth, header, image } = volume;
    const typedArray = getTypedArray(header, image);
    canvas.width = height;
    canvas.height = depth;
    const ctx = canvas.getContext("2d");
    const imageData = ctx.createImageData(height, depth);

    for (let z = 0; z < depth; z++) {
      for (let y = 0; y < height; y++) {
        const voxel = getVoxel(typedArray, sagittalSlice, y, z);
        const value = convertToPixel(voxel);
        const displayY = depth - 1 - z;
        const index = (displayY * height + y) * 4;
        imageData.data[index] = value;
        imageData.data[index + 1] = value;
        imageData.data[index + 2] = value;
        imageData.data[index + 3] = 255;
      }
    }
    ctx.putImageData(imageData, 0, 0);
  }

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
          <h3>Multiplanar Reconstruction</h3>
        </div>
        <span>
          {volume.width} × {volume.height} × {volume.depth}
        </span>
      </div>
      <div className="ct-grid">
        <div className="ct-panel">
          <div className="ct-panel-title">
            Axial <span>{axialSlice + 1} / {volume.depth}</span>
          </div>
          <div className="ct-canvas-container">
            <canvas ref={axialCanvas} />
          </div>
          <input
            type="range"
            min="0"
            max={volume.depth - 1}
            value={axialSlice}
            onChange={(e) => setAxialSlice(Number(e.target.value))}
          />
        </div>

        <div className="ct-panel">
          <div className="ct-panel-title">
            Coronal <span>{coronalSlice + 1} / {volume.height}</span>
          </div>
          <div className="ct-canvas-container">
            <canvas ref={coronalCanvas} />
          </div>
          <input
            type="range"
            min="0"
            max={volume.height - 1}
            value={coronalSlice}
            onChange={(e) => setCoronalSlice(Number(e.target.value))}
          />
        </div>

        <div className="ct-panel">
          <div className="ct-panel-title">
            Sagittal <span>{sagittalSlice + 1} / {volume.width}</span>
          </div>
          <div className="ct-canvas-container">
            <canvas ref={sagittalCanvas} />
          </div>
          <input
            type="range"
            min="0"
            max={volume.width - 1}
            value={sagittalSlice}
            onChange={(e) => setSagittalSlice(Number(e.target.value))}
          />
        </div>
      </div>
    </div>
  );
}
