"""Base class for all ingredients."""

from abc import ABC, abstractmethod
from typing import overload

from pydantic import BaseModel, ConfigDict, PrivateAttr, computed_field
import tkinter as tk

from src.constants import OUTLINE_COLOR, OUTLINE_WIDTH_PX
from src.players.direction import PlayerDirection
from src.players.player import Player


class Ingredient(BaseModel, ABC):
    """Represents a generic interactive ingredient on the map.

    Allows for:
        - Picking up / placing down
        - Moving around
        - Chopping and cooking
    """
    model_config = ConfigDict(extra="forbid", strict=True)

    _ingredient: int = PrivateAttr()
    """The ID of the ingredient on the canvas."""

    _player: Player | None = PrivateAttr(default=None)
    """The player that is currently holding the ingredient."""

    _screen: tk.Canvas = PrivateAttr()
    """The canvas on which the ingredient is drawn."""

    _can_chop: bool = PrivateAttr(default=False)
    """Whether the ingredient can be chopped."""

    _can_cook: bool = PrivateAttr(default=False)
    """Whether the ingredient can be cooked."""

    def __init__(
        self,
        screen: tk.Canvas,
        x: float,
        y: float,
        length: float,
        fill: str,
        *,
        can_chop: bool = False,
        can_cook: bool = False,
    ):
        """Initializes the ingredient.
        
        Args:
            screen (tk.Canvas): The canvas on which the ingredient is drawn.
            x (float): The x-coordinate of the top left corner of the ingredient.
            y (float): The y-coordinate of the top left corner of the ingredient.
            length (float): The length of the ingredient (assumed to be square).
            fill (str): The fill color of the ingredient.
            can_chop (bool): Whether the ingredient can be chopped.
            can_cook (bool): Whether the ingredient can be cooked.
        """
        super().__init__()
        self._ingredient = screen.create_oval(
            x,
            y,
            x + length,
            y + length,
            outline=OUTLINE_COLOR,
            fill=fill,
            width=OUTLINE_WIDTH_PX,
        )
        self._screen = screen
        self._can_chop = can_chop
        self._can_cook = can_cook

    @computed_field  # type: ignore[prop-decorator]
    @property
    def can_chop(self) -> bool:
        """Whether the ingredient can be chopped."""
        return self._can_chop

    @computed_field  # type: ignore[prop-decorator]
    @property
    def can_cook(self) -> bool:
        """Whether the ingredient can be cooked."""
        return self._can_cook

    @computed_field  # type: ignore[prop-decorator]
    @property
    def ingredient(self) -> int:
        """The ID of the ingredient on the canvas."""
        return self._ingredient

    @computed_field  # type: ignore[prop-decorator]
    @property
    def coords(self) -> tuple[float, float, float, float]:
        """The coordinates of the ingredient on the canvas.
        
        Returns:
            tuple[float, float, float, float]:
                The coordinates of the ingredient on the canvas
        
        Raises:
            ValueError: If the number of coordinates is not 4.
        """
        coords = self._screen.coords(self._ingredient)
        if len(coords) != 4:
            raise ValueError(f"Expected 4 coordinates, got {len(coords)}")
        return tuple(coords)  # type: ignore[return-value]

    @overload
    def move(self, x: float, y: float) -> None:
        """Moves the ingredient by `(x, y)` pixels.
        
        Args:
            x (float): The number of pixels to move the ingredient in the x-direction.
            y (float): The number of pixels to move the ingredient in the y-direction.
        """
        ...

    @overload
    def move(self) -> None:
        """Leaves the ingredient in its current position."""
        ...

    @overload
    def move(self, *, x: float) -> None:
        """Moves the ingredient by `x` pixels in the x-direction.
        
        Args:
            x (float): The number of pixels to move the ingredient in the x-direction.
        """
        ...

    @overload
    def move(self, *, y: float) -> None:
        """Moves the ingredient by `y` pixels in the y-direction.
        
        Args:
            y (float): The number of pixels to move the ingredient in the y-direction.
        """
        ...

    def move(
        self,
        x: float | None = None,
        y: float | None = None,
    ) -> None:
        """Moves the ingredient by `(x, y)` pixels.
        
        Args:
            x (float | None): The number of pixels to move the ingredient in the
                x-direction. Defaults to zero when omitted.
            y (float | None): The number of pixels to move the ingredient in the
                y-direction. Defaults to zero when omitted.
        """
        self._screen.move(
            self._ingredient,
            0.0 if x is None else x,
            0.0 if y is None else y,
        )

    @overload
    def moveto(self, x: float, y: float) -> None:
        """Moves the ingredient to `(x, y)` as its new top-left coordinate.
        
        Args:
            x (float): The x-coordinate to move the ingredient to.
            y (float): The y-coordinate to move the ingredient to.
        """
        ...

    @overload
    def moveto(self) -> None:
        """Leaves the ingredient in its current position."""
        ...

    @overload
    def moveto(self, *, x: float) -> None:
        """Moves the ingredient to `x`, preserving its current y-coordinate.
        
        Args:
            x (float): The x-coordinate to move the ingredient to.
        """
        ...

    @overload
    def moveto(self, *, y: float) -> None:
        """Moves the ingredient to `y`, preserving its current x-coordinate.
        
        Args:
            y (float): The y-coordinate to move the ingredient to.
        """
        ...

    @overload
    def moveto(
        self,
        x: float | None = None,
        y: float | None = None,
    ) -> None:
        """Moves the ingredient to the specified top-left coordinates.
        
        Args:
            x (float | None): The x-coordinate to move the ingredient to.
                If omitted, the current x-coordinate is preserved.
            y (float | None): The y-coordinate to move the ingredient to.
                If omitted, the current y-coordinate is preserved.
        """

    def moveto(
        self,
        x: float | None = None,
        y: float | None = None,
    ) -> None:
        self._screen.moveto(
            self._ingredient,
            "" if x is None else x,
            "" if y is None else y,
        )

    def drop(self, x: float | None = None, y: float | None = None) -> None:
        """Drops the ingredient at the specified coordinates and removes player owner.

        Args:
            x (float | None): The x-coordinate to drop the ingredient to.
                If None, the ingredient will not be moved in the x-direction.
            y (float | None): The y-coordinate to drop the ingredient to.
                If None, the ingredient will not be moved in the y-direction.
        """
        if self._player is None:
            return
        self.moveto(x, y)
        self._player = None

    def pick_up(self, player: Player) -> None:
        """Allows a player to pick up the ingredient.

        The ingredient will be moved to the player's coordinates, and the player will be
        set as the owner of the ingredient. If another player has already picked up the
        ingredient, this method will do nothing.

        Args:
            player (Player): The player who is picking up the ingredient.
        
        Raises:
            ValueError: If the coordinates of the player or ingredient are not in the
                expected format.
        """
        if self._player:
            # another player has already picked this ingredient up
            return
        self._player = player
        x1, y1, x2, y2 = player.coords
        x3, _, x4, _ = self.coords
        x = (
            x1 + x3 - x4 if player.direction == PlayerDirection.LEFT
            else x2 if player.direction == PlayerDirection.RIGHT
            else (x1 + x2 + x3 - x4) / 2
        )
        y = (
            y1 + x3 - x4 if player.direction == PlayerDirection.UP
            else y2 if player.direction == PlayerDirection.DOWN
            else (y1 + y2 + x3 - x4) / 2
        )
        self.moveto(x, y)

    @abstractmethod
    def chop(self) -> "Ingredient":
        """Returns the resultant ingredient from the chopping process.

        If the ingredient cannot be chopped, it returns itself.

        Returns:
            Ingredient: The resultant ingredient from the chopping process.
        """
        return self

    @abstractmethod
    def cook(self) -> "Ingredient":
        """Returns the resultant ingredient from the cooking process.
        
        If the ingredient cannot be cooked, it returns itself.

        Returns:
            Ingredient: The resultant ingredient from the cooking process.
        """
        return self


if __name__ == "__main__":
    pass
