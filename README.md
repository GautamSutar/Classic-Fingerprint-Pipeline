
# 🧩 Fingerprint Feature Extraction Pipeline

## 📖 Overview

This project implements a **classic fingerprint recognition pipeline** using a series of image processing techniques.

The main objective is to process a raw fingerprint image and extract its **unique features** (*minutiae points, orientation field, ridge frequency, etc.*) for use in **matching and identification**.

The pipeline is modular, with each step in its own script, while **`fingerprint_engine.py`** orchestrates the full workflow.

---

## 📊 Current Status

✅ Implemented up to **Ridge Frequency Estimation**.
The pipeline can currently:

* Load a fingerprint
* Isolate it from the background
* Normalize intensity
* Estimate ridge **orientation map**
* Estimate ridge **frequency map**

---

## 📂 Project Structure

```bash
.
├── images/                 # Input fingerprint images
├── fingerprint_engine.py   # Main pipeline controller
├── segmentation.py         # Extracts fingerprint ROI
├── normalization.py        # Normalizes intensity & contrast
├── orientation.py          # Estimates ridge orientation
└── frequency.py            # Estimates ridge frequency
```

---

## 📑 File Descriptions

* **`fingerprint_engine.py`** → Central controller. Loads the image, calls each stage, and handles visualization.
* **`segmentation.py`** → Separates fingerprint (foreground) from noisy background.
* **`normalization.py`** → Normalizes image intensity for consistent brightness & contrast.
* **`orientation.py`** → Calculates local ridge orientation (orientation map).
* **`frequency.py`** → Estimates local ridge spacing (frequency map).

---

## ⚙️ Current Workflow

The pipeline runs the following steps in order:

1. **Image Loading** → Load grayscale fingerprint image.
2. **Segmentation** → Create mask for fingerprint area.
3. **Normalization** → Standardize intensity and contrast.
4. **Orientation Estimation** → Compute ridge orientation map.
5. **Ridge Frequency Estimation** → Compute ridge frequency map.

📌 *Each step pauses with a visualization window — close it to continue.*

---

## 🚀 How to Run

### 1️⃣ Place Images

Put `.tif`, `.png`, or `.jpg` fingerprint images in the `images/` directory.

### 2️⃣ Install Dependencies

```bash
pip install opencv-python numpy scikit-image scipy matplotlib
```

### 3️⃣ Update Engine

Edit `fingerprint_engine.py` and set your image path:

```python
# In fingerprint_engine.py
if __name__ == '__main__':
    image_path = 'images/sample_fingerprint.tif'
    preprocess_and_extract(image_path)
```

### 4️⃣ Run the Script

```bash
python fingerprint_engine.py
```

---

## 🔮 Future Work (Next Modules)

* **Image Enhancement (`gabor_filter.py`)** → Apply Gabor filters to enhance ridges.
* **Binarization (`color_threshold.py`)** → Convert enhanced image to black & white.
* **Skeletonization (`skeletonize.py`)** → Thin ridges to single-pixel width.
* **Feature Extraction**:

  * **`crossing_number.py`** → Detect minutiae points (ridge endings, bifurcations).
  * **`poincare.py`** → Detect singular points (cores & deltas).
* **Template Matching** → Compare extracted features for recognition.

