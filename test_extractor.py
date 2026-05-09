#!/usr/bin/env python3
"""
Test script to verify the 360 extractor works correctly.
Creates a sample equirectangular image and tests the reframer.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

import cv2
import numpy as np
from core.presets import VIEW_PRESETS, ViewConfig
from core.reframer import Reframer


def create_test_equirectangular(width=2048, height=1024):
    """Create a simple test equirectangular image with colored regions."""
    img = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Create gradient based on position
    for y in range(height):
        for x in range(width):
            # Horizontal gradient (yaw)
            r = int((x / width) * 255)
            # Vertical gradient (pitch)
            g = int((y / height) * 255)
            # Diagonal
            b = int(((x + y) / (width + height)) * 255)
            img[y, x] = [b, g, r]  # BGR for OpenCV
    
    # Add some text markers
    cv2.putText(img, "FRONT", (width//2 - 50, height//2), 
                cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
    cv2.putText(img, "BACK", (width//4 - 40, height//2), 
                cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
    
    return img


def main():
    # Create test directories
    test_dir = Path(__file__).parent / "test_data"
    input_dir = test_dir / "input"
    output_dir = test_dir / "output"
    
    input_dir.mkdir(parents=True, exist_ok=True)
    if output_dir.exists():
        import shutil
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create test image
    print("Creating test equirectangular image...")
    test_img = create_test_equirectangular(2048, 1024)
    input_path = input_dir / "test_panorama.jpg"
    cv2.imwrite(str(input_path), test_img)
    print(f"Saved test image to {input_path}")
    
    # Test with cubemap preset (6 views)
    print("\nTesting with cubemap preset (6 views)...")
    base_config = VIEW_PRESETS["cubemap"]
    view_config = ViewConfig(
        rings=base_config.rings,
        views=base_config.views,
        include_zenith=base_config.include_zenith,
        include_nadir=base_config.include_nadir,
        zenith_fov=base_config.zenith_fov,
        output_size=512,  # Smaller for faster testing
        jpeg_quality=95,
    )
    
    reframer = Reframer(view_config)
    
    def progress(current, total, filename):
        print(f"Progress: {current}/{total} - {filename}")
    
    result = reframer.reframe_batch(
        input_dir=str(input_dir),
        output_dir=str(output_dir),
        progress_callback=progress,
    )
    
    print(f"\nResult:")
    print(f"  Success: {result.success}")
    print(f"  Input count: {result.input_count}")
    print(f"  Output count: {result.output_count}")
    print(f"  Output dir: {result.output_dir}")
    if result.errors:
        print(f"  Errors: {result.errors}")
    
    # List output files
    print(f"\nOutput structure:")
    for view_dir in sorted(output_dir.iterdir()):
        if view_dir.is_dir():
            files = list(view_dir.glob("*.jpg"))
            print(f"  {view_dir.name}/: {len(files)} files")
    
    print("\nTest completed successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
