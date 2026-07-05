"""
Poultry Farm Management System — UI (ui.py)
-----------------------------------------------
Owned by: Flock Registry & UI module

This is the interactive menu that lets you actually type in commands
to add, view, search, edit, and delete birds. It imports Bird and
FlockRegistry from the backend file and never redefines them here.

RUN THIS FILE (not flock_registry_backend.py) to get the CRUD menu:
    python ui.py
"""

"""
Poultry Farm Management System — UI (ui.py)
-----------------------------------------------
Owned by: Flock Registry & UI module

This is the interactive menu that lets you actually type in commands
to add, view, search, edit, and delete birds, and sort the flock.

run_ui() can work in two modes:

  1. STANDALONE — run this file directly (`python ui.py`). It creates
     its own simple registry + sorting, with no hash table.

  2. INTEGRATED — main.py imports run_ui() and calls it with a
     PoultryFarmSystem object (registry + hash table + sorting all
     wired together). This is the mode you want for your actual demo,
     since it uses the real hash table for searching.
"""

from backend import (
    FlockRegistry,
    Bird,
    DuplicateTagIDError,
    BirdNotFoundError,
)

from SortingModule import sort_flock


def print_header(title: str):
    print("\n" + "=" * 60)
    print(title.center(60))
    print("=" * 60)


def print_flock_table(birds):
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


class _StandaloneSystem:
    """
    Lightweight fallback used only when ui.py is run directly on its
    own (no hash table). Search here uses the registry's own linear
    find_bird(), not a hash table.
    """

    def __init__(self):
        self.registry = FlockRegistry()

    def add_bird(self, bird):
        self.registry.add_bird(bird)

    def search_bird(self, tag_id):
        return self.registry.find_bird(tag_id)

    def edit_bird(self, tag_id, **fields):
        return self.registry.edit_bird(tag_id, **fields)

    def delete_bird(self, tag_id):
        return self.registry.delete_bird(tag_id)

    def sorted_flock(self, criteria):
        return sort_flock(self.registry.get_all_birds(), criteria)


def run_ui(system=None):
    """
    system: a PoultryFarmSystem instance from main.py (integrated mode),
    or None to run standalone (creates its own registry, no hash table).
    """
    if system is None:
        system = _StandaloneSystem()

    menu = """
1. Add bird
2. View all birds
3. Search bird by Tag ID
4. Edit bird
5. Delete bird
6. Sort flock
7. Exit
"""

    print_header("POULTRY FARM MANAGEMENT SYSTEM")

    while True:
        print(menu)
        choice = input("Select an option (1-7): ").strip()

        try:
            if choice == "1":
                bird = prompt_new_bird()
                system.add_bird(bird)
                print(f"\n✔ Bird '{bird.tag_id}' added successfully.")

            elif choice == "2":
                birds = system.registry.get_all_birds()
                print_header(f"FLOCK REGISTRY ({len(birds)} birds)")
                print_flock_table(birds)

            elif choice == "3":
                tag_id = input("Enter Tag ID to search: ").strip()
                bird = system.search_bird(tag_id)
                print("\n✔ Found:")
                print(bird)

            elif choice == "4":
                tag_id = input("Enter Tag ID to edit: ").strip()
                print("Leave a field blank to keep its current value.")
                current = system.search_bird(tag_id)
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

                updated = system.edit_bird(tag_id, **updates)
                print(f"\n✔ Updated record: {updated}")

            elif choice == "5":
                tag_id = input("Enter Tag ID to delete: ").strip()
                removed = system.delete_bird(tag_id)
                print(f"\n✔ Removed: {removed}")

            elif choice == "6":
                print("\nSort by: weight_kg / age_weeks / egg_count")
                criteria = input("Enter attribute to sort by: ").strip()
                sorted_birds = system.sorted_flock(criteria)
                print_header(f"FLOCK SORTED BY {criteria.upper()}")
                print_flock_table(sorted_birds)
                print("\nNote: original registry order is unchanged — "
                      "this is a sorted copy for display only.")

            elif choice == "7":
                print("\nGoodbye!")
                break

            else:
                print("Invalid option, please choose 1-7.")

        except (DuplicateTagIDError, BirdNotFoundError, ValueError,
                AttributeError) as e:
            print(f"\n⚠ Error: {e}")


if __name__ == "__main__":
    run_ui()