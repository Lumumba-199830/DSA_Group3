# =====================================================================
# MODULE: Health Alert System (Min-Heap Priority Queue)
# DELIVERABLE: Insert, extract-min, peek operations
# =====================================================================
#
# NOTE: This module operates on Bird objects from backend.py — it does
# NOT define its own record class. Priority is computed with a small
# helper function instead of being stored on the Bird itself, so we
# never have to modify the shared Bird class for this one module's need.
#
# Priority order (lower number = more urgent = comes out of heap first):
#   Critical -> 1
#   Sick     -> 2
#   Healthy  -> excluded entirely (not inserted, not alerted on)

from backend import Bird


def _priority(bird):
    """
    Returns the urgency score for a bird, or None if it doesn't need
    a health alert at all (Healthy birds are excluded).
    """
    if bird.health_status == "Critical":
        return 1
    elif bird.health_status == "Sick":
        return 2
    else:
        return None


class HealthAlertMinHeap:
    def __init__(self):
        self.heap = []

    def insert(self, bird):
        # Prevent healthy birds from cluttering the heap
        priority = _priority(bird)
        if priority is None:
            return

        self.heap.append(bird)
        self._bubble_up(len(self.heap) - 1)

    def extract_min(self):
        if len(self.heap) == 0:
            return None

        if len(self.heap) == 1:
            return self.heap.pop()

        # Swap the root with the last element
        min_bird = self.heap[0]
        self.heap[0] = self.heap.pop()

        # Re-sort the tree downwards
        self._sink_down(0)
        return min_bird

    def peek(self):
        if len(self.heap) == 0:
            return None
        return self.heap[0]

    def get_all_sorted(self):
        """
        Returns EVERY bird currently in the heap, ordered from most
        urgent (Critical) to least urgent (Sick), WITHOUT removing
        anything from the heap or changing its internal structure.

        This does not use extract_min() repeatedly, since that would
        empty the actual heap. Instead it sorts a separate COPY of the
        heap's contents, so the real heap stays intact for future
        insert()/extract_min()/peek() calls.
        """
        return sorted(self.heap, key=lambda bird: _priority(bird))

    def _bubble_up(self, index):
        parent_index = (index - 1) // 2

        while index > 0 and _priority(self.heap[index]) < _priority(self.heap[parent_index]):
            # Swap the child and parent
            self.heap[index], self.heap[parent_index] = self.heap[parent_index], self.heap[index]

            # Move the pointers up the tree
            index = parent_index
            parent_index = (index - 1) // 2

    def _sink_down(self, index):
        length = len(self.heap)

        while True:
            left_child_index = 2 * index + 1
            right_child_index = 2 * index + 2
            smallest = index

            # Check if left child is smaller than current smallest
            if left_child_index < length and _priority(self.heap[left_child_index]) < _priority(self.heap[smallest]):
                smallest = left_child_index

            # Check if right child is smaller than current smallest
            if right_child_index < length and _priority(self.heap[right_child_index]) < _priority(self.heap[smallest]):
                smallest = right_child_index

            # If the smallest is no longer the parent, swap them
            if smallest != index:
                self.heap[index], self.heap[smallest] = self.heap[smallest], self.heap[index]
                index = smallest
            else:
                break


# Small smoke test — only runs if this file is executed directly
if __name__ == "__main__":
    heap = HealthAlertMinHeap()

    heap.insert(Bird("PF-001", "Broiler", 6, 2.1, 0, "Healthy"))   # excluded
    heap.insert(Bird("PF-002", "Layer", 10, 1.8, 120, "Sick"))
    heap.insert(Bird("PF-003", "Kienyeji", 4, 1.2, 10, "Critical"))

    print("Most urgent (peek):")
    print(heap.peek())

    print("\nAll alerts, most urgent first (get_all_sorted):")
    for b in heap.get_all_sorted():
        print(b)

    print("\nExtracting in priority order:")
    while True:
        bird = heap.extract_min()
        if bird is None:
            break
        print(bird)