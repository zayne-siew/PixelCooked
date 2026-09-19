"""Player movement direction constants."""

from enum import IntEnum, unique


@unique
class PlayerDirection(IntEnum):
    """Class containing constants for player movement directions."""

    UP = 0
    """The UP direction."""
    DOWN = 1
    """The DOWN direction."""
    LEFT = 2
    """The LEFT direction."""
    RIGHT = 3
    """The RIGHT direction."""


if __name__ == "__main__":
    pass
