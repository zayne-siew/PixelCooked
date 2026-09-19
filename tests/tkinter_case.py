"""Reusable unittest support for Tkinter tests."""

import tkinter as tk
import unittest


class TkinterTestCase(unittest.TestCase):
    """Base test case that provides a hidden native Tkinter root and canvas."""

    root: tk.Tk
    canvas: tk.Canvas

    def setUp(self) -> None:
        """Create a hidden Tk root and a real canvas for the test."""
        try:
            self.root = tk.Tk()
        except tk.TclError as error:
            self.skipTest(f"Tkinter display is unavailable: {error}")

        self.root.withdraw()
        self.canvas = tk.Canvas(self.root)
        self.canvas.pack()
        self.root.update_idletasks()

    def tearDown(self) -> None:
        """Destroy the Tk root and release its native resources."""
        self.root.destroy()


if __name__ == "__main__":
    pass
