task_list = [1, 2, 3, 45, 356, 569, 600, 705, 923]


def search(number: int) -> bool:
    left, right = 0, len(task_list) - 1

    while left <= right:
        mid = (left + right) // 2
        if number == task_list[mid]:
            return True
        if number < task_list[mid]:
            right = mid - 1
        else:
            left = mid + 1
    return False

