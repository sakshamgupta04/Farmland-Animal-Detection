import json
from pathlib import Path

nb_path = Path("notebooks/01_farmland_animal_detection.ipynb")
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

# Markdown cell explaining image testing
md_cell = {
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "## 8. 📸 Test on Any Custom Image File (JPG / PNG)\n",
        "Use this function to run the complete pipeline on any single image from your disk or phone:\n",
        "1. Enter the path to your image (e.g., `'my_farm.jpg'` or `'test_image.jpg'`).\n",
        "2. Adjust `conf_threshold` (e.g. `0.25` for distant/obscured animals, `0.40` for strict).\n",
        "3. Optionally pass a custom polygon if you have defined crop zones.\n",
        "4. Displays the complete visual bounding box HUD + prints the structured parametric JSON.\n"
    ]
}

# Code cell with the runner function and execution
code_cell = {
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "def test_single_image(\n",
        "    image_path: str,\n",
        "    conf_threshold: float = 0.30,\n",
        "    iou_threshold: float = 0.45,\n",
        "    protected_polygon: np.ndarray | None = None\n",
        ") -> tuple[list[dict], dict]:\n",
        "    \"\"\"\n",
        "    Loads a local image, runs the farmland parametric analysis,\n",
        "    detects all animals/people/vehicles, and renders the dual-pane HUD.\n",
        "    \"\"\"\n",
        "    if not Path(image_path).exists():\n",
        "        print(f\"❌ Error: Image file not found at: '{image_path}'\")\n",
        "        print(\"💡 Tip: Put your image in the 'notebooks/' folder and pass its filename.\")\n",
        "        return [], {}\n",
        "        \n",
        "    # Load image with OpenCV\n",
        "    img = cv2.imread(image_path)\n",
        "    if img is None:\n",
        "        print(f\"❌ Error: Could not decode image '{image_path}'. Ensure it is a valid JPG/PNG.\")\n",
        "        return [], {}\n",
        "        \n",
        "    print(f\"Analyzing '{image_path}' ({img.shape[1]}x{img.shape[0]} px)...\")\n",
        "    \n",
        "    # Run detection & parametric analysis\n",
        "    detections, scene_params = run_parametric_detection(\n",
        "        model=model,\n",
        "        image_bgr=img,\n",
        "        conf_threshold=conf_threshold,\n",
        "        iou_threshold=iou_threshold,\n",
        "        protected_polygon=protected_polygon\n",
        "    )\n",
        "    \n",
        "    # Render complete HUD\n",
        "    render_farmland_detections(img, detections, scene_params, protected_polygon=protected_polygon)\n",
        "    \n",
        "    return detections, scene_params\n",
        "\n",
        "# ------------------------------------------------------------------\n",
        "# RUN ON A REAL TEST IMAGE:\n",
        "# (Replace 'test_image.jpg' with the path to your own farmland/animal photo)\n",
        "# ------------------------------------------------------------------\n",
        "detections, params = test_single_image(\n",
        "    image_path=\"test_image.jpg\",  # Downloaded sample test image\n",
        "    conf_threshold=0.30\n",
        ")\n"
    ]
}

nb["cells"].append(md_cell)
nb["cells"].append(code_cell)

with open(nb_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=2)

print("Updated notebook with Image testing cells!")

