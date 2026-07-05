# =====================================================================
# MODULE: Sorting Module (Merge Sort & Quick Sort)
# DELIVERABLE: Sort poultry records by weight, age, and egg count
# =====================================================================

# 1. MERGE SORT (Used for Stable Sorting: Age and Egg Count)
def merge_sort_poultry(flock, key):
    """
    Sorts the flock by age or egg_count using the Merge Sort algorithm.
    Guarantees O(n log n) time complexity and maintains structural stability.
    """
    flock_copy = list(flock)  # Create a shallow copy to protect original registry array
    
    if len(flock_copy) <= 1:
        return flock_copy
    
    mid = len(flock_copy) // 2
    left_half = flock_copy[:mid]
    right_half = flock_copy[mid:]
    
    left_sorted = merge_sort_poultry(left_half, key)
    right_sorted = merge_sort_poultry(right_half, key)
    
    return _merge(left_sorted, right_sorted, key)

def _merge(left, right, key):
    sorted_list = []
    i = j = 0
    
    while i < len(left) and j < len(right):
        if left[i][key] <= right[j][key]:
            sorted_list.append(left[i])
            i += 1
        else:
            sorted_list.append(right[j])
            j += 1
            
    sorted_list.extend(left[i:])
    sorted_list.extend(right[j:])
    return sorted_list


# 2. QUICK SORT (Used for Fast Market Sorting: Weight)
def quick_sort_poultry(flock, key="weight"):
    """
    Sorts the flock by weight using the Quick Sort algorithm.
    Sorts quickly with an average time complexity of O(n log n).
    """
    flock_copy = list(flock)  # Create a shallow copy to protect original registry array
    
    if len(flock_copy) <= 1:
        return flock_copy
    
    # Using the last element as the pivot as outlined in the project proposal
    pivot_bird = flock_copy[-1]
    pivot_weight = pivot_bird[key]
    
    left_side = [bird for bird in flock_copy[:-1] if bird[key] <= pivot_weight]
    right_side = [bird for bird in flock_copy[:-1] if bird[key] > pivot_weight]
    
    return quick_sort_poultry(left_side, key) + [pivot_bird] + quick_sort_poultry(right_side, key)


# 3. THE CENTRAL CONTROL FUNCTION (For Frontend/UI Integration)
def sort_flock(flock, criteria):
    """
    The main driver function that your team's UI module will call.
    Accepts criteria: 'weight', 'age', or 'egg_count'
    """
    if criteria == "weight":
        print(f"[Sorting Module] Executing Quick Sort on attribute: {criteria}")
        return quick_sort_poultry(flock, key="weight")
    
    elif criteria in ["age", "egg_count"]:
        print(f"[Sorting Module] Executing Merge Sort on attribute: {criteria}")
        return merge_sort_poultry(flock, key=criteria)
    
    else:
        print(f"[Sorting Error] Invalid sorting criteria: {criteria}")
        return flock