"""Tests for the base ingredient class."""

import unittest
from typing import cast
from unittest.mock import patch

from src.ingredients.base import Ingredient
from src.players.direction import PlayerDirection
from src.players.player import Player
from tests.tkinter_case import TkinterTestCase


_EXPECTED_INITIAL_COORDS = (10, 20, 40, 50)
_MOVE_X = 5
_MOVE_Y = -10
_EXPECTED_MOVED_COORDS = (15, 10, 45, 40)
_EXPECTED_X_MOVED_COORDS = (15, 20, 45, 50)
_EXPECTED_Y_MOVED_COORDS = (15, 10, 45, 40)
_MOVE_TO_X = 100
_MOVE_TO_Y = 200
_EXPECTED_MOVETO_COORDS = (101.0, 201.0, 131.0, 231.0)
_EXPECTED_X_MOVETO_COORDS = (101.0, 20.0, 131.0, 50.0)
_EXPECTED_DROP_COORDS = (76.0, 20.0, 106.0, 50.0)
_PLAYER_COORDS = (100, 100, 120, 120)
_EXPECTED_PICKUP_COORDS = (121.0, 96.0, 151.0, 126.0)


class TestIngredient(Ingredient):
    """Concrete ingredient used to exercise the abstract base class."""


class FakePlayer:
	"""Minimal player double exposing coordinates and direction."""

	def __init__(self, coords, direction):
		"""Store the player's geometry and facing direction."""
		self.coords = coords
		self.direction = direction


class IngredientTests(TkinterTestCase):
	def setUp(self) -> None:
		"""Create a fresh native canvas and ingredient for each test."""
		super().setUp()
		self.ingredient = TestIngredient(  # type: ignore[call-arg]
			self.canvas,  # pyright: ignore[reportCallIssue]
			10,
			20,
			30,
			"red",
			can_chop=True,
			can_cook=True,
		)

	def test_initializes_canvas_item_and_computed_fields(self):
		"""Verify canvas creation and computed ingredient properties."""
		self.assertEqual(self.ingredient.coords, _EXPECTED_INITIAL_COORDS)
		self.assertTrue(self.ingredient.can_chop)
		self.assertTrue(self.ingredient.can_cook)
		self.assertEqual(self.ingredient.ingredient, 1)
		self.assertEqual(
			self.canvas.itemcget(self.ingredient.ingredient, "fill"),
			"red",
		)

	def test_coords_rejects_non_bounding_box(self):
		"""Reject canvas coordinate results that are not bounding boxes."""
		with (
			patch.object(self.canvas, "coords", return_value=[1, 2, 3]),
			self.assertRaisesRegex(ValueError, "Expected 4 coordinates"),
		):
			_ = self.ingredient.coords

	def test_move_supports_both_axes(self):
		"""Move the ingredient along both axes with positional arguments."""
		self.ingredient.move(_MOVE_X, _MOVE_Y)

		self.assertEqual(self.ingredient.coords, _EXPECTED_MOVED_COORDS)

	def test_move_supports_single_axis(self):
		"""Move the ingredient along either axis independently."""
		self.ingredient.move(x=_MOVE_X)
		self.assertEqual(self.ingredient.coords, _EXPECTED_X_MOVED_COORDS)

		self.ingredient.move(y=_MOVE_Y)
		self.assertEqual(self.ingredient.coords, _EXPECTED_Y_MOVED_COORDS)

	def test_empty_move_is_a_no_op(self):
		"""Allow an empty move call without changing the ingredient."""
		self.ingredient.move()

		self.assertEqual(self.ingredient.coords, _EXPECTED_INITIAL_COORDS)

	def test_moveto_supports_both_axes(self):
		"""Move the ingredient to a new top-left coordinate."""
		self.ingredient.moveto(_MOVE_TO_X, _MOVE_TO_Y)

		self.assertEqual(self.ingredient.coords, _EXPECTED_MOVETO_COORDS)

	def test_moveto_preserves_omitted_axis(self):
		"""Preserve the current axis when moveto receives one coordinate."""
		self.ingredient.moveto(x=_MOVE_TO_X)
		self.assertEqual(self.ingredient.coords, _EXPECTED_X_MOVETO_COORDS)

		self.ingredient.moveto(y=_MOVE_TO_Y)
		self.assertEqual(self.ingredient.coords, _EXPECTED_MOVETO_COORDS)

	def test_empty_moveto_is_a_no_op(self):
		"""Allow an empty moveto call without changing the ingredient."""
		self.ingredient.moveto()

		self.assertEqual(self.ingredient.coords, _EXPECTED_INITIAL_COORDS)

	def test_drop_clears_player_and_preserves_omitted_axis(self):
		"""Clear ownership while preserving an omitted drop coordinate."""
		player = FakePlayer((0, 0, 10, 10), PlayerDirection.RIGHT)
		self.ingredient._player = cast("Player", player)

		self.ingredient.drop(x=75)

		self.assertEqual(self.ingredient.coords, _EXPECTED_DROP_COORDS)
		self.assertIsNone(self.ingredient._player)

	def test_pick_up_moves_ingredient_in_front_of_player(self):
		"""Move the ingredient in front of a player who picks it up."""
		player = FakePlayer(_PLAYER_COORDS, PlayerDirection.RIGHT)

		self.ingredient.pick_up(cast("Player", player))

		self.assertEqual(self.ingredient.coords, _EXPECTED_PICKUP_COORDS)
		self.assertIs(self.ingredient._player, player)


if __name__ == "__main__":
	unittest.main()
