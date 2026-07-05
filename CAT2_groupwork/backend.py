"""
Poultry Farm Management System
--------------------------------
Module owned by: Flock Registry + UI

This file implements:
  1. Bird        - a simple record representing one bird
  2. FlockRegistry - an ARRAY-BASED data structure that stores all Bird
                     records and supports full CRUD (Create, Read,
                     Update, Delete) operations.
  3. A menu-driven command-line UI that lets a farm manager interact
     with the registry directly from the terminal.

DESIGN NOTES (for the report / complexity analysis section):
  - The registry is a plain Python list, which behaves like a dynamic
    array. This mirrors the "Array — Flock Registry" section of the
    proposal.
  - add_bird()      -> O(1) amortized  (append to end of list)
  - find_bird()     -> O(n) worst case (linear scan by tag_id)
  - edit_bird()     -> O(n) worst case (must locate the bird first)
  - delete_bird()   -> O(n) worst case (locate + shift elements left)
  - get_all_birds() -> O(n) (returns a copy so callers, e.g. the
                        sorting module, never mutate the master list
                        by accident)

INTEGRATION NOTE:
  Your teammates will plug in a hash table (for O(1) tag ID lookup),
  merge sort / quick sort (for sorting a *copy* of the array), and a
  min-heap (for health alerts). This file exposes get_all_birds() and
  simple hooks so those modules can be wired in later without changing
  this file's structure.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional


# ---------------------------------------------------------------------
# 1. BIRD RECORD
# ---------------------------------------------------------------------

VALID_HEALTH_STATUSES = ("Healthy", "Sick", "Critical")


@dataclass
class Bird:
    tag_id: str          # unique identifier, e.g. "PF-001"
    breed: str           # e.g. Broiler, Layer, Kienyeji
    age_weeks: int        # age in weeks
    weight_kg: float      # weight in kilograms
    egg_count: int        # total eggs produced
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


# ---------------------------------------------------------------------
# 2b. CLASSIC SORTING ALGORITHMS (taught in DSA class)
# ---------------------------------------------------------------------
#
# NOTE: Your teammate's module implements merge sort and quick sort for
# the "official" flock sorting features described in the proposal
# (section 3.3 / 3.4). The three algorithms below are the simpler,
# classroom-taught sorts (insertion, selection, bubble) included here
# as an additional demonstration of manual sorting on the array.
#
# All three functions:
#   - take a List[Bird] and a `key` function (e.g. lambda b: b.weight_kg)
#   - operate on a COPY of the list (never mutate the original registry)
#   - sort in ascending order by whatever attribute `key` returns
#
# Complexity (all three, worst/average case):
#   Time  -> O(n^2)
#   Space -> O(1) extra (in-place on the copy)
# They are less efficient than merge sort / quick sort (O(n log n)),
# which is exactly the kind of comparison your report can make.

def insertion_sort(birds: List[Bird], key) -> List[Bird]:
    """
    Insertion Sort: builds the sorted list one element at a time.
    At each step, take the next unsorted element and insert it into
    its correct position among the already-sorted elements to its left.
    Good for small or nearly-sorted lists. Stable sort.
    """
    result = birds.copy()
    for i in range(1, len(result)):
        current = result[i]
        j = i - 1
        # Shift elements greater than `current` one position to the right
        while j >= 0 and key(result[j]) > key(current):
            result[j + 1] = result[j]
            j -= 1
        result[j + 1] = current
    return result


def selection_sort(birds: List[Bird], key) -> List[Bird]:
    """
    Selection Sort: repeatedly finds the minimum element from the
    unsorted portion and swaps it into place at the front.
    Not stable. Always O(n^2) comparisons, even on sorted input.
    """
    result = birds.copy()
    n = len(result)
    for i in range(n):
        min_index = i
        for j in range(i + 1, n):
            if key(result[j]) < key(result[min_index]):
                min_index = j
        if min_index != i:
            result[i], result[min_index] = result[min_index], result[i]
    return result


def bubble_sort(birds: List[Bird], key) -> List[Bird]:
    """
    Bubble Sort: repeatedly steps through the list, swapping adjacent
    elements if they are in the wrong order. Each full pass "bubbles"
    the largest remaining value to the end. Stable sort.
    Includes an early-exit flag: if a full pass makes no swaps, the
    list is already sorted, so we stop early (best case O(n)).
    """
    result = birds.copy()
    n = len(result)
    for i in range(n - 1):
        swapped = False
        for j in range(n - 1 - i):
            if key(result[j]) > key(result[j + 1]):
                result[j], result[j + 1] = result[j + 1], result[j]
                swapped = True
        if not swapped:
            break
    return result


# Convenience key functions for sorting birds by common attributes
SORT_KEYS = {
    "weight": lambda b: b.weight_kg,
    "age": lambda b: b.age_weeks,
    "eggs": lambda b: b.egg_count,
}


# ---------------------------------------------------------------------
# 3. MENU-DRIVEN COMMAND-LINE UI
# ---------------------------------------------------------------------

def print_header(title: str):
    print("\n" + "=" * 60)
    print(title.center(60))
    print("=" * 60)


def print_flock_table(birds: List[Bird]):
    if not birds:
        print("No birds in the registry yet.")
        return
    print(f"{'TAG ID':<8} | {'BREED':<10} | {'AGE':>4} | {'WEIGHT':>7} | "
          f"{'EGGS':<9} | HEALTH")
    print("-" * 60)
    for bird in birds:
        print(bird)


def prompt_new_bird() -> Bird:
    print("\n-- Add New Bird --")
    tag_id = input("Tag ID (e.g. PF-001): ").strip()
    breed = input("Breed (Broiler / Layer / Kienyeji): ").strip()
    age_weeks = int(input("Age (weeks): ").strip())
    weight_kg = float(input("Weight (kg): ").strip())
    egg_count = int(input("Egg count: ").strip())
    health_status = input(
        "Health status (Healthy / Sick / Critical) [Healthy]: "
    ).strip() or "Healthy"
    return Bird(tag_id, breed, age_weeks, weight_kg, egg_count, health_status)


def run_ui():
    registry = FlockRegistry()

    menu = """
