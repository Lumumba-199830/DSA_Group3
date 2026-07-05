"""
Poultry Farm Management System — main.py (INTEGRATION FILE)
----------------------------------------------------------------
This file ties every teammate's module into one working system.

HOW IT WORKS:
  For each teammate's module, this file FIRST tries to import their
  REAL file. If that import fails (file missing, wrong name, not
  finished yet, contains an error), it automatically falls back to a
  STUB placeholder so the program still runs end-to-end.

  A message prints at startup telling you exactly which parts are
  REAL and which are still STUBS — so you always know the true state
  of the project before a demo or presentation.

FILES THIS EXPECTS TO FIND IN THE SAME FOLDER:
  backend.py         -> your file: Bird, FlockRegistry
  SystemSearch.py     -> Search System teammate: HashTable class
                          (methods: insert(bird), search(tag_id), delete(tag_id))
  sorting_module.py   -> Sorting teammate: sort_flock(flock, criteria)

NOTE: The Health Alert System (min-heap) module has been removed from
this integration file since nobody on the team is currently building
it. If someone picks it up later, this file can be extended again.

IMPORTANT SHARED RULE FOR THE WHOLE GROUP:
  Only ONE Bird class should exist in the entire project — the one in
  backend.py. Every other file must IMPORT it, never redefine it.
  Field names to use everywhere: tag_id, breed, age_weeks, weight_kg,
  egg_count, health_status.
"""

# ---------------------------------------------------------------------
# 1. YOUR MODULE — REQUIRED (the program cannot run without this)
# ---------------------------------------------------------------------

from backend import (
    FlockRegistry,
    Bird,
    DuplicateTagIDError,
    BirdNotFoundError,
)


# ---------------------------------------------------------------------
# 2. TEAMMATES' MODULES — OPTIONAL (fall back to stubs if not ready)
# ---------------------------------------------------------------------

# ---- Search System (Hash Table) --------------------------------------
try:
    from SystemSearch import HashTable as RealHashTable
    HASH_TABLE_IS_REAL = True
except Exception as e:
    HASH_TABLE_IS_REAL = False
    _hash_table_import_error = e


# ---- Sorting Module (Merge Sort + Quick Sort) ------------------------
try:
    from SortingModule import sort_flock as real_sort_flock
    SORTING_IS_REAL = True
except Exception as e:
    SORTING_IS_REAL = False
    _sorting_import_error = e


# ---------------------------------------------------------------------
# 3. STUB FALLBACKS — used only when a real module isn't available yet
# ---------------------------------------------------------------------

class StubHashTable:
    """Fallback used only if hash_table.py is missing or broken."""

    def __init__(self):
        self._table = {}

    def insert(self, bird):
        self._table[bird.tag_id] = bird

    def search(self, tag_id):
        return self._table.get(tag_id)

    def delete(self, tag_id):
        return self._table.pop(tag_id, None) is not None


class StubSorting:
    """Fallback used only if sorting_module.py is missing or broken."""

    ATTRIBUTE_MAP = {
        "weight_kg": "weight_kg",
        "age_weeks": "age_weeks",
        "egg_count": "egg_count",
    }

    def sort_flock(self, flock, criteria):
        key = self.ATTRIBUTE_MAP.get(criteria, criteria)
        return sorted(flock, key=lambda bird: getattr(bird, key))


# ---------------------------------------------------------------------
# 4. INTEGRATION LAYER — the "glue" that connects every module
# ---------------------------------------------------------------------

class PoultryFarmSystem:
    """
    Owns ONE FlockRegistry and keeps every other module in sync with it.
    This is the object the whole team's UI and demos should use.
    """

    def __init__(self):
        self.registry = FlockRegistry()
        self.hash_table = RealHashTable() if HASH_TABLE_IS_REAL else StubHashTable()

    # ---- CREATE -----------------------------------------------------
    def add_bird(self, bird: Bird) -> None:
        self.registry.add_bird(bird)          # array (source of truth)
        self.hash_table.insert(bird)          # keep hash table in sync

    # ---- READ (fast path via hash table) -----------------------------
    def search_bird(self, tag_id: str):
        bird = self.hash_table.search(tag_id)
        if bird is not None:
            return bird
        # Fall back to the registry's own linear search if the hash
        # table doesn't have it (keeps the system correct even if the
        # two ever drift out of sync)
        return self.registry.find_bird(tag_id)

    # ---- UPDATE -------------------------------------------------------
    def edit_bird(self, tag_id: str, **fields) -> Bird:
        updated = self.registry.edit_bird(tag_id, **fields)
        # Hash table's insert() rejects duplicates, so remove + re-insert
        self.hash_table.delete(tag_id)
        self.hash_table.insert(updated)
        return updated

    # ---- DELETE ---------------------------------------------------------
    def delete_bird(self, tag_id: str) -> Bird:
        removed = self.registry.delete_bird(tag_id)
        self.hash_table.delete(tag_id)
        return removed

    # ---- SORT (delegates to the sorting module or its stub) -------------
    def sorted_flock(self, criteria: str):
        flock = self.registry.get_all_birds()  # always sort a COPY
        if SORTING_IS_REAL:
            return real_sort_flock(flock, criteria)
        return StubSorting().sort_flock(flock, criteria)


# ---------------------------------------------------------------------
# 5. STARTUP REPORT — shows which modules are real vs stubbed
# ---------------------------------------------------------------------

def print_integration_status():
    print("=" * 60)
    print("POULTRY FARM MANAGEMENT SYSTEM — MODULE STATUS".center(60))
    print("=" * 60)
    print(f"  Flock Registry (backend.py) ..... LOADED (required)")
    print(f"  Hash Table ....................... "
          f"{'REAL MODULE' if HASH_TABLE_IS_REAL else 'STUB (hash_table.py not found/broken)'}")
    if not HASH_TABLE_IS_REAL:
        print(f"      reason: {_hash_table_import_error}")
    print(f"  Sorting Module ................... "
          f"{'REAL MODULE' if SORTING_IS_REAL else 'STUB (sorting_module.py not found/broken)'}")
    if not SORTING_IS_REAL:
        print(f"      reason: {_sorting_import_error}")
    print("=" * 60)


# ---------------------------------------------------------------------
# 6. DEMO — proves the whole pipeline works end-to-end
# ---------------------------------------------------------------------

def demo():
    system = PoultryFarmSystem()

    system.add_bird(Bird("PF-001", "Broiler", 6, 2.1, 0, "Healthy"))
    system.add_bird(Bird("PF-002", "Layer", 10, 1.8, 120, "Sick"))
    system.add_bird(Bird("PF-003", "Kienyeji", 4, 1.2, 10, "Critical"))

    print("\n-- All birds (registry) --")
    for b in system.registry.get_all_birds():
        print(b)

    print("\n-- Search PF-002 --")
    print(system.search_bird("PF-002"))

    print("\n-- Sorted by weight_kg --")
    for b in system.sorted_flock("weight_kg"):
        print(b)

    system.edit_bird("PF-001", health_status="Critical")
    print("\n-- PF-001 updated to Critical --")
    print(system.search_bird("PF-001"))

    system.delete_bird("PF-003")
    print("\n-- After deleting PF-003 --")
    for b in system.registry.get_all_birds():
        print(b)


if __name__ == "__main__":
    print_integration_status()
    print("\n1. Run demo (automatic test)")
    print("2. Run interactive menu (add/search/sort birds yourself)")
    choice = input("\nChoose 1 or 2: ").strip()

    if choice == "2":
        from UI import run_ui
        system = PoultryFarmSystem()
        run_ui(system)
    else:
        demo()