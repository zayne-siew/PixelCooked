"""Player class for the game."""

from collections.abc import Sequence

from pydantic import BaseModel, ConfigDict, PrivateAttr, computed_field
import tkinter as tk

from src.constants import OUTLINE_COLOR, OUTLINE_WIDTH_PX
from src.players.direction import PlayerDirection


class Player(BaseModel):
    """Class representing a player in the game."""
    model_config = ConfigDict(extra="forbid", strict=True)

    _player: int = PrivateAttr()
    """The ID of the player on the canvas."""

    _screen: tk.Canvas = PrivateAttr()
    """The canvas on which the player is drawn."""

    _direction: PlayerDirection = PrivateAttr()
    """The direction the player is facing."""

    def __init__(
            self,
            screen: tk.Canvas,
            x: float,
            y: float,
            length: float,
            velocity,
            fill,
    ):
        # (x, y) is the top left corner
        self._ingredient = None
        self._direction = PlayerDirection.UP
        self._vx = self._vy = 0
        self._interact = False
        self._screen = screen
        self._velocity = velocity
        self._fill = fill
        triangle = ((x, y + length),
            (x + 0.5 * length, y),
            (x + length, y + length))
        self._player = self._create(triangle)
    
    def _create(self, triangle: Sequence[float]) -> int:
        return self._screen.create_polygon(
            triangle,
            outline=OUTLINE_COLOR,
            fill=self._fill,
            width=OUTLINE_WIDTH_PX,
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def direction(self) -> PlayerDirection:
        """The direction the player is facing."""
        return self._direction

    @computed_field  # type: ignore[prop-decorator]
    @property
    def coords(self) -> tuple[float, float, float, float]:
        """The coordinates of the player on the canvas.

        Returns:
            tuple[float, float, float, float]:
                The coordinates of the player on the canvas
        
        Raises:
            ValueError: If the number of coordinates retrieved from tkinter is not 6.
        """
        coords = self._screen.coords(self._player)
        if len(coords) != 6:
            raise ValueError(f"Expected 6 coordinates, got {len(coords)}")
        x1, y1, x2, y2, x3, y3 = coords
        return min(x1, x2, x3), min(y1, y2, y3), max(x1, x2, x3), max(y1, y2, y3)


if __name__ == "__main__":
    pass
