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


# ---- Health Alert System (Min-Heap) ----------------------------------
try:
    from HealthAlertMinHeap import HealthAlertMinHeap as RealHealthAlertHeap
    MIN_HEAP_IS_REAL = True
except Exception as e:
    MIN_HEAP_IS_REAL = False
    _min_heap_import_error = e


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


class StubHealthAlertHeap:
    """Fallback used only if min_heap.py is missing or broken."""

    _SEVERITY = {"Critical": 0, "Sick": 1, "Healthy": 2}

    def __init__(self):
        self._items = []

    def insert(self, bird):
        if bird.health_status in ("Sick", "Critical"):
            self._items.append(bird)

    def extract_min(self):
        if not self._items:
            return None
        self._items.sort(key=lambda b: self._SEVERITY.get(b.health_status, 3))
        return self._items.pop(0)

    def peek(self):
        if not self._items:
            return None
        return min(self._items, key=lambda b: self._SEVERITY.get(b.health_status, 3))

    def get_all_sorted(self):
        return sorted(self._items, key=lambda b: self._SEVERITY.get(b.health_status, 3))


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
        self.health_alerts = RealHealthAlertHeap() if MIN_HEAP_IS_REAL else StubHealthAlertHeap()

    # ---- CREATE -----------------------------------------------------
    def add_bird(self, bird: Bird) -> None:
        self.registry.add_bird(bird)          # array (source of truth)
        self.hash_table.insert(bird)          # keep hash table in sync
        self.health_alerts.insert(bird)       # flag for health alerts if Sick/Critical

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
        self.health_alerts.insert(updated)
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

    # ---- HEALTH ALERTS ----------------------------------------------------
    def most_urgent_bird(self):
        return self.health_alerts.peek()

    def all_health_alerts(self):
        return self.health_alerts.get_all_sorted()


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
    print(f"  Health Alert Heap ................. "
          f"{'REAL MODULE' if MIN_HEAP_IS_REAL else 'STUB (min_heap.py not found/broken)'}")
    if not MIN_HEAP_IS_REAL:
        print(f"      reason: {_min_heap_import_error}")
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

    print("\n-- Most urgent health alert --")
    print(system.most_urgent_bird())

    system.edit_bird("PF-001", health_status="Critical")
    print("\n-- Most urgent after PF-001 turns Critical --")
    print(system.most_urgent_bird())

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