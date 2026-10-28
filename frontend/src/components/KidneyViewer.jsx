import { Suspense, useRef, useState } from "react";
import { Canvas, useLoader } from "@react-three/fiber";
import {
  OrbitControls,
  Html,
  Environment,
} from "@react-three/drei";
import { STLLoader } from "three/examples/jsm/loaders/STLLoader";
import * as THREE from "three";

const BACKEND = "http://localhost:8000";

function Kidney({
  url,
  name,
  color,
  visible,
  selected,
  onSelect,
}) {
  const geometry = useLoader(STLLoader, url);

  return (
    <mesh
      geometry={geometry}
      visible={visible}
      onClick={(event) => {
        event.stopPropagation();
        onSelect(name);
      }}
      scale={selected ? 1.03 : 1}
    >
      <meshStandardMaterial
        color={selected ? "#facc15" : color}
        roughness={0.5}
        metalness={0.05}
        side={THREE.DoubleSide}
      />

      {visible && selected && (
        <Html
          center
          distanceFactor={80}
          style={{
            pointerEvents: "none",
            color: "#111827",
            background: "#facc15",
            padding: "5px 9px",
            borderRadius: "6px",
            fontSize: "11px",
            fontWeight: "700",
            whiteSpace: "nowrap",
          }}
        >
          {name}
        </Html>
      )}
    </mesh>
  );
}

function Scene({
  showLeft,
  showRight,
  selected,
  setSelected,
  controlsRef,
}) {
  return (
    <>
      <ambientLight intensity={1.2} />

      <directionalLight
        position={[100, 100, 200]}
        intensity={2.5}
      />

      <directionalLight
        position={[-100, -50, 100]}
        intensity={1.2}
      />

      <Suspense fallback={null}>
        <Kidney
          url={`${BACKEND}/api/studies/models/left-kidney`}
          name="Left Kidney"
          color="#d96b76"
          visible={showLeft}
          selected={selected === "Left Kidney"}
          onSelect={setSelected}
        />

        <Kidney
          url={`${BACKEND}/api/studies/models/right-kidney`}
          name="Right Kidney"
          color="#4c91d9"
          visible={showRight}
          selected={selected === "Right Kidney"}
          onSelect={setSelected}
        />

        <Environment preset="studio" />
      </Suspense>

      <OrbitControls
        ref={controlsRef}
        enableDamping
        dampingFactor={0.08}
        minDistance={50}
        maxDistance={600}
      />
    </>
  );
}

function MeasurementBlock({ title, data }) {
  if (!data) return null;

  return (
    <div className="measurement-block">
      <strong>{title}</strong>

      <div className="measurement-row">
        <span>Volume</span>
        <span>
          {Number(data.volume_cm3).toFixed(2)} cm³
        </span>
      </div>

      <div className="measurement-row">
        <span>Surface area</span>
        <span>
          {Number(data.surface_area_cm2).toFixed(2)} cm²
        </span>
      </div>

      <div className="measurement-row">
        <span>Dimensions</span>
        <span>
          {Number(data.width_mm).toFixed(0)} ×{" "}
          {Number(data.depth_mm).toFixed(0)} ×{" "}
          {Number(data.height_mm).toFixed(0)} mm
        </span>
      </div>

      <div className="measurement-row">
        <span>Centroid</span>
        <span>
          {Number(data.centroid_x_mm).toFixed(1)},{" "}
          {Number(data.centroid_y_mm).toFixed(1)},{" "}
          {Number(data.centroid_z_mm).toFixed(1)} mm
        </span>
      </div>

      <div className="measurement-row">
        <span>Mesh quality</span>
        <span className="quality-ok">
          {data.watertight ? "Valid" : "Check"}
        </span>
      </div>
    </div>
  );
}

export default function KidneyViewer({ measurements }) {
  const controlsRef = useRef(null);

  const [showLeft, setShowLeft] = useState(true);
  const [showRight, setShowRight] = useState(true);
  const [selected, setSelected] = useState(null);

  function resetCamera() {
    if (!controlsRef.current) return;

    controlsRef.current.reset();
  }

  function clearSelection() {
    setSelected(null);
  }

  return (
    <div className="kidney-viewer">

      <div className="kidney-toolbar">
        <div>
          <p className="section-label">3D ANATOMY</p>
          <h3>Patient-Specific Kidney Model</h3>
        </div>

        <div className="viewer-actions">
          <button
            className="reset-button"
            onClick={resetCamera}
          >
            Reset View
          </button>

          <button
            className="reset-button"
            onClick={clearSelection}
          >
            Clear Selection
          </button>
        </div>
      </div>

      <div className="viewer-body">

        <div className="three-canvas">
          <Canvas
            camera={{
              position: [0, 0, 300],
              fov: 45,
            }}
            onPointerMissed={clearSelection}
          >
            <Scene
              showLeft={showLeft}
              showRight={showRight}
              selected={selected}
              setSelected={setSelected}
              controlsRef={controlsRef}
            />
          </Canvas>
        </div>

        <div className="model-controls">

          <p className="control-title">
            Structures
          </p>

          <label className="model-toggle">
            <input
              type="checkbox"
              checked={showLeft}
              onChange={(e) => setShowLeft(e.target.checked)}
            />

            <span className="model-color left-color"></span>

            Left Kidney
          </label>

          <label className="model-toggle">
            <input
              type="checkbox"
              checked={showRight}
              onChange={(e) => setShowRight(e.target.checked)}
            />

            <span className="model-color right-color"></span>

            Right Kidney
          </label>

          <div className="viewer-help">
            <p>Mouse controls</p>
            <span>Left drag — Rotate</span>
            <span>Scroll — Zoom</span>
            <span>Right drag — Pan</span>
            <span>Click model — Select</span>
          </div>

          {selected && (
            <div className="selected-model">
              <p>Selected structure</p>
              <strong>{selected}</strong>
            </div>
          )}

          {measurements && (
            <div className="measurement-panel">
              <p className="control-title">
                Anatomical Measurements
              </p>

              <MeasurementBlock
                title="Left Kidney"
                data={measurements.left_kidney}
              />

              <MeasurementBlock
                title="Right Kidney"
                data={measurements.right_kidney}
              />
            </div>
          )}

        </div>
      </div>
    </div>
  );
}
