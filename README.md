# 360 Panorama Image Extractor

A standalone GUI application for extracting multiple camera angles from 360° equirectangular images.

## What It Does

Takes a folder of 360° equirectangular images (like those from Insta360 Pro, Ricoh Theta, etc.) and extracts multiple perspective views from each image using configurable camera rigs.

### Features

- **Simple GUI**: Select input/output folders with a few clicks
- **Multiple presets**: Choose from 6 to 24 views per image
  - **Cubemap** (6 views): Front, back, left, right, top, bottom
  - **Low** (10 views): Fibonacci-spiral distribution
  - **Medium** (14 views): Fibonacci-spiral distribution
  - **Default** (16 views): Two-ring layout (8 down, 8 up)
  - **High** (20 views): Fibonacci-spiral distribution
  - **Ultra** (24 views): Fibonacci-spiral distribution
- **Configurable output**: Adjust resolution (960-1920px) and JPEG quality
- **Progress tracking**: Real-time progress bar and status messages
- **Lightweight**: Only requires OpenCV and NumPy

## Installation

### Prerequisites

- Python 3.8 or higher
- pip or uv

### Setup

```bash
# Using pip
pip install opencv-python-headless numpy

# Or using uv (recommended)
uv venv .venv
.venv\Scripts\activate
uv pip install opencv-python-headless numpy
```

## Usage

### GUI Application

```bash
python extractor_app.py
```

1. **Select Input Folder**: Choose a folder containing your 360° equirectangular images (`.jpg`, `.png`)
2. **Select Output Folder**: Choose where to save the extracted views
3. **Choose Preset**: Select how many views to extract per image
4. **Adjust Settings**: Output size (960-1920px) and JPEG quality (50-100)
5. **Click "Extract Views"**: Processing begins with progress tracking

### Output Structure

```
output/
  00_00/          # View 1 (e.g., front)
    image1.jpg
    image2.jpg
  00_01/          # View 2 (e.g., right)
    image1.jpg
    image2.jpg
  00_02/          # View 3 (e.g., back)
    ...
  ...
```

Each folder corresponds to a virtual camera view with a specific yaw/pitch angle. All images from the same source panorama share the same filename across folders.

### Preset Details

| Preset | Views | Description |
|--------|-------|-------------|
| Cubemap | 6 | 4 horizon faces (0°, 90°, 180°, 270°) + top + bottom, all 90° FOV |
| Low | 10 | Fibonacci-spiral from zenith to nadir, 90° FOV |
| Medium | 14 | Fibonacci-spiral from zenith to nadir, 90° FOV |
| Default | 16 | Two-ring: 8 at -35° pitch + 8 at +35° pitch, 90° FOV |
| High | 20 | Fibonacci-spiral from zenith to nadir, 90° FOV |
| Ultra | 24 | Fibonacci-spiral from zenith to nadir, 90° FOV |

## Testing

Run the test script to verify everything works:

```bash
python test_extractor.py
```

This creates a sample equirectangular image and extracts all views from it.

## Supported Image Formats

- JPEG (`.jpg`, `.jpeg`)
- PNG (`.png`)

**Recommended**: 2:1 aspect ratio equirectangular images (e.g., 7680×3840, 4096×2048, etc.)

## Notes

- **Unicode paths**: The application handles paths with special characters (e.g., accented letters) correctly on Windows
- **Large images**: Processing 7680×3840 images may take a few seconds per image depending on your hardware
- **Memory usage**: The application precomputes remap tables for faster processing, which uses some additional memory

## Credits

Based on the Lichtfeld 360 Plugin by Alex Gee. The reprojection math is a transliteration of an equirectangular perspective planner webapp.

## License

GPL-3.0-or-later
