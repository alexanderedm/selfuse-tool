"""
Implementation of the desktop pet plugin.

This plugin opens a borderless window that floats on top of other
windows.  It cycles through a sequence of images for its idle animation
and swaps to alternative images on user interaction (hover, click,
drag).  You can customise the images by placing PNG files in the
``assets`` subdirectory next to this module.

If the Pillow library (PIL) is not installed, the plugin will log an
error and do nothing.
"""

import os
import threading
import time
from typing import Dict, List

try:
    import tkinter as tk
    from PIL import Image, ImageTk
except ImportError:
    # If dependencies are missing, the plugin should not crash the host
    tk = None  # type: ignore
    Image = None  # type: ignore
    ImageTk = None  # type: ignore

from src.plugins.plugin_base import Plugin
from src.core.logger import logger


class DesktopPetWindow(tk.Toplevel):  # type: ignore
    """A top‑level window that displays the animated pet."""

    def __init__(self, master: tk.Tk, frames: Dict[str, List[ImageTk.PhotoImage]]) -> None:
        super().__init__(master)
        self.frames = frames
        self.current_animation = "idle"
        self.frame_index = 0

        # Remove window borders and set always on top
        self.overrideredirect(True)
        self.attributes("-topmost", True)

        # Create label to display the pet image
        self.label = tk.Label(self, bd=0, bg="transparent")
        self.label.pack()

        # Bind mouse events
        self.label.bind("<Enter>", self.on_hover)
        self.label.bind("<Leave>", self.on_leave)
        self.label.bind("<Button-1>", self.on_click)
        self.label.bind("<B1-Motion>", self.on_drag)
        self.label.bind("<ButtonRelease-1>", self.on_release)

        # Position the window near the bottom right corner
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = self.frames["idle"][0].width()
        window_height = self.frames["idle"][0].height()
        x = screen_width - window_width - 100
        y = screen_height - window_height - 150
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self._running = True
        self.animation_thread = threading.Thread(target=self.run_animation, daemon=True)
        self.animation_thread.start()

    def run_animation(self) -> None:
        """Cycle through the current animation's frames."""
        while self._running:
            frames = self.frames.get(self.current_animation) or self.frames["idle"]
            frame = frames[self.frame_index % len(frames)]
            self.label.configure(image=frame)
            self.frame_index = (self.frame_index + 1) % len(frames)
            # Idle frames have a slower cadence
            delay = 0.5 if self.current_animation == "idle" else 0.3
            time.sleep(delay)

    def switch_animation(self, name: str) -> None:
        """Switch to another animation sequence."""
        if name in self.frames:
            self.current_animation = name
            self.frame_index = 0

    # Event handlers
    def on_hover(self, event) -> None:
        logger.debug("DesktopPet: hover")
        self.switch_animation("hover")

    def on_leave(self, event) -> None:
        logger.debug("DesktopPet: leave")
        self.switch_animation("idle")

    def on_click(self, event) -> None:
        logger.debug("DesktopPet: click")
        self.switch_animation("click")

    def on_drag(self, event) -> None:
        logger.debug("DesktopPet: drag")
        self.switch_animation("drag")

    def on_release(self, event) -> None:
        logger.debug("DesktopPet: release")
        self.switch_animation("idle")

    def stop(self) -> None:
        """Stop the animation thread."""
        self._running = False


class Plugin(Plugin):  # type: ignore
    """Concrete plugin that spawns the desktop pet window."""

    def __init__(self) -> None:
        self.window: DesktopPetWindow | None = None

    def load_frames(self, assets_path: str) -> Dict[str, List[ImageTk.PhotoImage]]:
        """Load PNG frames for each animation from ``assets_path``.

        Returns a dictionary mapping animation names to lists of images.
        Missing animations will fall back to the idle frames.
        """
        animations: Dict[str, List[ImageTk.PhotoImage]] = {
            "idle": [],
            "hover": [],
            "click": [],
            "drag": [],
        }
        for name in animations:
            # Gather all PNG files starting with the pattern
            files = sorted(
                [
                    f
                    for f in os.listdir(assets_path)
                    if f.startswith(name) and f.lower().endswith(".png")
                ]
            )
            for file in files:
                image_path = os.path.join(assets_path, file)
                try:
                    pil_img = Image.open(image_path)
                    animations[name].append(ImageTk.PhotoImage(pil_img))
                except Exception as exc:
                    logger.exception(f"Failed to load image {image_path}: {exc}")
        # Ensure there is at least one idle frame
        if not animations["idle"]:
            raise RuntimeError("No idle frames found for desktop pet plugin")
        # For any empty animation, fallback to idle frames
        for name, frames in list(animations.items()):
            if not frames:
                animations[name] = animations["idle"]
        return animations

    def start(self) -> None:
        """Entry point called by the plugin loader."""
        if tk is None or Image is None or ImageTk is None:
            logger.error(
                "Desktop pet plugin requires tkinter and Pillow; plugin disabled"
            )
            return
        try:
            # Create a hidden root window for Tkinter
            root = tk.Tk()
            root.withdraw()
            assets_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "assets"
            )
            frames = self.load_frames(assets_path)
            self.window = DesktopPetWindow(root, frames)
            # Start Tkinter event loop
            logger.info("Desktop pet plugin started")
            root.mainloop()
        except Exception as exc:
            logger.exception(f"Desktop pet plugin failed to start: {exc}")

    def stop(self) -> None:
        """Stop the desktop pet when shutting down the application."""
        if self.window:
            self.window.stop()
