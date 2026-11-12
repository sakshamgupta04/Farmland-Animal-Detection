import json
from pathlib import Path

def make_notebook():
    cells = []

    def md(source):
        cells.append({
            "cell_type": "markdown",
            "metadata": {},
            "source": [line + "\n" for line in source.strip().split("\n")]
        })

    def code(source):
        cells.append({
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [line + "\n" for line in source.strip().split("\n")]
        })

    # Header
    md("""
# 🌾 FarmGuard — Model 1: Farmland & Field Intrusion Detection Benchmark
### Interactive Parameterized Detection Notebook (YOLO + Scene Quality + Geometric Field Analysis)

This notebook executes **Model 1**:
1. **Scene Parametrics**: Scene brightness, contrast, green vegetation index (ExG / VARI) to evaluate if the scene qualifies as farmland/vegetation field.
2. **Object Detection**: Fast bounding box inference (using YOLOv8-nano) detecting animals, people, and farm machinery/vehicles.
3. **Parametric Analytics**:
   - Bounding box metrics (normalized coordinates, absolute pixel dimensions, bbox area % of field).
   - Distance/proximity estimation based on bounding box relative size.
   - Intrusion angle and position quadrant within the field.
   - Cropland / Protected zone intrusion check (Point-in-Polygon).
4. **Interactive Parameter Controls**: Thresholds for confidence, IoU (NMS), zone definitions, and animal filter.
5. **Direct Integration with FarmGuard's 27-Species Taxonomy & Threat Database**.
    """)

    # Setup cell
    md("## 1. Setup & Environment Initialization")
    code("""
import os
import sys
from pathlib import Path

# Configure paths and suppress noisy cache warnings
os.environ["YOLO_CONFIG_DIR"] = str(Path("./.cache/ultralytics").resolve())
os.environ["MPLCONFIGDIR"] = str(Path("./.cache/matplotlib").resolve())
Path("./.cache/ultralytics").mkdir(parents=True, exist_ok=True)
Path("./.cache/matplotlib").mkdir(parents=True, exist_ok=True)

# Add edge package to Python path so taxonomy and threat_db are directly accessible
edge_src = Path("../edge/src").resolve()
if not edge_src.exists():
    edge_src = Path("./edge/src").resolve()
if str(edge_src) not in sys.path:
    sys.path.insert(0, str(edge_src))

import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from ultralytics import YOLO

# Import FarmGuard core taxonomy & threat database
from farmguard.taxonomy import SpeciesRegistry, ThreatLevel
from farmguard.threat_db import ThreatDatabase

registry = SpeciesRegistry()
threat_db = ThreatDatabase(registry)
print(f"✓ FarmGuard Taxonomy loaded: {len(registry.list_all())} registered classes")
print(f"✓ PyTorch & Ultralytics ready.")
    """)

    # Section 2: Farm scene parameter analysis
    md("""
## 2. Farmland Scene Parametric Analysis (Scene Quality & Vegetation Index)
Before running object detection, evaluate whether the scene displays farmland characteristics:
- **ExG (Excess Green Index)**: $2G - R - B$
- **VARI (Visible Atmospherically Resistant Index)**: $(G - R) / (G + R - B)$
- **Illumination & Contrast**: Checks for night mode, severe fog, or underexposure.
    """)
    code("""
def analyze_farmland_scene(image_bgr: np.ndarray) -> dict:
    \"\"\"
    Calculate photometric and botanical indices on the input frame
    to quantify farmland visual parameters.
    \"\"\"
    h, w, _ = image_bgr.shape
    img_float = image_bgr.astype(np.float32) / 255.0
    b, g, r = img_float[:, :, 0], img_float[:, :, 1], img_float[:, :, 2]
    
    # Excess Green Index (ExG): Highlights green foliage/crop cover
    exg = 2.0 * g - r - b
    exg_mean = float(np.mean(exg))
    
    # VARI (Visible Atmospherically Resistant Index): crop canopy vigor
    denom = g + r - b
    denom[denom == 0] = 1e-6
    vari = (g - r) / denom
    vari_mean = float(np.clip(np.mean(vari), -1.0, 1.0))
    
    # Lighting & Photometrics
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    brightness = float(np.mean(gray))
    contrast = float(np.std(gray))
    
    # Heuristic farmland classification score (0.0 to 1.0)
    # Farms typically have moderate-to-high vegetation index and open-air contrast
    green_ratio = float(np.sum(exg > 0.05) / (h * w))
    is_daylight = brightness > 35.0
    is_farmland = green_ratio > 0.15 or exg_mean > 0.02
    
    return {
        "dimensions": (w, h),
        "mean_brightness": round(brightness, 2),
        "contrast_std": round(contrast, 2),
        "excess_green_index": round(exg_mean, 4),
        "vari_index": round(vari_mean, 4),
        "green_coverage_ratio": round(green_ratio, 4),
        "is_daylight": is_daylight,
        "is_farmland_candidate": is_farmland,
        "scene_label": "Active Farmland / Vegetation" if is_farmland else "Non-farmland / Sparse Field"
    }
    """)

    # Section 3: Detection & Parametric Extraction Engine
    md("""
## 3. Parametric Object Detection & Tracking Engine
The detection function applies YOLO, filters for relevant farm objects (animals, persons, vehicles), and computes key physical parameters:
- **Normalized & Absolute Coordinates**: $[x_1, y_1, x_2, y_2, w, h]$
- **Aspect Ratio & Field Coverage**: $\% \text{ Area} = \frac{W_{box} \times H_{box}}{W_{img} \times H_{img}} \times 100$
- **Ground Touch Point (Bottom-Center)**: Essential for accurate Polygon-in-Field tests without perspective distortion.
- **Estimated Proximity Tier**: (Close: $>8\\%$ area, Medium: $2-8\\%$, Distant: $<2\\%$)
- **Intrusion Quadrant**: Top-Left, Top-Right, Bottom-Left, Bottom-Right.
    """)
    code("""
# COCO Animal class IDs mapped to common farm-intrusion categories
COCO_ANIMAL_MAP = {
    14: "bird",
    15: "cat",
    16: "dog",
    17: "horse",
    18: "sheep",
    19: "cow",
    20: "elephant",
    21: "bear",
    22: "zebra",
    23: "giraffe"
}
COCO_HUMAN_ID = 0      # person
COCO_VEHICLE_IDS = [1, 2, 3, 4, 6, 7]  # bicycle, car, motorcycle, bus, train, truck

def run_parametric_detection(
    model: YOLO,
    image_bgr: np.ndarray,
    conf_threshold: float = 0.35,
    iou_threshold: float = 0.45,
    protected_polygon: np.ndarray | None = None
) -> tuple[list[dict], dict]:
    \"\"\"
    Runs detection and computes geometric and behavioral parameters.
    \"\"\"
    h, w, _ = image_bgr.shape
    scene_params = analyze_farmland_scene(image_bgr)
    
    # Run YOLO inference
    results = model.predict(
        source=image_bgr,
        conf=conf_threshold,
        iou=iou_threshold,
        verbose=False
    )
    
    detections = []
    
    for r in results:
        boxes = r.boxes
        if boxes is None:
            continue
            
        for i in range(len(boxes)):
            cls_id = int(boxes.cls[i].item())
            conf = float(boxes.conf[i].item())
            xyxy = boxes.xyxy[i].cpu().numpy().tolist()
            x1, y1, x2, y2 = xyxy
            
            # Categorize detected target
            category = "other"
            if cls_id == COCO_HUMAN_ID:
                category = "person"
                label = "Person"
            elif cls_id in COCO_ANIMAL_MAP:
                category = "animal"
                label = COCO_ANIMAL_MAP[cls_id]
            elif cls_id in COCO_VEHICLE_IDS:
                category = "vehicle"
                label = "Farm Machinery / Vehicle"
            else:
                # Include any other object with lower priority
                label = model.names[cls_id]
            
            # Parametric calculations
            box_w = x2 - x1
            box_h = y2 - y1
            area_px = box_w * box_h
            area_pct = (area_px / (w * h)) * 100.0
            aspect_ratio = box_w / max(1.0, box_h)
            
            # Bottom-center ground contact point
            bottom_center_x = (x1 + x2) / 2.0
            bottom_center_y = y2
            ground_pt = (bottom_center_x, bottom_center_y)
            
            # Spatial quadrant
            quad_x = "Left" if bottom_center_x < (w / 2) else "Right"
            quad_y = "Upper Field" if bottom_center_y < (h / 2) else "Lower Field"
            quadrant = f"{quad_y} - {quad_x}"
            
            # Distance / Proximity estimation
            if area_pct > 8.0:
                proximity = "Close Range (High Urgency)"
            elif area_pct > 2.0:
                proximity = "Mid Range (Approaching)"
            else:
                proximity = "Distant Perimeter"
                
            # Point-in-Polygon Protected Zone Check
            in_protected_zone = True
            if protected_polygon is not None and len(protected_polygon) >= 3:
                # cv2.pointPolygonTest returns >= 0 for inside/on boundary
                inside = cv2.pointPolygonTest(protected_polygon, ground_pt, measureDist=False)
                in_protected_zone = (inside >= 0)
                
            # Threat & taxonomy lookup
            # Map detection label to FarmGuard species registry
            species_match = None
            if category == "person":
                species_match = registry.get("person")
            elif category == "vehicle":
                species_match = registry.get("vehicle")
            else:
                # Fuzzy/direct match
                for sp in registry.list_all():
                    if label.lower() in sp.common_name.lower() or label.lower() in sp.species_id:
                        species_match = sp
                        break
                if not species_match:
                    species_match = registry.get("unknown_animal")
            
            threat_eval = threat_db.classify_threat(species_match.species_id, conf)
            
            det_record = {
                "id": i + 1,
                "label": label,
                "category": category,
                "confidence": round(conf, 3),
                "bbox_xyxy": [round(v, 1) for v in [x1, y1, x2, y2]],
                "bbox_dimensions": {"width": round(box_w, 1), "height": round(box_h, 1)},
                "field_area_percent": round(area_pct, 2),
                "aspect_ratio": round(aspect_ratio, 2),
                "ground_touch_point": (round(bottom_center_x, 1), round(bottom_center_y, 1)),
                "field_quadrant": quadrant,
                "proximity": proximity,
                "in_protected_zone": in_protected_zone,
                "taxonomy": {
                    "common_name": species_match.common_name,
                    "scientific_name": species_match.scientific_name,
                    "hindi_name": species_match.hindi_name,
                    "family": species_match.family,
                    "is_dangerous": species_match.is_dangerous,
                    "threat_level": species_match.threat_level.name
                },
                "threat_assessment": {
                    "level": threat_eval.level.name,
                    "recommended_actions": threat_eval.recommended_actions,
                    "reasoning": threat_eval.reasoning
                }
            }
            detections.append(det_record)
            
        return detections, scene_params
    """)

    # Section 4: Synthetic & Real Test Image Generation
    md("""
## 4. Synthetic Farmland & Animal Test Frame Generator
This module generates a photo-realistic simulated farmland crop field with customizable animals, fencing, and crop rows to benchmark the detection pipeline immediately without needing external video files.
    """)
    code("""
def generate_sample_farmland_scene(add_animal: bool = True, add_person: bool = False) -> np.ndarray:
    \"\"\"
    Generates a realistic test frame of an agricultural field with crop rows,
    distant tree line, sky, and simulated targets for parameter verification.
    \"\"\"
    w, h = 960, 540
    frame = np.zeros((h, w, 3), dtype=np.uint8)
    
    # 1. Sky (graduated blue to pale cyan)
    sky_h = int(h * 0.35)
    for y in range(sky_h):
        ratio = y / sky_h
        color = [int(220 - 40 * ratio), int(180 - 20 * ratio), int(120 - 40 * ratio)]
        frame[y, :] = color
        
    # 2. Distant tree line / hills (deep green-olive)
    tree_line = sky_h + 30
    cv2.rectangle(frame, (0, sky_h), (w, tree_line), (34, 80, 45), -1)
    
    # 3. Farmland ground (crop field with perspective rows)
    ground_h = h - tree_line
    for y in range(tree_line, h):
        factor = (y - tree_line) / ground_h
        # Soil-to-crop gradient: warm earthen green (BGR)
        color = [int(25 + 40 * factor), int(75 + 85 * factor), int(35 + 20 * factor)]
        frame[y, :] = color
        
    # Draw converging crop rows (perspective lines)
    vp_x, vp_y = w // 2, sky_h
    for start_x in range(-200, w + 300, 75):
        cv2.line(frame, (vp_x, vp_y), (start_x, h), (20, 110, 35), 3, cv2.LINE_AA)
        
    # Optional: Draw animal silhouette (Wild Boar / Cattle proxy)
    if add_animal:
        # Animal body ellipse
        ax, ay = int(w * 0.58), int(h * 0.65)
        cv2.ellipse(frame, (ax, ay), (65, 38), 0, 0, 360, (28, 42, 60), -1)
        # Head
        cv2.circle(frame, (ax - 60, ay - 10), 24, (28, 42, 60), -1)
        # Snout
        cv2.ellipse(frame, (ax - 82, ay - 4), (14, 9), -15, 0, 360, (35, 50, 70), -1)
        # Legs
        cv2.line(frame, (ax - 35, ay + 30), (ax - 35, ay + 65), (25, 38, 55), 8)
        cv2.line(frame, (ax + 35, ay + 30), (ax + 35, ay + 65), (25, 38, 55), 8)
        
    if add_person:
        px, py = int(w * 0.25), int(h * 0.58)
        # Torso
        cv2.rectangle(frame, (px - 15, py - 40), (px + 15, py + 25), (140, 60, 40), -1)
        # Head
        cv2.circle(frame, (px, py - 60), 16, (160, 190, 220), -1)
        # Legs
        cv2.line(frame, (px - 8, py + 25), (px - 8, py + 80), (80, 50, 40), 7)
        cv2.line(frame, (px + 8, py + 25), (px + 8, py + 80), (80, 50, 40), 7)
        
    return frame
    """)

    # Section 5: Visualization & Parametric Reporting
    md("""
## 5. Visualizer with Parametric HUD & Threat Assessment
This renderer plots:
1. **The Farmland Scene** with color-coded Bounding Boxes (🔴 High Threat, 🟡 Medium, ⚠️ Danger, 🚫 Person Suppression).
2. **Protected Zone Polygon**: Visualizes farm perimeter/boundary.
3. **Parametric HUD Table**: Displays spatial quadrant, proximity, area %, scientific taxonomy, and threat escalation commands.
    """)
    code("""
def render_farmland_detections(
    image_bgr: np.ndarray,
    detections: list[dict],
    scene_params: dict,
    protected_polygon: np.ndarray | None = None
):
    \"\"\"
    Renders high-resolution bounding boxes, HUD telemetry, and parametric dashboard.
    \"\"\"
    vis_img = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    h, w, _ = vis_img.shape
    
    fig, (ax_main, ax_hud) = plt.subplots(1, 2, figsize=(18, 8), gridspec_kw={'width_ratios': [1.3, 1]})
    
    # 1. Main Scene Plot
    ax_main.imshow(vis_img)
    ax_main.set_title(
        f"🌾 Farmland Monitor: {scene_params['scene_label']} | ExG: {scene_params['excess_green_index']} | "
        f"Brightness: {scene_params['mean_brightness']}",
        fontsize=12, fontweight='bold', pad=10
    )
    
    # Draw Protected Zone Polygon if configured
    if protected_polygon is not None and len(protected_polygon) >= 3:
        poly_patch = patches.Polygon(
            protected_polygon,
            closed=True,
            fill=True,
            facecolor='cyan',
            alpha=0.18,
            edgecolor='cyan',
            linestyle='--',
            linewidth=2.5,
            label='Protected Crop Boundary'
        )
        ax_main.add_patch(poly_patch)
        
    # Draw Bounding Boxes and Parametric Badges
    threat_colors = {
        "HIGH": "red",
        "MEDIUM": "goldenrod",
        "LOW": "green",
        "DANGER": "purple",
        "SUPPRESS": "dodgerblue",
        "IGNORE": "gray"
    }
    
    for det in detections:
        x1, y1, x2, y2 = det["bbox_xyxy"]
        bw = x2 - x1
        bh = y2 - y1
        t_level = det["threat_assessment"]["level"]
        color = threat_colors.get(t_level, "white")
        
        # Bounding box rectangle
        rect = patches.Rectangle(
            (x1, y1), bw, bh,
            linewidth=2.5,
            edgecolor=color,
            facecolor='none'
        )
        ax_main.add_patch(rect)
        
        # Ground touch anchor point
        gx, gy = det["ground_touch_point"]
        ax_main.plot(gx, gy, marker='o', markersize=6, color=color)
        
        # Species badge label
        sc_name = det["taxonomy"]["scientific_name"]
        badge_text = f"#{det['id']} {det['taxonomy']['common_name']}\\n({sc_name})\\nConf: {det['confidence']*100:.1f}% | {det['proximity']}"
        ax_main.text(
            x1, max(15, y1 - 8),
            badge_text,
            color='white',
            fontsize=8.5,
            fontweight='bold',
            bbox=dict(facecolor=color, alpha=0.82, edgecolor='none', boxstyle='round,pad=0.3')
        )
        
    ax_main.set_xlim(0, w)
    ax_main.set_ylim(h, 0)  # Invert Y to match image coordinates
    ax_main.axis('off')
    if protected_polygon is not None:
        ax_main.legend(loc='lower left', framealpha=0.8)

    # 2. Parametric Telemetry Table (HUD)
    ax_hud.axis('off')
    hud_lines = [
        "==================================================",
        "          FARMLAND INTRUSION TELEMETRY            ",
        "==================================================",
        f"• Scene State:          {scene_params['scene_label']}",
        f"• Green Cover Index:    {scene_params['green_coverage_ratio']*100:.1f}% (ExG: {scene_params['excess_green_index']})",
        f"• Illumination/StdDev:  {scene_params['mean_brightness']} / {scene_params['contrast_std']} (Daylight: {scene_params['is_daylight']})",
        f"• Active Intrusion(s):  {len(detections)} target(s) detected",
        "--------------------------------------------------"
    ]
    
    if not detections:
        hud_lines.append("✓ Perimeter Clear: No animal or person detected.")
    else:
        for d in detections:
            hud_lines.extend([
                f"[Target #{d['id']}] {d['taxonomy']['common_name']} ({d['taxonomy']['hindi_name']})",
                f"  ├ Scientific:      {d['taxonomy']['scientific_name']} [{d['taxonomy']['family']}]",
                f"  ├ Threat Level:    {d['threat_assessment']['level']} (Dangerous: {d['taxonomy']['is_dangerous']})",
                f"  ├ Field Position:  {d['field_quadrant']} | Touch: ({d['ground_touch_point'][0]}, {d['ground_touch_point'][1]})",
                f"  ├ Crop Intrusion:  {'⚠️ INSIDE PROTECTED ZONE' if d['in_protected_zone'] else 'Outside Perimeter'}",
                f"  ├ Spatial Size:    {d['bbox_dimensions']['width']}x{d['bbox_dimensions']['height']}px ({d['field_area_percent']}% field area)",
                f"  ├ Proximity Tier:  {d['proximity']}",
                f"  └ Actions Queued:  {', '.join(d['threat_assessment']['recommended_actions'])}",
                ""
            ])
            
    ax_hud.text(
        0.02, 0.98,
        "\\n".join(hud_lines),
        transform=ax_hud.transAxes,
        fontsize=9,
        verticalalignment='top',
        fontfamily='monospace',
        bbox=dict(boxstyle='square,pad=0.8', facecolor='#15181e', edgecolor='#30363d', alpha=0.95),
        color='#58a6ff'
    )
    
    plt.tight_layout()
    plt.show()
    """)

    # Section 6: Live Execution Cell
    md("""
## 6. Run Execution & Benchmark on Test Frame
Execute inference with customizable parameters:
- `conf_threshold`: Filter detections by minimum confidence.
- `iou_threshold`: Non-Maximum Suppression overlap threshold.
- `protected_polygon`: Polygon coordinates defining the farm cropland boundary.
    """)
    code("""
# Initialize YOLOv8-nano model (downloads lightweight ~6MB weights on first run)
print("Loading YOLOv8-nano model...")
model = YOLO("yolov8n.pt")

# Define a simulated protected farmland crop field boundary polygon
test_polygon = np.array([
    [100, 220],
    [860, 220],
    [930, 520],
    [30, 520]
], dtype=np.int32)

# Generate test scene with simulated intrusion
sample_frame = generate_sample_farmland_scene(add_animal=True, add_person=False)

# Run complete parametric detection
detections, scene_params = run_parametric_detection(
    model=model,
    image_bgr=sample_frame,
    conf_threshold=0.30,
    iou_threshold=0.45,
    protected_polygon=test_polygon
)

print(f"Extracted {len(detections)} detection(s) with scene metrics: {scene_params}")

# Render complete visualization
render_farmland_detections(sample_frame, detections, scene_params, protected_polygon=test_polygon)
    """)

    # Section 7: Video File or Webcam Streaming Runner
    md("""
## 7. Run on Any Custom Video File or Live Webcam
Use this cell to run the same parametric pipeline on an MP4 video or local webcam (`0`).
    """)
    code("""
def process_video_or_webcam(
    source_path_or_idx: str | int = 0,
    max_frames: int = 150,
    skip_frames: int = 2
):
    \"\"\"
    Processes an input video or live webcam stream with parametric telemetry.
    \"\"\"
    cap = cv2.VideoCapture(source_path_or_idx)
    if not cap.isOpened():
        print(f"❌ Error: Could not open camera/video source: {source_path_or_idx}")
        return
        
    frame_idx = 0
    processed_count = 0
    print(f"Streaming from '{source_path_or_idx}' (Press Ctrl+C or stop cell to end)...")
    
    try:
        while cap.isOpened() and processed_count < max_frames:
            ret, frame = cap.read()
            if not ret:
                break
                
            frame_idx += 1
            if frame_idx % (skip_frames + 1) != 0:
                continue
                
            dets, params = run_parametric_detection(
                model=model,
                image_bgr=frame,
                conf_threshold=0.35,
                protected_polygon=test_polygon
            )
            
            processed_count += 1
            if dets:
                print(f"Frame #{frame_idx}: Detected {len(dets)} target(s) -> {[d['label'] + ' (' + d['proximity'] + ')' for d in dets]}")
                
    finally:
        cap.release()
        print(f"Finished processing {processed_count} frames.")

# Example usage (uncomment to run on a local video file):
# process_video_or_webcam("test_footage.mp4", max_frames=60)
    """)

    nb_content = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.12.0"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }

    out_path = Path("notebooks/01_farmland_animal_detection.ipynb")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(nb_content, f, indent=2)
    print(f"✓ Notebook successfully written to: {out_path.resolve()}")

if __name__ == "__main__":
    make_notebook()

