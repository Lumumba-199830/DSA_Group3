"""
Poultry Farm Management System — Flock Registry (backend)
"""
from dataclasses import dataclass, asdict
from typing import List
# ---------------------------------------------------------------------
# 1. BIRD RECORD
# ---------------------------------------------------------------------

VALID_HEALTH_STATUSES = ("Healthy", "Sick", "Critical")


@dataclass
class Bird:
    tag_id: str            # unique identifier, e.g. "PF-001"
    breed: str             # e.g. Broiler, Layer, Kienyeji
    age_weeks: int         # age in weeks
    weight_kg: float       # weight in kilograms
    egg_count: int         # total eggs produced
    health_status: str = "Healthy"   # Healthy | Sick | Critical

    def __post_init__(self):
        if self.health_status not in VALID_HEALTH_STATUSES:
            raise ValueError(
                f"health_status must be one of {VALID_HEALTH_STATUSES}, "
                f"got '{self.health_status}'"
            )

    def to_dict(self):
        return asdict(self)

    def __str__(self):
        return (
            f"{self.tag_id:<8} | {self.breed:<10} | "
            f"{self.age_weeks:>3}w | {self.weight_kg:>5.2f}kg | "
            f"eggs:{self.egg_count:<4} | {self.health_status}"
        )


# ---------------------------------------------------------------------
# 2. FLOCK REGISTRY (ARRAY-BASED CRUD)
# ---------------------------------------------------------------------

class DuplicateTagIDError(Exception):
    """Raised when a bird with the same tag_id already exists."""
    pass


class BirdNotFoundError(Exception):
    """Raised when a tag_id does not match any bird in the registry."""
    pass


class FlockRegistry:
    """
    Array-based store for every bird on the farm.

    Internally this wraps a Python list (self._flock), which is a
    dynamic array. All CRUD operations are implemented manually with
    explicit loops (rather than relying on things like `in` or
    dict lookups) so the O(n) behaviour described in the report is
    visible in the code.
    """

    def __init__(self):
        self._flock: List[Bird] = []

    # ---- CREATE -------------------------------------------------
    def add_bird(self, bird: Bird) -> None:
        """
        Append a new bird to the registry. O(1) amortized.
        Raises DuplicateTagIDError if the tag_id is already in use.
        """
        if self._find_index(bird.tag_id) != -1:
            raise DuplicateTagIDError(
                f"A bird with tag ID '{bird.tag_id}' already exists."
            )
        self._flock.append(bird)

    # ---- READ -----------------------------------------------------
    def find_bird(self, tag_id: str) -> Bird:
        """
        Linear search for a bird by tag ID. O(n) worst case.
        (Once the hash table module is wired in, this is the method
        it will speed up to O(1) average case.)
        """
        index = self._find_index(tag_id)
        if index == -1:
            raise BirdNotFoundError(f"No bird found with tag ID '{tag_id}'.")
        return self._flock[index]

    def get_all_birds(self) -> List[Bird]:
        """
        Returns a shallow COPY of the registry list. Sorting or
        filtering modules should operate on this copy, never on the
        internal list directly, so the master registry stays intact.
        """
        return self._flock.copy()

    def count(self) -> int:
        return len(self._flock)

    # ---- UPDATE -----------------------------------------------------
    def edit_bird(self, tag_id: str, **fields) -> Bird:
        """
        Update one or more fields on an existing bird.
        Example: registry.edit_bird("PF-001", weight_kg=2.4, health_status="Sick")
        """
        index = self._find_index(tag_id)
        if index == -1:
            raise BirdNotFoundError(f"No bird found with tag ID '{tag_id}'.")

        bird = self._flock[index]
        for key, value in fields.items():
            if not hasattr(bird, key):
                raise AttributeError(f"Bird has no field '{key}'.")
            setattr(bird, key, value)

        # Re-validate health_status in case it was changed
        if bird.health_status not in VALID_HEALTH_STATUSES:
            raise ValueError(
                f"health_status must be one of {VALID_HEALTH_STATUSES}"
            )

        self._flock[index] = bird
        return bird

    # ---- DELETE -----------------------------------------------------
    def delete_bird(self, tag_id: str) -> Bird:
        """
        Remove a bird from the registry. O(n) worst case:
        locate the bird (O(n)) then shift all following elements
        left by one position (O(n)).
        """
        index = self._find_index(tag_id)
        if index == -1:
            raise BirdNotFoundError(f"No bird found with tag ID '{tag_id}'.")
        return self._flock.pop(index)

    # ---- INTERNAL HELPER --------------------------------------------
    def _find_index(self, tag_id: str) -> int:
        """Manual linear scan returning the index, or -1 if not found."""
        for i in range(len(self._flock)):
            if self._flock[i].tag_id == tag_id:
                return i
        return -1


# Small smoke test — only runs if this file is executed directly
if __name__ == "__main__":
    registry = FlockRegistry()
    registry.add_bird(Bird("PF-001", "Broiler", 6, 2.1, 0, "Healthy"))
    registry.add_bird(Bird("PF-002", "Layer", 10, 1.8, 120, "Sick"))
    print(f"{registry.count()} birds in registry:")
    for b in registry.get_all_birds():
        print(b)