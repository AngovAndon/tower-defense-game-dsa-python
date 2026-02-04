def quick_sort(towers):
    """Custom Quick Sort for objects with a .cost attribute (ascending by cost)."""
    if len(towers) <= 1:
        return towers

    pivot = towers[len(towers) // 2].cost
    left = [t for t in towers if t.cost < pivot]
    mid = [t for t in towers if t.cost == pivot]
    right = [t for t in towers if t.cost > pivot]

    return quick_sort(left) + mid + quick_sort(right)


def binary_search_max_affordable_index(towers, budget):
    """Binary-search variant: returns the rightmost index with cost <= budget.

    Assumes `towers` is sorted ascending by .cost.
    Returns -1 if nothing is affordable.
    """
    low, high = 0, len(towers) - 1
    ans = -1
    while low <= high:
        mid = (low + high) // 2
        if towers[mid].cost <= budget:
            ans = mid
            low = mid + 1  # try to find a higher affordable cost
        else:
            high = mid - 1
    return ans


def insertion_sort_desc(values):
    """Custom insertion sort (descending) for a list of numbers."""
    arr = list(values)  # copy
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        # Move smaller elements to the right to make space for `key`
        while j >= 0 and arr[j] < key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr
