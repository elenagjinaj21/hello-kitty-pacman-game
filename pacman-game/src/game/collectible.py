"""Collectible items - pacgums and super-pacgums."""

from enum import Enum
from typing import List, Tuple
from utils.constants import (
    PACGUM_VALUE, SUPER_PACGUM_VALUE,
    PACGUM_SIZE, SUPER_PACGUM_SIZE,
)


class CollectibleType(Enum):
    """Types of collectibles."""
    PACGUM = "pacgum"
    SUPER_PACGUM = "super_pacgum"


class Collectible:
    """Base collectible class."""

    def __init__(self, x: int, y: int, collectible_type: CollectibleType):
        """
        Initialize a collectible.

        Args:
            x: X position in maze cells
            y: Y position in maze cells
            collectible_type: Type of collectible
        """
        self.x = x
        self.y = y
        self.type = collectible_type
        self.collected = False

    @property
    def value(self) -> int:
        """Get the point value of this collectible."""
        if self.type == CollectibleType.PACGUM:
            return PACGUM_VALUE
        elif self.type == CollectibleType.SUPER_PACGUM:
            return SUPER_PACGUM_VALUE
        return 0

    @property
    def size(self) -> int:
        """Get the visual size of this collectible."""
        if self.type == CollectibleType.PACGUM:
            return PACGUM_SIZE
        elif self.type == CollectibleType.SUPER_PACGUM:
            return SUPER_PACGUM_SIZE
        return 0

    @property
    def is_power_up(self) -> bool:
        """Check if this collectible is a power-up."""
        return self.type == CollectibleType.SUPER_PACGUM

    def collect(self) -> None:
        """Mark this collectible as collected."""
        self.collected = True

    def __repr__(self) -> str:
        return f"Collectible({self.x}, {self.y}, {self.type.value})"


class CollectibleManager:
    """Manages all collectibles in the level."""

    def __init__(self) -> None:
        """Initialize the collectible manager."""
        self.collectibles: List[Collectible] = []
        self.total_collectibles = 0

    def add_collectible(
        self,
        x: int,
        y: int,
        collectible_type: CollectibleType,
    ) -> None:
        """Add a collectible to the level."""
        self.collectibles.append(Collectible(x, y, collectible_type))
        self.total_collectibles += 1

    def create_level_collectibles(
        self,
        corridors: List[Tuple[int, int]],
        corners: List[Tuple[int, int]]
    ) -> None:
        """
        Create collectibles for a level.

        Args:
            corridors: List of all corridor positions
            corners: List of corner positions
        """
        self.collectibles.clear()
        self.total_collectibles = 0

        # Add super-pacgums to corners
        for corner in corners:
            if corner in corridors:
                self.add_collectible(corner[0], corner[1], CollectibleType.SUPER_PACGUM)

        # Add regular pacgums to corridors (excluding corners)
        for x, y in corridors:
            if (x, y) not in corners:
                self.add_collectible(x, y, CollectibleType.PACGUM)

    def collect_at_position(self, x: int, y: int) -> Tuple[bool, int, bool]:
        """
        Collect collectibles at a given position.

        Args:
            x: X position
            y: Y position

        Returns:
            Tuple of (collected_any, points_gained, is_power_up)
        """
        collected_any = False
        points_gained = 0
        is_power_up = False

        for collectible in self.collectibles:
            if not collectible.collected and collectible.x == x and collectible.y == y:
                collectible.collect()
                collected_any = True
                points_gained += collectible.value
                if collectible.is_power_up:
                    is_power_up = True

        return collected_any, points_gained, is_power_up

    def get_remaining_count(self) -> int:
        """Get the number of remaining collectibles."""
        return sum(1 for c in self.collectibles if not c.collected)

    def get_remaining_pacgums(self) -> int:
        """Get the number of remaining pacgums (not super-pacgums)."""
        return sum(
            1 for c in self.collectibles
            if not c.collected and c.type == CollectibleType.PACGUM
        )

    def get_remaining_super_pacgums(self) -> int:
        """Get the number of remaining super-pacgums."""
        return sum(
            1 for c in self.collectibles
            if not c.collected and c.type == CollectibleType.SUPER_PACGUM
        )

    def is_level_complete(self) -> bool:
        """Check if all collectibles have been collected."""
        return all(c.collected for c in self.collectibles)

    def get_all_collectibles(self) -> List[Collectible]:
        """Get all collectibles."""
        return self.collectibles

    def reset(self) -> None:
        """Reset all collectibles for a new level."""
        self.collectibles.clear()
        self.total_collectibles = 0