1. Add bird
2. View all birds
3. Search bird by Tag ID
4. Edit bird
5. Delete bird
6. Sort flock (insertion / selection / bubble sort)
7. Exit
"""

    print_header("POULTRY FARM MANAGEMENT SYSTEM")

    while True:
        print(menu)
        choice = input("Select an option (1-6): ").strip()

        try:
            if choice == "1":
                bird = prompt_new_bird()
                registry.add_bird(bird)
                print(f"\n✔ Bird '{bird.tag_id}' added successfully.")

            elif choice == "2":
                print_header(f"FLOCK REGISTRY ({registry.count()} birds)")
                print_flock_table(registry.get_all_birds())

            elif choice == "3":
                tag_id = input("Enter Tag ID to search: ").strip()
                bird = registry.find_bird(tag_id)
                print("\n✔ Found:")
                print(bird)

            elif choice == "4":
                tag_id = input("Enter Tag ID to edit: ").strip()
                print("Leave a field blank to keep its current value.")
                current = registry.find_bird(tag_id)
                print(f"Current record: {current}")

                updates = {}
                new_weight = input("New weight (kg): ").strip()
                if new_weight:
                    updates["weight_kg"] = float(new_weight)
                new_age = input("New age (weeks): ").strip()
                if new_age:
                    updates["age_weeks"] = int(new_age)
                new_eggs = input("New egg count: ").strip()
                if new_eggs:
                    updates["egg_count"] = int(new_eggs)
                new_health = input("New health status: ").strip()
                if new_health:
                    updates["health_status"] = new_health

                updated = registry.edit_bird(tag_id, **updates)
                print(f"\n✔ Updated record: {updated}")

            elif choice == "5":
                tag_id = input("Enter Tag ID to delete: ").strip()
                removed = registry.delete_bird(tag_id)
                print(f"\n✔ Removed: {removed}")

            elif choice == "6":
                attr = input(
                    "Sort by (weight / age / eggs): "
                ).strip().lower()
                if attr not in SORT_KEYS:
                    print("⚠ Please choose weight, age, or eggs.")
                    continue
                key = SORT_KEYS[attr]

                algo = input(
                    "Algorithm (insertion / selection / bubble): "
                ).strip().lower()
                if algo == "insertion":
                    sorted_birds = insertion_sort(registry.get_all_birds(), key)
                elif algo == "selection":
                    sorted_birds = selection_sort(registry.get_all_birds(), key)
                elif algo == "bubble":
                    sorted_birds = bubble_sort(registry.get_all_birds(), key)
                else:
                    print("⚠ Please choose insertion, selection, or bubble.")
                    continue

                print_header(f"FLOCK SORTED BY {attr.upper()} ({algo.title()} Sort)")
                print_flock_table(sorted_birds)
                print("\nNote: original registry order is unchanged — "
                      "this is a sorted copy for display only.")

            elif choice == "7":
                print("\nGoodbye!")
                break

            else:
                print("Invalid option, please choose 1-6.")

        except (DuplicateTagIDError, BirdNotFoundError, ValueError,
                AttributeError) as e:
            print(f"\n⚠ Error: {e}")


if __name__ == "__main__":
    run_ui()