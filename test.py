def quick_sort(nums, left, right):
    if left >= right:
        return
    pivot = nums[(left + right) // 2]
    i, j = left, right
    while i <= j:
        while nums[i] < pivot:    # 左边找一个 >= pivot 的
            i += 1
        while nums[j] > pivot:    # 右边找一个 <= pivot 的
            j -= 1
        if i <= j:
            nums[i], nums[j] = nums[j], nums[i]  # 交换
            i += 1
            j -= 1
    quick_sort(nums, left, j)     # 排左半
    quick_sort(nums, i, right)    # 排右半