#!/usr/bin/env python3
"""
360 Panorama Image Extractor - Standalone GUI Application

Extracts multiple camera angles from 360° equirectangular images
and organizes them into an output directory.

Usage:
    python extractor_app.py
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from threading import Thread
import logging

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('extractor.log', mode='w'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Add the parent directory to path to import core modules
sys.path.insert(0, str(Path(__file__).parent))

# Import directly from modules to avoid heavy dependencies (pycolmap, etc.)
from core.presets import VIEW_PRESETS, ViewConfig
from core.reframer import Reframer


class ExtractorApp:
    """Simple GUI for extracting camera angles from 360° images."""

    def __init__(self, root):
        self.root = root
        self.root.title("360 Panorama Image Extractor")
        self.root.geometry("600x400")
        self.root.resizable(False, False)

        self.input_dir = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.selected_preset = tk.StringVar()
        self.output_size = tk.IntVar(value=1920)
        self.jpeg_quality = tk.IntVar(value=95)

        self._build_ui()

    def _build_ui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Input folder
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(input_frame, text="Input Folder:").pack(side=tk.LEFT)
        ttk.Entry(input_frame, textvariable=self.input_dir, state="readonly", width=40).pack(
            side=tk.LEFT, padx=(5, 5), fill=tk.X, expand=True
        )
        ttk.Button(input_frame, text="Browse...", command=self._select_input).pack(side=tk.RIGHT)

        # Output folder
        output_frame = ttk.Frame(main_frame)
        output_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(output_frame, text="Output Folder:").pack(side=tk.LEFT)
        ttk.Entry(output_frame, textvariable=self.output_dir, state="readonly", width=40).pack(
            side=tk.LEFT, padx=(5, 5), fill=tk.X, expand=True
        )
        ttk.Button(output_frame, text="Browse...", command=self._select_output).pack(side=tk.RIGHT)

        # Preset selection
        preset_frame = ttk.LabelFrame(main_frame, text="Extraction Preset", padding="10")
        preset_frame.pack(fill=tk.X, pady=(0, 10))

        preset_names = sorted(VIEW_PRESETS.keys())
        preset_display = {
            "cubemap": "Cubemap (6 views)",
            "default": "Default (16 views)",
            "high": "High (20 views)",
            "low": "Low (10 views)",
            "medium": "Medium (14 views)",
            "ultra": "Ultra (24 views)",
        }

        self.preset_combo = ttk.Combobox(
            preset_frame,
            values=[preset_display[name] for name in preset_names],
            state="readonly",
            width=30,
        )
        self.preset_combo.current(1)  # Default to "default"
        self.preset_combo.pack(side=tk.LEFT)

        self.view_count_label = ttk.Label(
            preset_frame,
            text="Views per image: 16",
        )
        self.view_count_label.pack(side=tk.LEFT, padx=(15, 0))

        self.preset_combo.bind("<<ComboboxSelected>>", self._update_view_count)
        
        # Sync initial selection
        self._update_view_count()

        # Output size
        size_frame = ttk.Frame(main_frame)
        size_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(size_frame, text="Output Size:").pack(side=tk.LEFT)
        size_combo = ttk.Combobox(
            size_frame,
            textvariable=self.output_size,
            values=[960, 1280, 1536, 1920],
            state="readonly",
            width=10,
        )
        size_combo.current(3)
        size_combo.pack(side=tk.LEFT, padx=(5, 0))

        ttk.Label(size_frame, text="px (square)").pack(side=tk.LEFT, padx=(5, 0))

        # JPEG quality
        quality_frame = ttk.Frame(main_frame)
        quality_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(quality_frame, text="JPEG Quality:").pack(side=tk.LEFT)
        quality_scale = ttk.Scale(
            quality_frame,
            from_=50,
            to=100,
            variable=self.jpeg_quality,
            orient=tk.HORIZONTAL,
            length=200,
        )
        quality_scale.pack(side=tk.LEFT, padx=(5, 5))
        ttk.Label(quality_frame, textvariable=self.jpeg_quality, width=3).pack(side=tk.LEFT)

        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode="determinate")
        self.progress.pack(fill=tk.X, pady=(0, 5))

        self.status_label = ttk.Label(main_frame, text="Ready", foreground="gray")
        self.status_label.pack(fill=tk.X)

        # Process button
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        self.process_btn = ttk.Button(
            button_frame, text="Extract Views", command=self._start_processing
        )
        self.process_btn.pack(side=tk.RIGHT)

    def _update_view_count(self, event=None):
        display_to_preset = {
            "Cubemap (6 views)": "cubemap",
            "Default (16 views)": "default",
            "High (20 views)": "high",
            "Low (10 views)": "low",
            "Medium (14 views)": "medium",
            "Ultra (24 views)": "ultra",
        }
        display_text = self.preset_combo.get()
        preset_name = display_to_preset.get(display_text, "default")
        self.selected_preset.set(preset_name)
        view_count = VIEW_PRESETS[preset_name].total_views()
        self.view_count_label.config(text=f"Views per image: {view_count}")

    def _select_input(self):
        directory = filedialog.askdirectory(title="Select Input Folder with 360° Images")
        if directory:
            self.input_dir.set(directory)

    def _select_output(self):
        directory = filedialog.askdirectory(title="Select Output Folder")
        if directory:
            self.output_dir.set(directory)

    def _start_processing(self):
        if not self.input_dir.get():
            messagebox.showerror("Error", "Please select an input folder.")
            return
        if not self.output_dir.get():
            messagebox.showerror("Error", "Please select an output folder.")
            return

        input_path = Path(self.input_dir.get())
        if not input_path.exists() or not input_path.is_dir():
            messagebox.showerror("Error", "Input folder does not exist.")
            return

        self.process_btn.config(state=tk.DISABLED)
        self.progress["value"] = 0
        self.status_label.config(text="Processing...")

        thread = Thread(target=self._process, daemon=True)
        thread.start()

    def _process(self):
        try:
            display_to_preset = {
                "Cubemap (6 views)": "cubemap",
                "Default (16 views)": "default",
                "High (20 views)": "high",
                "Low (10 views)": "low",
                "Medium (14 views)": "medium",
                "Ultra (24 views)": "ultra",
            }
            display_text = self.preset_combo.get()
            preset_name = display_to_preset.get(display_text, "default")
            logger.info(f"Using preset: {preset_name}")
            
            base_config = VIEW_PRESETS[preset_name]

            view_config = ViewConfig(
                rings=base_config.rings,
                views=base_config.views,
                include_zenith=base_config.include_zenith,
                include_nadir=base_config.include_nadir,
                zenith_fov=base_config.zenith_fov,
                output_size=self.output_size.get(),
                jpeg_quality=self.jpeg_quality.get(),
            )
            
            logger.info(f"Output size: {self.output_size.get()}, Quality: {self.jpeg_quality.get()}")

            reframer = Reframer(view_config)

            def progress_callback(current, total, filename):
                pct = (current / max(total, 1)) * 100
                self.root.after(0, self._update_progress, pct, f"Processing {current}/{total}: {filename}")

            logger.info(f"Starting reframe_batch: input={self.input_dir.get()}, output={self.output_dir.get()}")
            result = reframer.reframe_batch(
                input_dir=str(self.input_dir.get()),
                output_dir=str(self.output_dir.get()),
                progress_callback=progress_callback,
            )
            
            logger.info(f"Reframe result: success={result.success}, input_count={result.input_count}, output_count={result.output_count}")
            if result.errors:
                logger.error(f"Errors: {result.errors}")

            if result.success:
                self.root.after(
                    0,
                    self._processing_complete,
                    True,
                    f"Successfully extracted {result.output_count} views from {result.input_count} images.",
                )
            else:
                errors = "; ".join(result.errors)
                self.root.after(
                    0,
                    self._processing_complete,
                    False,
                    f"Processing completed with errors: {errors}",
                )

        except Exception as e:
            logger.exception("Exception during processing")
            self.root.after(0, self._processing_complete, False, f"Error: {str(e)}")

    def _update_progress(self, pct, message):
        self.progress["value"] = pct
        self.status_label.config(text=message)

    def _processing_complete(self, success, message):
        self.process_btn.config(state=tk.NORMAL)
        self.status_label.config(
            text=message,
            foreground="green" if success else "red",
        )
        if success:
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", message)


def main():
    root = tk.Tk()
    app = ExtractorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
