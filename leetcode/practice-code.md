两数之和
```bash
给定一个数组 nums 和一个目标值 target 找出数组中两个数 它们的和等于 target 返回这两个数的索引

class Solution:
    def twoSum(self, nums: list[int], target: int) -> list[int]:
        hash_map = {}  # 存储值到索引的映射
        
        for i, num in enumerate(nums):
            complement = target - num
            
            if complement in hash_map:
                return [hash_map[complement], i]
            
            hash_map[num] = i
        
        return []  # 题目保证有解，这行不会执行

```

字母异位词分组
```bash
给定一个字符串数组，将字母异位词分组在一起。
字母异位词：字母相同，顺序不同的字符串。

class Solution:
    def groupAnagrams(self, strs: list[str]) -> list[list[str]]:
        hash_map = {}  # key: 排序后的字符串, value: 原字符串列表
        
        for s in strs:
            key = "".join(sorted(s))
            
            if key not in hash_map:
                hash_map[key] = []
            
            hash_map[key].append(s)
        
        return list(hash_map.values())
```

最长连续序列
```bash
给定一个未排序的整数数组 nums，找出数字连续的最长序列长度。
要求时间复杂度 O(n)。

class Solution:
    def longestConsecutive(self, nums: list[int]) -> int:
        num_set = set(nums)
        max_len = 0
        
        for num in num_set:
            # 只从序列开头开始找
            if num - 1 not in num_set:
                current_num = num
                current_len = 1
                
                # 往后找连续的数
                while current_num + 1 in num_set:
                    current_num += 1
                    current_len += 1
                
                max_len = max(max_len, current_len)
        
        return max_len

```

移动零
```bash
给定一个数组 nums，把所有 0 移到数组末尾，同时保持非零元素的相对顺序。
class Solution:
    def moveZeroes(self, nums: list[int]) -> None:
        j = 0  # 慢指针：指向下一个非零元素的位置
        
        for i in range(len(nums)):  # 快指针：遍历
            if nums[i] != 0:
                nums[j] = nums[i]
                j += 1
        
        # 把后面的位置都填 0
        for i in range(j, len(nums)):
            nums[i] = 0
            
```

盛最多水的容器
```bash
给定一个整数数组 height，每个元素代表一个高度。找出两条线，使得它们与 x 轴构成的容器能容纳最多的水。
class Solution:
    def maxArea(self, height: list[int]) -> int:
        left, right = 0, len(height) - 1
        max_area = 0
        
        while left < right:
            # 计算当前容量
            area = min(height[left], height[right]) * (right - left)
            max_area = max(max_area, area)
            
            # 移动较小的指针
            if height[left] < height[right]:
                left += 1
            else:
                right -= 1
        
        return max_area
```

三数之和
```bash
给定一个数组 nums，找出所有不重复的三元组 [nums[i], nums[j], nums[k]]，使得它们的和为 0。

class Solution:
    def threeSum(self, nums: list[int]) -> list[list[int]]:
        nums.sort()
        result = []
        n = len(nums)
        
        for i in range(n - 2):
            # 跳过重复的第一个数
            if i > 0 and nums[i] == nums[i - 1]:
                continue
            
            # 如果最小的三个数都大于0，后面不可能有解
            if nums[i] + nums[i + 1] + nums[i + 2] > 0:
                break
            
            # 如果最大的三个数都小于0，跳过
            if nums[i] + nums[n - 2] + nums[n - 1] < 0:
                continue
            
            left, right = i + 1, n - 1
            target = -nums[i]
            
            while left < right:
                total = nums[left] + nums[right]
                
                if total == target:
                    result.append([nums[i], nums[left], nums[right]])
                    # 跳过重复
                    while left < right and nums[left] == nums[left + 1]:
                        left += 1
                    while left < right and nums[right] == nums[right - 1]:
                        right -= 1
                    left += 1
                    right -= 1
                elif total < target:
                    left += 1
                else:
                    right -= 1
        
        return result
```

无重复字符的最长子串
```bash
给定一个字符串 s，找出其中不含有重复字符的最长子串的长度。

class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        char_index = {}  # 字符 → 最后出现的位置 ，  相当于窗口内的字符出现的位置记录
        left = 0
        max_len = 0
        
        for right, char in enumerate(s):
            # 如果字符重复且在窗口内，移动左指针
            if char in char_index and char_index[char] >= left:
                left = char_index[char] + 1
            
            # 更新字符位置
            char_index[char] = right
            
            # 更新最大长度
            max_len = max(max_len, right - left + 1)
        
        return max_len

```


找到字符串中所有字母异位词
```bash
给定两个字符串 s 和 p，找出 s 中所有 p 的字母异位词的起始索引。
输入: s = "cbaebabacd", p = "abc"
输出: [0, 6]
解释:
- s[0:3] = "cba" 是 "abc" 的异位词
- s[6:9] = "bac" 是 "abc" 的异位词


class Solution:
    def findAnagrams(self, s: str, p: str) -> list[int]:
        if len(s) < len(p):
            return []
        
        p_count = [0] * 26
        window_count = [0] * 26
        
        # 统计 p 的字符计数
        for c in p:
            p_count[ord(c) - ord('a')] += 1
        
        result = []
        
        # 初始化窗口
        for i in range(len(p)):
            window_count[ord(s[i]) - ord('a')] += 1
        
        # 检查初始窗口
        if window_count == p_count:
            result.append(0)
        
        # 滑动窗口
        for i in range(len(p), len(s)):
            # 移出左边的字符
            left_char = s[i - len(p)]
            window_count[ord(left_char) - ord('a')] -= 1
            
            # 移入右边的字符
            right_char = s[i]
            window_count[ord(right_char) - ord('a')] += 1
            
            # 检查是否匹配
            if window_count == p_count:
                result.append(i - len(p) + 1)
        
        return result

```

和为K的子数组
```bash
给定一个整数数组 nums 和一个整数 k，找出该数组中和为 k 的连续子数组的个数。

class Solution:
    def subarraySum(self, nums: list[int], k: int) -> int:
        prefix_sum_count = {0: 1}  # 前缀和 → 出现次数
        prefix_sum = 0
        count = 0
        
        for num in nums:
            prefix_sum += num
            
            # 检查是否有 prefix_sum - k
            if (prefix_sum - k) in prefix_sum_count:
                count += prefix_sum_count[prefix_sum - k]
            
            # 更新前缀和计数
            prefix_sum_count[prefix_sum] = prefix_sum_count.get(prefix_sum, 0) + 1
        
        return count

```


最大子数组之和
```bash
给定一个整数数组 nums，找出一个连续子数组，使其和最大。
class Solution:
    def maxSubArray(self, nums: list[int]) -> int:
        max_sum = nums[0]
        current_sum = nums[0]
        
        for i in range(1, len(nums)):
            # 要么重新开始，要么累加
            current_sum = max(nums[i], current_sum + nums[i])
            max_sum = max(max_sum, current_sum)
        
        return max_sum

```

合并区间
```bash
给定一个区间的集合 intervals，合并所有重叠的区间，返回一个不重叠的区间列表。

class Solution:
    def merge(self, intervals: list[list[int]]) -> list[list[int]]:
        if not intervals:
            return []
        
        # 按起点排序
        intervals.sort(key=lambda x: x[0])
        
        result = [intervals[0]]
        
        for interval in intervals[1:]:
            last = result[-1]
            
            # 如果重叠（当前起点 <= 上一个终点）
            if interval[0] <= last[1]:
                # 合并：更新终点为较大的那个
                last[1] = max(last[1], interval[1])
            else:
                # 不重叠，加入结果
                result.append(interval)
        
        return result
```

轮转数组
```bash
给定一个数组 nums 和一个整数 k，将数组中的元素向右移动 k 步。

class Solution:
    def rotate(self, nums: list[int], k: int) -> None:
        n = len(nums)
        k %= n  # 处理 k > n 的情况
        
        # 翻转整个数组
        self.reverse(nums, 0, n - 1)
        # 翻转前 k 个
        self.reverse(nums, 0, k - 1)
        # 翻转剩余
        self.reverse(nums, k, n - 1)
    
    def reverse(self, nums: list[int], left: int, right: int) -> None:
        while left < right:
            nums[left], nums[right] = nums[right], nums[left]
            left += 1
            right -= 1
```

除了自身以外数组的乘积
```bash
给定一个整数数组 nums，返回一个数组 answer，其中 answer[i] 等于 nums 中除 nums[i] 之外各元素的乘积
输入: nums = [1, 2, 3, 4]
输出: [24, 12, 8, 6]

class Solution:
    def productExceptSelf(self, nums: list[int]) -> list[int]:
        n = len(nums)
        answer = [1] * n
        
        # 计算前缀积
        left = 1
        for i in range(n):
            answer[i] = left
            left *= nums[i]
        
        # 计算后缀积，直接乘到 answer 上
        right = 1
        for i in range(n - 1, -1, -1):
            answer[i] *= right
            right *= nums[i]
        
        return answer
        
```

矩阵置零
```bash
给定一个 m × n 矩阵，如果某个元素是 0，则将其所在行和列的所有元素都置为 0。

class Solution:
    def setZeroes(self, matrix: list[list[int]]) -> None:
        m, n = len(matrix), len(matrix[0])
        first_row_zero = any(matrix[0][j] == 0 for j in range(n))
        first_col_zero = any(matrix[i][0] == 0 for i in range(m))
        
        # 用第一行和第一列作为标记
        for i in range(1, m):
            for j in range(1, n):
                if matrix[i][j] == 0:
                    matrix[i][0] = 0
                    matrix[0][j] = 0
        
        # 根据标记置零
        for i in range(1, m):
            for j in range(1, n):
                if matrix[i][0] == 0 or matrix[0][j] == 0:
                    matrix[i][j] = 0
        
        # 处理第一行
        if first_row_zero:
            for j in range(n):
                matrix[0][j] = 0
        
        # 处理第一列
        if first_col_zero:
            for i in range(m):
                matrix[i][0] = 0

```

螺旋矩阵
```bash
给定一个 m × n 矩阵，按顺时针螺旋顺序返回所有元素。

class Solution:
    def spiralOrder(self, matrix: list[list[int]]) -> list[int]:
        if not matrix:
            return []
        
        m, n = len(matrix), len(matrix[0])
        top, bottom = 0, m - 1
        left, right = 0, n - 1
        result = []
        
        while top <= bottom and left <= right:
            # 从左到右
            for j in range(left, right + 1):
                result.append(matrix[top][j])
            top += 1
            
            # 从上到下
            for i in range(top, bottom + 1):
                result.append(matrix[i][right])
            right -= 1
            
            # 从右到左
            if top <= bottom:
                for j in range(right, left - 1, -1):
                    result.append(matrix[bottom][j])
                bottom -= 1
            
            # 从下到上
            if left <= right:
                for i in range(bottom, top - 1, -1):
                    result.append(matrix[i][left])
                left += 1
        
        return result
```

旋转图像
```bash
给定一个 n × n 的二维矩阵，将其顺时针旋转 90 度。

class Solution:
    def rotate(self, matrix: list[list[int]]) -> None:
        n = len(matrix)
        
        # 转置
        for i in range(n):
            for j in range(i, n):
                matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]
        
        # 水平翻转
        for i in range(n):
            matrix[i].reverse()

```

搜索二维矩阵II
```bash
给定一个 m × n 矩阵，每行从左到右递增，每列从上到下递增。判断目标值是否存在。

class Solution:
    def searchMatrix(self, matrix: list[list[int]], target: int) -> bool:
        if not matrix or not matrix[0]:
            return False
        
        m, n = len(matrix), len(matrix[0])
        row, col = 0, n - 1  # 从右上角开始
        
        while row < m and col >= 0:
            if matrix[row][col] == target:
                return True
            elif matrix[row][col] > target:
                col -= 1  # 往左
            else:
                row += 1  # 往下
        
        return False

```


相交链表
```bash
给定两个单链表，找出它们的第一个相交节点。如果不相交，返回 null。

class ListNode:
    def __init__(self, x):
        self.val = x
        self.next = None

class Solution:
    def getIntersectionNode(self, headA: ListNode, headB: ListNode) -> ListNode:
        if not headA or not headB:
            return None
        
        pA, pB = headA, headB
        
        while pA != pB:
            pA = pA.next if pA else headB
            pB = pB.next if pB else headA
        
        return pA
```

反转链表
```bash
给定一个单链表，将其翻转。

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

class Solution:
    def reverseList(self, head: ListNode) -> ListNode:
        prev = None
        curr = head
        
        while curr:
            next_node = curr.next  # 保存下一个节点
            curr.next = prev       # 翻转指针
            prev = curr            # prev 向后移
            curr = next_node       # curr 向后移
        
        return prev
```

回文链表
```bash
给定一个单链表，判断它是否是回文链表。


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

class Solution:
    def isPalindrome(self, head: ListNode) -> bool:
        if not head or not head.next:
            return True
        
        # 1. 找中点
        slow, fast = head, head
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next
        
        # 2. 翻转后半部分
        prev = None
        curr = slow
        while curr:
            next_node = curr.next
            curr.next = prev
            prev = curr
            curr = next_node
        
        # 3. 比较
        left, right = head, prev
        result = True
        while right:
            if left.val != right.val:
                result = False
                break
            left = left.next
            right = right.next
        
        # 4. 恢复链表（可选）
        # ... 翻转回去
        
        return result
```
环形链表
```bash
给定一个链表，判断它是否有环。

class ListNode:
    def __init__(self, x):
        self.val = x
        self.next = None

class Solution:
    def hasCycle(self, head: ListNode) -> bool:
        if not head or not head.next:
            return False
        
        slow = head
        fast = head.next
        
        while slow != fast:
            if not fast or not fast.next:
                return False
            slow = slow.next
            fast = fast.next.next
        
        return True

```
环形链表2
```bash
给定一个链表，返回环的起始节点。如果没有环，返回 null。

class ListNode:
    def __init__(self, x):
        self.val = x
        self.next = None

class Solution:
    def detectCycle(self, head: ListNode) -> ListNode:
        if not head or not head.next:
            return None
        
        slow, fast = head, head
        
        # 1. 找相遇点
        while True:
            if not fast or not fast.next:
                return None
            slow = slow.next
            fast = fast.next.next
            if slow == fast:
                break
        
        # 2. 找环起点
        slow = head
        while slow != fast:
            slow = slow.next
            fast = fast.next
        
        return slow

```

合并两个有序链表
```bash
给定两个升序链表，把它们合并成一个新的升序链表。

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

class Solution:
    def mergeTwoLists(self, l1: ListNode, l2: ListNode) -> ListNode:
        dummy = ListNode(0)  # 哨兵节点
        curr = dummy
        
        while l1 and l2:
            if l1.val <= l2.val:
                curr.next = l1
                l1 = l1.next
            else:
                curr.next = l2
                l2 = l2.next
            curr = curr.next
        
        # 接上剩余的部分
        curr.next = l1 if l1 else l2
        
        return dummy.next
```


两数相加
```bash
给定两个非空链表，表示两个非负整数。每个数字按逆序存储在链表中，求它们的和并以链表形式返回。
输入: l1 = 2 → 4 → 3, l2 = 5 → 6 → 4
输出: 7 → 0 → 8
解释: 342 + 465 = 807


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

class Solution:
    def addTwoNumbers(self, l1: ListNode, l2: ListNode) -> ListNode:
        dummy = ListNode(0)  # 哨兵节点
        curr = dummy
        carry = 0
        
        while l1 or l2 or carry:
            # 获取当前位的值
            val1 = l1.val if l1 else 0
            val2 = l2.val if l2 else 0
            
            # 计算和与进位
            total = val1 + val2 + carry
            carry = total // 10
            digit = total % 10
            
            # 创建新节点
            curr.next = ListNode(digit)
            curr = curr.next
            
            # 移动指针
            if l1:
                l1 = l1.next
            if l2:
                l2 = l2.next
        
        return dummy.next
```
删除链表的倒数第N个节点
```bash
给定一个链表，删除链表的倒数第 n 个节点，返回链表的头节点。

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

class Solution:
    def removeNthFromEnd(self, head: ListNode, n: int) -> ListNode:
        dummy = ListNode(0)  # 哨兵节点
        dummy.next = head
        fast, slow = dummy, dummy
        
        # 快指针先走 n 步
        for _ in range(n):
            fast = fast.next
        
        # 快慢指针同时走
        while fast.next:
            fast = fast.next
            slow = slow.next
        
        # 删除节点
        slow.next = slow.next.next
        
        return dummy.next

```
两两交换链表中的节点
```bash
给定一个链表，两两交换其中相邻的节点，返回交换后的链表。


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

class Solution:
    def swapPairs(self, head: ListNode) -> ListNode:
        dummy = ListNode(0)  # 哨兵节点
        dummy.next = head
        prev = dummy
        
        while prev.next and prev.next.next:
            # 要交换的两个节点
            first = prev.next
            second = prev.next.next
            
            # 交换
            prev.next = second
            first.next = second.next
            second.next = first
            
            # 移动 prev
            prev = first
        
        return dummy.next


```

随机链表的复制
```bash
给定一个链表，每个节点除了 next 指针外，还有一个 random 指针（可以指向链表中的任意节点或 null）。深拷贝这个链表。
class Node:
    def __init__(self, x, next=None, random=None):
        self.val = int(x)
        self.next = next
        self.random = random

class Solution:
    def copyRandomList(self, head: Node) -> Node:
        if not head:
            return None
        
        # 第一遍：创建新节点，建立映射
        old_to_new = {}
        curr = head
        while curr:
            old_to_new[curr] = Node(curr.val)
            curr = curr.next
        
        # 第二遍：设置 next 和 random
        curr = head
        while curr:
            new_node = old_to_new[curr]
            new_node.next = old_to_new.get(curr.next)
            new_node.random = old_to_new.get(curr.random)
            curr = curr.next
        
        return old_to_new[head]
```

排序链表
```bash
给定一个链表，将其按升序排序。

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

class Solution:
    def sortList(self, head: ListNode) -> ListNode:
        if not head or not head.next:
            return head
        
        # 1. 找中点
        slow, fast = head, head.next
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next
        
        # 2. 断开链表
        mid = slow.next
        slow.next = None
        
        # 3. 递归排序
        left = self.sortList(head)
        right = self.sortList(mid)
        
        # 4. 合并
        return self.merge(left, right)
    
    def merge(self, l1: ListNode, l2: ListNode) -> ListNode:
        dummy = ListNode(0)
        curr = dummy
        
        while l1 and l2:
            if l1.val <= l2.val:
                curr.next = l1
                l1 = l1.next
            else:
                curr.next = l2
                l2 = l2.next
            curr = curr.next
        
        curr.next = l1 if l1 else l2
        return dummy.next
```
LRU缓存
```bash
设计一个 LRU（最近最少使用）缓存，支持 get 和 put 操作，时间复杂度 O(1)。

get(key)：获取 key 的值，不存在返回 -1
put(key, value)：插入或更新 key，如果容量满了，删除最近最少使用的项


class Node:
    def __init__(self, key=0, val=0):
        self.key = key
        self.val = val
        self.prev = None
        self.next = None

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}  # key → Node
        self.head = Node()  # 哨兵头节点
        self.tail = Node()  # 哨兵尾节点
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _remove_node(self, node: Node):
        """从链表中移除节点"""
        node.prev.next = node.next
        node.next.prev = node.prev
    
    def _add_to_head(self, node: Node):
        """添加节点到头部"""
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node
    
    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        node = self.cache[key]
        self._remove_node(node)
        self._add_to_head(node)
        return node.val
    
    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            node = self.cache[key]
            node.val = value
            self._remove_node(node)
            self._add_to_head(node)
        else:
            if len(self.cache) >= self.capacity:
                # 删除尾部节点（最近最少使用）
                lru = self.tail.prev
                self._remove_node(lru)
                del self.cache[lru.key]
            
            new_node = Node(key, value)
            self.cache[key] = new_node
            self._add_to_head(new_node)
```


二叉树的中序遍历
```bash
给定二叉树的根节点，返回其中序遍历结果。


class Solution:
    def inorderTraversal(self, root: TreeNode) -> list[int]:
        result = []
        self._inorder(root, result)
        return result
    
    def _inorder(self, node: TreeNode, result: list[int]):
        if not node:
            return
        self._inorder(node.left, result)  # 左
        result.append(node.val)           # 根
        self._inorder(node.right, result) # 右
        
        
class Solution:
    def inorderTraversal(self, root: TreeNode) -> list[int]:
        if not root:
            return []
        return (self.inorderTraversal(root.left) + 
                [root.val] + 
                self.inorderTraversal(root.right))

```


二叉树的最大深度
```bash
给定二叉树的根节点，返回其最大深度。

最大深度 = 从根节点到最远叶子节点的最长路径上的节点数。


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution:
    def maxDepth(self, root: TreeNode) -> int:
        if not root:
            return 0
        left_depth = self.maxDepth(root.left)
        right_depth = self.maxDepth(root.right)
        return max(left_depth, right_depth) + 1


```
翻转二叉树
```bash
给定二叉树的根节点，翻转它，即左右子树交换。

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution:
    def invertTree(self, root: TreeNode) -> TreeNode:
        if not root:
            return None
        
        # 递归翻转左右子树
        left = self.invertTree(root.left)
        right = self.invertTree(root.right)
        
        # 交换
        root.left = right
        root.right = left
        
        return root
        

```
对称二叉树
```bash
给定二叉树的根节点，判断它是否是轴对称的。
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution:
    def isSymmetric(self, root: TreeNode) -> bool:
        if not root:
            return True
        return self._isMirror(root.left, root.right)
    
    def _isMirror(self, left: TreeNode, right: TreeNode) -> bool:
        if not left and not right:
            return True
        if not left or not right:
            return False
        if left.val != right.val:
            return False
        return self._isMirror(left.left, right.right) and self._isMirror(left.right, right.left)
        
```

二叉树的直径
```bash
给定二叉树的根节点，计算其直径长度。
直径 = 任意两个节点之间的最长路径的边数。

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution:
    def diameterOfBinaryTree(self, root: TreeNode) -> int:
        self.max_diameter = 0
        self._depth(root)
        return self.max_diameter
    
    def _depth(self, node: TreeNode) -> int:
        if not node:
            return 0
        
        left_depth = self._depth(node.left)
        right_depth = self._depth(node.right)
        
        # 更新最大直径
        self.max_diameter = max(self.max_diameter, left_depth + right_depth)
        
        # 返回当前节点的深度
        return max(left_depth, right_depth) + 1

```


二叉树的层序遍历
```bash
给定二叉树的根节点，返回其层序遍历结果（逐层，从左到右）。

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

from collections import deque

class Solution:
    def levelOrder(self, root: TreeNode) -> list[list[int]]:
        if not root:
            return []
        
        result = []
        queue = deque([root])
        
        while queue:
            level_size = len(queue) # 根据当前长度只处理这一层长度的树
            level_values = []   # 每一层是一个list
            
            for _ in range(level_size):
                node = queue.popleft()   # 加入这一层的值
                level_values.append(node.val) 
                
                if node.left:       # 加入这一层 的 左右节点
                    queue.append(node.left)
                if node.right:
                    queue.append(node.right)
            
            result.append(level_values)
        
        return result

BFS 是广度优先搜索，用队列实现，按层遍历，适合找最短路径和层序遍历。
队列：先进先出，用 deque 的 append 和 popleft；栈：后进先出，用 list 的 append 和 pop。
```


将有序数组转换为二叉搜索树
```bash
给定一个升序数组，将其转换为一个高度平衡的二叉搜索树（BST）。
高度平衡：左右子树高度差不超过 1。

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution:
    def sortedArrayToBST(self, nums: list[int]) -> TreeNode:
        return self._build(nums, 0, len(nums) - 1)
    
    def _build(self, nums: list[int], left: int, right: int) -> TreeNode:
        if left > right:
            return None
        
        mid = (left + right) // 2
        root = TreeNode(nums[mid])
        
        root.left = self._build(nums, left, mid - 1)
        root.right = self._build(nums, mid + 1, right)
        
        return root

```


验证二叉搜索树
```bash
给定一个二叉树，判断它是否是有效的二叉搜索树（BST）。

BST 定义：

左子树所有节点的值 < 根节点值
右子树所有节点的值 > 根节点值
左右子树也都是 BST


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution:
    def isValidBST(self, root: TreeNode) -> bool:
        return self._validate(root, float('-inf'), float('inf'))
    
    def _validate(self, node: TreeNode, min_val: float, max_val: float) -> bool:
        if not node:
            return True
        
        # 检查当前节点是否在范围内
        if node.val <= min_val or node.val >= max_val:
            return False
        
        # 递归检查左右子树
        return (self._validate(node.left, min_val, node.val) and
                self._validate(node.right, node.val, max_val))
```


二叉搜索树中第K小的元素
```bash
给定二叉搜索树的根节点和一个整数 k，返回第 k 小的元素。

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution:
    def kthSmallest(self, root: TreeNode, k: int) -> int:
        self.count = 0
        self.result = None
        self._inorder(root, k)
        return self.result
    
    def _inorder(self, node: TreeNode, k: int):
        if not node or self.result is not None:
            return
        
        self._inorder(node.left, k)
        
        self.count += 1
        if self.count == k:
            self.result = node.val
            return
        
        self._inorder(node.right, k)
```





199 二叉树的右视图
```bash
from collections import deque
from typing import List, Optional
 
# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
 
class Solution:
    def rightSideView(self, root: Optional[TreeNode]) -> List[int]:
        if not root:
            return []
 
        result = []
        queue = deque([root])
 
        while queue:
            size = len(queue)
 
            for i in range(size):
                node = queue.popleft()
 
                if i == size - 1:
                    result.append(node.val)
 
                if node.left:
                    queue.append(node.left)
                if node.right:
                    queue.append(node.right)
 
        return result
```

114 二叉树展开为链表
```bash
class Solution:
    def flatten(self, root: Optional[TreeNode]) -> None:
        cur = root

        while cur:
            if cur.left:
                prev = cur.left
                while prev.right:
                    prev = prev.right

                prev.right = cur.right
                cur.right = cur.left
                cur.left = None

            cur = cur.right
```

105 从前序与中序遍历序列构造二叉树
```bash
class Solution:
    def buildTree(self, preorder: List[int], inorder: List[int]) -> Optional[TreeNode]:
        index_map = {value: i for i, value in enumerate(inorder)}

        def helper(pre_left, pre_right, in_left, in_right):
            if pre_left > pre_right:
                return None

            root_val = preorder[pre_left]
            root = TreeNode(root_val)

            in_root = index_map[root_val]
            left_size = in_root - in_left

            root.left = helper(pre_left + 1, pre_left + left_size, in_left, in_root - 1)
            root.right = helper(pre_left + left_size + 1, pre_right, in_root + 1, in_right)

            return root

        return helper(0, len(preorder) - 1, 0, len(inorder) - 1)
```

437 路经总和III
```bash
class Solution:
    def pathSum(self, root: Optional[TreeNode], targetSum: int) -> int:
        if not root:
            return 0

        def dfs(node, target):
            if not node:
                return 0

            count = 0
            if node.val == target:
                count += 1

            count += dfs(node.left, target - node.val)
            count += dfs(node.right, target - node.val)

            return count

        return (
            dfs(root, targetSum)
            + self.pathSum(root.left, targetSum)
            + self.pathSum(root.right, targetSum)
        )
          
          
from collections import defaultdict

class Solution:
    def pathSum(self, root: Optional[TreeNode], targetSum: int) -> int:
        prefix = defaultdict(int)
        prefix[0] = 1

        def dfs(node, cur_sum):
            if not node:
                return 0

            cur_sum += node.val
            count = prefix[cur_sum - targetSum]

            prefix[cur_sum] += 1
            count += dfs(node.left, cur_sum)
            count += dfs(node.right, cur_sum)
            prefix[cur_sum] -= 1

            return count

        return dfs(root, 0)

```

236 二叉树的最近公共祖先
```bash
class Solution:
    def lowestCommonAncestor(self, root: 'TreeNode', p: 'TreeNode', q: 'TreeNode') -> 'TreeNode':
        if not root or root == p or root == q:
            return root

        left = self.lowestCommonAncestor(root.left, p, q)
        right = self.lowestCommonAncestor(root.right, p, q)

        if left and right:
            return root

        return left if left else right

```
124 二叉树中的最大路径和
```bash

class Solution:
    def maxPathSum(self, root: Optional[TreeNode]) -> int:
        self.ans = float('-inf')

        def dfs(node):
            if not node:
                return 0

            left = max(dfs(node.left), 0)
            right = max(dfs(node.right), 0)

            self.ans = max(self.ans, node.val + left + right)

            return node.val + max(left, right)

        dfs(root)
        return self.ans
```

124 二叉树中的最大路径和
```bash
class Solution:
    def maxPathSum(self, root: Optional[TreeNode]) -> int:
        self.ans = float('-inf')

        def dfs(node):
            if not node:
                return 0

            left = max(dfs(node.left), 0)
            right = max(dfs(node.right), 0)

            self.ans = max(self.ans, node.val + left + right)

            return node.val + max(left, right)

        dfs(root)
        return self.ans
```
35 搜索插入位置

```bash
给定一个升序数组和一个目标值，返回目标值应该插入的位置。如果目标值已存在，返回它应该插入的位置（即第一个大于等于目标值的位置）。

class Solution:
    def searchInsert(self, nums: List[int], target: int) -> int:
        left, right = 0, len(nums) - 1

        while left <= right:
            mid = (left + right) // 2

            if nums[mid] == target:
                return mid
            elif nums[mid] < target:
                left = mid + 1
            else:
                right = mid - 1

        return left
```

74 搜索二维矩阵

```bash
给定一个 m × n 矩阵，每行从左到右递增，每行的第一个数大于上一行的最后一个数。判断目标值是否存在。

class Solution:
    def searchMatrix(self, matrix: List[List[int]], target: int) -> bool:
        m, n = len(matrix), len(matrix[0])
        left, right = 0, m * n - 1

        while left <= right:
            mid = (left + right) // 2
            value = matrix[mid // n][mid % n]

            if value == target:
                return True
            elif value < target:
                left = mid + 1
            else:
                right = mid - 1

        return False

```

34 在排序数组中查找元素的第一个和最后一个位置

```bash
给定一个升序数组和一个目标值，找出目标值在数组中的起始位置和结束位置。如果不存在，返回 [-1, -1]。

class Solution:
    def searchRange(self, nums: List[int], target: int) -> List[int]:
        def findLeft():
            left, right = 0, len(nums) - 1
            ans = -1

            while left <= right:
                mid = (left + right) // 2
                if nums[mid] == target:
                    ans = mid
                    right = mid - 1
                elif nums[mid] < target:
                    left = mid + 1
                else:
                    right = mid - 1

            return ans

        def findRight():
            left, right = 0, len(nums) - 1
            ans = -1

            while left <= right:
                mid = (left + right) // 2
                if nums[mid] == target:
                    ans = mid
                    left = mid + 1
                elif nums[mid] < target:
                    left = mid + 1
                else:
                    right = mid - 1

            return ans

        return [findLeft(), findRight()]

```

33 搜索旋转排序数组

```bash
给定一个旋转过的升序数组（如 [4,5,6,7,0,1,2]）和一个目标值，判断目标值是否存在。数组中不存在重复元素。

class Solution:
    def search(self, nums: List[int], target: int) -> int:
        left, right = 0, len(nums) - 1

        while left <= right:
            mid = (left + right) // 2

            if nums[mid] == target:
                return mid

            if nums[left] <= nums[mid]:
                if nums[left] <= target < nums[mid]: #通过这种方法可以更高效
                    right = mid - 1
                else:
                    left = mid + 1
            else:
                if nums[mid] < target <= nums[right]:
                    left = mid + 1
                else:
                    right = mid - 1

        return -1
```

153 寻找旋转排序数组中的最小值

```bash

给定一个旋转过的升序数组（如 [3,4,5,1,2]），找出其中的最小元素。数组中不存在重复元素。

class Solution:
    def findMin(self, nums: List[int]) -> int:
        left, right = 0, len(nums) - 1

        while left < right:
            mid = (left + right) // 2

            if nums[mid] > nums[right]:
                left = mid + 1
            else:
                right = mid

        return nums[left]
```

排序
```bash
冒泡：相邻比较交换； 相邻元素比较，大的往后冒，每轮确定一个最大值。
选择：找最小值放前面； 每轮找最小值，放到未排序部分的开头。
插入：逐个插入； 像打扑克，把每个元素插入到已排序部分的合适位置。
快排：选基准分治； 边拆分边分区归类， 分完基本成型
归并：分治后合并。合并， 就是简单比大小。  先彻底拆分打散，收尾再逐级合并排序（和快排的区别就是分的时候有没有做操作）

快排
def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)

归并
def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result
```



4 寻找两个正序数组中的中位数

```bash
class Solution:
    def findMedianSortedArrays(self, nums1: List[int], nums2: List[int]) -> float:
        A, B = nums1, nums2
        m, n = len(A), len(B)

        if m > n:
            A, B, m, n = B, A, n, m

        left, right = 0, m

        while left <= right:
            i = (left + right) // 2
            j = (m + n + 1) // 2 - i

            Aleft = A[i - 1] if i > 0 else float("-inf")
            Aright = A[i] if i < m else float("inf")
            Bleft = B[j - 1] if j > 0 else float("-inf")
            Bright = B[j] if j < n else float("inf")

            if Aleft <= Bright and Bleft <= Aright:
                if (m + n) % 2 == 1:
                    return max(Aleft, Bleft)
                return (max(Aleft, Bleft) + min(Aright, Bright)) / 2

            elif Aleft > Bright:
                right = i - 1
            else:
                left = i + 1

```

20 有效的括号

```bash
给定一个只包含括号的字符串，判断括号是否匹配有效。

输入: "()[]{}"
输出: true

输入: "([)]"
输出: false

class Solution:
    def isValid(self, s: str) -> bool:
        stack = []
        mapping = {
            ')': '(',
            ']': '[',
            '}': '{'
        }

        for ch in s:
            if ch in mapping:
                if not stack or stack[-1] != mapping[ch]:
                    return False
                stack.pop()
            else:
                stack.append(ch)

        return len(stack) == 0
```

155 最小的栈

```bash
class MinStack:

    def __init__(self):
        self.stack = []
        self.min_stack = []

    def push(self, val: int) -> None:
        self.stack.append(val)
        if not self.min_stack:
            self.min_stack.append(val)
        else:
            self.min_stack.append(min(val, self.min_stack[-1]))

    def pop(self) -> None:
        self.stack.pop()
        self.min_stack.pop()

    def top(self) -> int:
        return self.stack[-1]

    def getMin(self) -> int:
        return self.min_stack[-1]
```

394 字符串解码
```bash
class Solution:
    def decodeString(self, s: str) -> str:
        stack = []

        for ch in s:
            if ch != ']':
                stack.append(ch)
            else:
                # 1. 取出 [] 里的字符串
                substr = ''
                while stack[-1] != '[':
                    substr = stack.pop() + substr
                stack.pop()  # 弹掉 '['

                # 2. 取出前面的数字
                num = ''
                while stack and stack[-1].isdigit():
                    num = stack.pop() + num

                # 3. 重复后压回栈
                stack.append(int(num) * substr)

        return ''.join(stack)
```

739 每日温度

```bash
class Solution:
    def dailyTemperatures(self, temperatures: list[int]) -> list[int]:
        n = len(temperatures)
        answer = [0] * n
        stack = []

        for i in range(n):
            while stack and temperatures[i] > temperatures[stack[-1]]:
                prev_index = stack.pop()
                answer[prev_index] = i - prev_index
            stack.append(i)

        return answer
        
stack = []
for i in range(len(nums)):
    while stack and nums[i] > nums[stack[-1]]:
        prev = stack.pop()
        ans[prev] = i - prev
    stack.append(i)
```

84 柱状图中最大的矩形
```bash
class Solution:
    def largestRectangleArea(self, heights: list[int]) -> int:
        stack = []
        max_area = 0
        heights = [0] + heights + [0]

        for i in range(len(heights)):
            while stack and heights[i] < heights[stack[-1]]:
                h = heights[stack.pop()]
                w = i - stack[-1] - 1
                max_area = max(max_area, h * w)
            stack.append(i)

        return max_area
```

215 数组中的第K个最大元素
```bash
import heapq

class Solution:
    def findKthLargest(self, nums: list[int], k: int) -> int:
        heap = []
        for num in nums:
            if len(heap) < k:
                heapq.heappush(heap, num)
            elif num > heap[0]:
                heapq.heapreplace(heap, num)
        return heap[0]
        
简单写法
        heap = []
        for num in nums:
            heapq.heappush(heap, num)
            if len(heap) > k:
                heapq.heappop(heap)  # 先 push 再 pop
        return heap[0]
        
```

347 前K个高频元素
```bash
from collections import Counter
import heapq

class Solution:
    def topKFrequent(self, nums, k):
        count = Counter(nums)
        heap = []

        for num, freq in count.items():
            heapq.heappush(heap, (freq, num))
            if len(heap) > k:
                heapq.heappop(heap)

        return [num for freq, num in heap]

```

295 数据流的中位数
```bash
import heapq

class MedianFinder:

    def __init__(self):
        self.small = []  # 大顶堆（存较小一半，实际存负数）
        self.large = []  # 小顶堆（存较大一半）

    def addNum(self, num: int) -> None:
        heapq.heappush(self.small, -num)

        # 保证 small 里的最大值 <= large 里的最小值
        heapq.heappush(self.large, -heapq.heappop(self.small))

        # 保证两个堆元素个数平衡
        if len(self.large) > len(self.small):
            heapq.heappush(self.small, -heapq.heappop(self.large))

    def findMedian(self) -> float:
        if len(self.small) > len(self.large):
            return -self.small[0]
        return (-self.small[0] + self.large[0]) / 2.0

```

爬楼梯
```bash
class Solution:
    def climbStairs(self, n: int) -> int:
        if n <= 2:
            return n

        dp = [0] * (n + 1)
        dp[1] = 1
        dp[2] = 2

        for i in range(3, n + 1):
            dp[i] = dp[i - 1] + dp[i - 2]

        return dp[n]
```
杨辉三角

```bash
class Solution:
    def generate(self, numRows: int):
        res = []

        for i in range(numRows):
            row = [1] * (i + 1)

            for j in range(1, i):
                row[j] = res[i - 1][j - 1] + res[i - 1][j]

            res.append(row)

        return res
```

打家劫舍
```bash
class Solution:
    def rob(self, nums):
        if not nums:
            return 0
        if len(nums) == 1:
            return nums[0]

        dp = [0] * len(nums)
        dp[0] = nums[0]
        dp[1] = max(nums[0], nums[1])

        for i in range(2, len(nums)):
            dp[i] = max(dp[i - 1], dp[i - 2] + nums[i])

        return dp[-1]
```
完全平方数
```bash
class Solution:
    def numSquares(self, n: int) -> int:
        dp = [float('inf')] * (n + 1)
        dp[0] = 0

        for i in range(1, n + 1):
            j = 1
            while j * j <= i:
                dp[i] = min(dp[i], dp[i - j * j] + 1)
                j += 1

        return dp[n]
```

零钱兑换 
```bash
class Solution:
    def coinChange(self, coins, amount):
        dp = [float('inf')] * (amount + 1)
        dp[0] = 0

        for i in range(1, amount + 1):
            for coin in coins:
                if i >= coin:
                    dp[i] = min(dp[i], dp[i - coin] + 1)

        return dp[amount] if dp[amount] != float('inf') else -1

```

单词拆分
```bash
class Solution:
    def wordBreak(self, s, wordDict):
        word_set = set(wordDict)
        n = len(s)
        dp = [False] * (n + 1)
        dp[0] = True

        for i in range(1, n + 1):
            for j in range(i):
                if dp[j] and s[j:i] in word_set:
                    dp[i] = True
                    break

        return dp[n]
```

最长递增子序列
```bash
class Solution:
    def lengthOfLIS(self, nums):
        n = len(nums)
        dp = [1] * n
        res = 1

        for i in range(n):
            for j in range(i):
                if nums[j] < nums[i]:
                    dp[i] = max(dp[i], dp[j] + 1)
            res = max(res, dp[i])

        return res
        
```

乘积最大子数组
```bash
class Solution:
    def maxProduct(self, nums):
        prev_max = nums[0]
        prev_min = nums[0]
        res = nums[0]

        for i in range(1, len(nums)):
            x = nums[i]
            cur_max = max(x, prev_max * x, prev_min * x)
            cur_min = min(x, prev_max * x, prev_min * x)

            prev_max = cur_max
            prev_min = cur_min
            res = max(res, cur_max)

        return res
        
```

分割等和子集
```bash
class Solution:
    def canPartition(self, nums):
        total = sum(nums)

        if total % 2 != 0:
            return False

        target = total // 2
        dp = [False] * (target + 1)
        dp[0] = True

        for num in nums:
            for j in range(target, num - 1, -1):
                dp[j] = dp[j] or dp[j - num]

        return dp[target]

```

最长有效括号 (hard)
```bash
class Solution:
    def longestValidParentheses(self, s: str) -> int:
        stack = [-1]
        res = 0

        for i, ch in enumerate(s):
            if ch == '(':
                stack.append(i)
            else:
                stack.pop()
                if not stack:
                    stack.append(i)
                else:
                    res = max(res, i - stack[-1])

        return res
        

class Solution:
    def longestValidParentheses(self, s: str) -> int:
        n = len(s)
        dp = [0] * n
        res = 0

        for i in range(1, n):
            if s[i] == ')':
                if s[i - 1] == '(':
                    dp[i] = (dp[i - 2] if i >= 2 else 0) + 2
                else:
                    left = i - dp[i - 1] - 1
                    if left >= 0 and s[left] == '(':
                        dp[i] = dp[i - 1] + 2
                        if left - 1 >= 0:
                            dp[i] += dp[left - 1]

                res = max(res, dp[i])

        return res

```

不同路径
```bash
class Solution:
    def uniquePaths(self, m: int, n: int) -> int:
        dp = [[1] * n for _ in range(m)]

        for i in range(1, m):
            for j in range(1, n):
                dp[i][j] = dp[i - 1][j] + dp[i][j - 1]

        return dp[m - 1][n - 1]

```

最小路径和
```bash
class Solution:
    def minPathSum(self, grid):
        m, n = len(grid), len(grid[0])
        dp = [[0] * n for _ in range(m)]
        dp[0][0] = grid[0][0]

        for j in range(1, n):
            dp[0][j] = dp[0][j - 1] + grid[0][j]

        for i in range(1, m):
            dp[i][0] = dp[i - 1][0] + grid[i][0]

        for i in range(1, m):
            for j in range(1, n):
                dp[i][j] = min(dp[i - 1][j], dp[i][j - 1]) + grid[i][j]

        return dp[m - 1][n - 1]
```

最长回文子串
```bash
class Solution:
    def longestPalindrome(self, s: str) -> str:
        n = len(s)
        dp = [[False] * n for _ in range(n)]
        res = ""
        max_len = 0

        for i in range(n - 1, -1, -1):
            for j in range(i, n):
                if s[i] == s[j] and (j - i < 2 or dp[i + 1][j - 1]):
                    dp[i][j] = True
                    if j - i + 1 > max_len:
                        max_len = j - i + 1
                        res = s[i:j + 1]

        return res

```

最长公共子序列
```bash
class Solution:
    def longestCommonSubsequence(self, text1: str, text2: str) -> int:
        m, n = len(text1), len(text2)
        
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if text1[i - 1] == text2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1] + 1
                else:
                    dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
        
        return dp[m][n]  
```

编辑距离
```bash
class Solution:
    def minDistance(self, word1: str, word2: str) -> int:
        m, n = len(word1), len(word2)
        
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        # 边界：word1 为空，需要插入 n 次
        for j in range(n + 1):
            dp[0][j] = j
        
        # 边界：word2 为空，需要删除 m 次
        for i in range(m + 1):
            dp[i][0] = i
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if word1[i - 1] == word2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    dp[i][j] = min(dp[i - 1][j],      # 删除
                                    dp[i][j - 1],      # 插入
                                    dp[i - 1][j - 1]) + 1  # 替换
        
        return dp[m][n]

```

只出现一次的数字
```bash
给定一个非空整数数组，除了某个元素只出现一次外，其余每个元素均出现两次。找出那个只出现一次的元素。

class Solution:
    def singleNumber(self, nums: list[int]) -> int:
        result = 0
        for num in nums:
            result ^= num
        return result


class Solution:
    def singleNumber(self, nums: list[int]) -> int:
        from collections import Counter
        count = Counter(nums)
        for num, freq in count.items():
            if freq == 1:
                return num
                
```

多数元素
```bash
给定一个大小为 n 的数组，找到其中的多数元素。多数元素是指在数组中出现次数大于 ⌊n/2⌋ 的元素。

思路
维护一个候选数和计数，遇到相同数计数加 1，不同数计数减 1，计数为 0 时更换候选数。

多数元素数量超过一半，即使和其他元素全部抵消，剩下的还是多数元素。

class Solution:
    def majorityElement(self, nums: list[int]) -> int:
        candidate = None
        count = 0
        
        for num in nums:
            if count == 0:
                candidate = num
            count += 1 if num == candidate else -1
        
        return candidate
        

其他解法
class Solution:
    def majorityElement(self, nums: list[int]) -> int:
        from collections import Counter
        count = Counter(nums)
        return max(count.keys(), key=count.get)
        

class Solution:
    def majorityElement(self, nums: list[int]) -> int:
        nums.sort()
        return nums[len(nums) // 2]

```

颜色分类
```bash

给定一个包含红色、白色和蓝色、共 n 个元素的数组，原地对它们进行排序，使得相同颜色的元素相邻，
并按照红色、白色、蓝色顺序排列。使用整数 0、1、2 分别代表红色、白色、蓝色。

class Solution:
    def sortColors(self, nums: list[int]) -> None:
        left, right = 0, len(nums) - 1
        curr = 0
        
        while curr <= right:
            if nums[curr] == 0:
                nums[left], nums[curr] = nums[curr], nums[left]
                left += 1
                curr += 1
            elif nums[curr] == 2:
                nums[curr], nums[right] = nums[right], nums[curr]
                right -= 1
            else:
                curr += 1

```


下一个排列
```bash
给定一个整数数组，找到其下一个排列。如果不存在下一个更大的排列，则将数字重新排列成最小的排列（即升序）。

输入: nums = [1, 2, 3]
输出: [1, 3, 2]
 
输入: nums = [3, 2, 1]
输出: [1, 2, 3]

步骤 1：找第一个下降的位置
步骤 2：找第一个大于 nums[i] 的位置
步骤 3：交换 nums[i] 和 nums[j]
步骤 4：反转 i+1 到末尾


class Solution:
    def nextPermutation(self, nums: list[int]) -> None:
        n = len(nums)
        
        # 1. 找到第一个下降的位置（比较 nums[i-1] 和 nums[i]）
        i = n - 1
        while i > 0 and nums[i - 1] >= nums[i]:
            i -= 1
        
        # 下降位置在 i-1
        pivot = i - 1
        
        if pivot >= 0:
            # 2. 找到第一个大于 nums[pivot] 的位置
            j = n - 1
            while nums[j] <= nums[pivot]:
                j -= 1
            # 3. 交换
            nums[pivot], nums[j] = nums[j], nums[pivot]
        
        # 4. 反转 pivot+1 到末尾
        left, right = pivot + 1, n - 1
        while left < right:
            nums[left], nums[right] = nums[right], nums[left]
            left += 1
            right -= 1
            
```

寻找重复数
```bash
题意
给定一个包含 n + 1 个整数的数组，数字都在 [1, n] 范围内，只有一个数字重复，找出这个重复的数字。不能修改数组，只能用常数空间。

示例
输入: nums = [1, 3, 4, 2, 2]
输出: 2
 
输入: nums = [3, 1, 3, 4, 2]
输出: 3

class Solution:
    def findDuplicate(self, nums: list[int]) -> int:
        slow = fast = 0
        
        # 第一阶段：找到相遇点
        while True:
            slow = nums[slow]
            fast = nums[nums[fast]]
            if slow == fast:
                break
        
        # 第二阶段：找到环的入口
        slow = 0
        while slow != fast:
            slow = nums[slow]
            fast = nums[fast]
        
        return slow
        
        
class Solution:
    def findDuplicate(self, nums: list[int]) -> int:
        left, right = 1, len(nums) - 1
        
        while left < right:
            mid = (left + right) // 2
            count = sum(1 for num in nums if num <= mid)
            
            if count > mid:
                right = mid
            else:
                left = mid + 1
        
        return left


```

买卖股票的最佳时机
```bash

给定一个数组，其中第 i 个元素是第 i 天的股票价格。如果你最多只允许完成一笔交易（即买入和卖出一次），设计算法计算最大利润。

输入: prices = [7, 1, 5, 3, 6, 4]
输出: 5
解释: 在第 2 天（价格=1）买入，第 5 天（价格=6）卖出，利润 = 6-1 = 5
 
输入: prices = [7, 6, 4, 3, 1]
输出: 0
解释: 没有利润，不交易



class Solution:
    def maxProfit(self, prices: list[int]) -> int:
        min_price = float('inf')
        max_profit = 0
        
        for price in prices:
            min_price = min(min_price, price)
            max_profit = max(max_profit, price - min_price)
        
        return max_profit
        
        
```

跳跃游戏
```bash
给定一个非负整数数组，每个元素代表你在该位置可以跳跃的最大长度。判断是否能到达最后一个位置。
输入: nums = [2, 3, 1, 1, 4]
输出: true
解释: 从索引 0 跳 1 步到索引 1，再跳 3 步到索引 4
 
输入: nums = [3, 2, 1, 0, 4]
输出: false
解释: 无论怎么跳，都会停在索引 3

class Solution:
    def canJump(self, nums: list[int]) -> bool:
        max_reach = 0
        
        for i in range(len(nums)):
            if i > max_reach:  # 当前位置无法到达
                return False
            max_reach = max(max_reach, i + nums[i])
            if max_reach >= len(nums) - 1:
                return True
        
        return max_reach >= len(nums) - 1

```


跳跃游戏II

```bash
给定一个非负整数数组，每个元素代表你在该位置可以跳跃的最大长度。假设总能到达最后一个位置，求最少跳跃次数。

输入: nums = [2, 3, 1, 1, 4]
输出: 2
解释: 从索引 0 跳 1 步到索引 1，再跳 3 步到索引 4（最少 2 次）


class Solution:
    def jump(self, nums: list[int]) -> int:
        jumps = 0
        current_end = 0  # 当前跳跃能到达的边界
        farthest = 0     # 下一次跳跃能到达的最远位置
        
        for i in range(len(nums) - 1):  # 不需要遍历最后一个位置
            farthest = max(farthest, i + nums[i])
            
            if i == current_end:  # 到达当前边界，必须跳跃 
                jumps += 1
                current_end = farthest
                
                if current_end >= len(nums) - 1:
                    break
        
        return jumps
        
就是先把跳的次数加一 ， 比如跳一下 可以跳到 0-4 ， 然后就记录这其中的max farthest， 
到第四步（当时他有可能是在 2  的时候得到的最大值）的时候，  跳的次数再加一

        
```


划分字母区间
```bash
给定一个字符串，把字符串分成尽可能多的部分，使得每个字母最多出现在一个部分中。返回每个部分的长度。

输入: s = "ababcbacadefegdehijhklij"
输出: [9, 7, 8]
解释:
- "ababcbaca" (长度 9)
- "defegde" (长度 7)
- "hijhklij" (长度 8)

"ababcbacadefegdehijhklij"
分成三段：
- "ababcbaca" → a, b, c 只在这段出现
- "defegde" → d, e, f, g 只在这段出现  
- "hijhklij" → h, i, j, k, l 只在这段出现


思路
记录每个字母最后一次出现的位置
遍历字符串，维护当前区间的结束位置
当到达结束位置时，划分一个区间

class Solution:
    def partitionLabels(self, s: str) -> list[int]:
        # 记录每个字母最后出现的位置
        last_pos = {char: i for i, char in enumerate(s)}
        
        result = []
        start = 0  # 当前区间开始
        end = 0    # 当前区间结束
        
        for i, char in enumerate(s):
            end = max(end, last_pos[char])  # 更新当前区间的结束位置
            
            if i == end:  # 到达区间结束位置
                result.append(end - start + 1)
                start = i + 1  # 下一个区间开始
        
        return result
        
```


拼出小于目标数的最大整数
```bash
class Solution:
    def largestNumberLessThanTarget(self, digits: list[int], target: int) -> str:
        from collections import Counter
        
        target_str = str(target)
        n = len(target_str)
        counter = Counter(digits)
        
        def backtrack(pos, is_smaller, current):
            if pos == n:
                return ''.join(current) if current else "无效"
            
            limit = int(target_str[pos]) if not is_smaller else 9
            
            for d in range(limit, -1, -1):
                if counter[d] > 0:
                    counter[d] -= 1
                    current.append(str(d))
                    
                    if d < limit or is_smaller:
                        res = backtrack(pos + 1, True, current)
                    else:
                        res = backtrack(pos + 1, False, current)
                    
                    if res != "无效":
                        return res
                    
                    current.pop()
                    counter[d] += 1
            
            return "无效"
        
        return backtrack(0, False, [])
```



全排列
```bash
给定一个不含重复数字的数组，返回其所有可能的全排列。

输入: nums = [1, 2, 3]
输出: [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]

class Solution:
    def permute(self, nums: list[int]) -> list[list[int]]:
        result = []
        used = [False] * len(nums)
        
        def backtrack(path):
            if len(path) == len(nums):
                result.append(path[:])
                return
            
            for i in range(len(nums)):
                if used[i]:
                    continue
                
                used[i] = True
                path.append(nums[i])
                backtrack(path)
                path.pop()
                used[i] = False
        
        backtrack([])
        return result


```

子集
```bash
给定一个不含重复元素的整数数组，返回所有可能的子集（幂集）。
输入: nums = [1, 2, 3]
输出: [[], [1], [2], [1, 2], [3], [1, 3], [2, 3], [1, 2, 3]]

class Solution:
    def subsets(self, nums: list[int]) -> list[list[int]]:
        result = []
        
        def backtrack(start, path):
            result.append(path[:])
            
            for i in range(start, len(nums)):
                path.append(nums[i])
                backtrack(i + 1, path)
                path.pop()
        
        backtrack(0, [])
        return result
        
```

电话号码的字母组合
```bash
给定一个包含 2-9 的字符串，返回数字能表示的所有字母组合。数字到字母的映射如下：
2: abc
3: def
4: ghi
5: jkl
6: mno
7: pqrs
8: tuv
9: wxyz
输入: digits = "23"
输出: ["ad", "ae", "af", "bd", "be", "bf", "cd", "ce", "cf"]


class Solution:
    def letterCombinations(self, digits: str) -> list[str]:
        if not digits:
            return []
        
        mapping = {
            '2': 'abc', '3': 'def', '4': 'ghi', '5': 'jkl',
            '6': 'mno', '7': 'pqrs', '8': 'tuv', '9': 'wxyz'
        }
        
        result = []
        
        def backtrack(index, path):
            if index == len(digits):
                result.append(''.join(path))
                return
            
            for letter in mapping[digits[index]]:
                path.append(letter)
                backtrack(index + 1, path)
                path.pop()
        
        backtrack(0, [])
        return result

```

组合总和
```bash
给定一个无重复元素的整数数组 candidates 和一个目标整数 target，找出 candidates 中所有可以使数字和为 target 的组合。candidates 中的数字可以无限制重复使用。

输入: candidates = [2, 3, 6, 7], target = 7
输出: [[2, 2, 3], [7]]


class Solution:
    def combinationSum(self, candidates: list[int], target: int) -> list[list[int]]:
        result = []
        
        def backtrack(start, path, remaining):
            if remaining == 0:
                result.append(path[:])
                return
            if remaining < 0:
                return
            
            for i in range(start, len(candidates)):
                path.append(candidates[i])
                backtrack(i, path, remaining - candidates[i])  # 从 i 开始，可以重复使用
                path.pop()
        
        backtrack(0, [], target)
        return result

```

括号生成
```bash
给定 n 对括号，生成所有有效的括号组合。
输入: n = 3
输出: ["((()))", "(()())", "(())()", "()(())", "()()()"]

思路
维护左括号和右括号的数量：

左括号数量 < n 时，可以加左括号
右括号数量 < 左括号数量时，可以加右括号


class Solution:
    def generateParenthesis(self, n: int) -> list[str]:
        result = []
        
        def backtrack(left, right, path):
            if len(path) == 2 * n:
                result.append(''.join(path))
                return
            
            if left < n:
                path.append('(')
                backtrack(left + 1, right, path)
                path.pop()
            
            if right < left:
                path.append(')')
                backtrack(left, right + 1, path)
                path.pop()
        
        backtrack(0, 0, [])
        return result

```

单词搜索
```bash
给定一个 m x n 的二维字符网格和一个单词，判断单词是否存在于网格中。单词必须由相邻单元格的字母构成，不能重复使用单元格。
输入: board = [["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]], word = "ABCCED"
输出: true

思路
从每个位置开始，尝试匹配单词，用 DFS 搜索四个方向，标记已访问的单元格。

class Solution:
    def exist(self, board: list[list[str]], word: str) -> bool:
        m, n = len(board), len(board[0])
        
        def dfs(i, j, index):
            if index == len(word):
                return True
            if i < 0 or i >= m or j < 0 or j >= n or board[i][j] != word[index]:
                return False
            
            temp = board[i][j]
            board[i][j] = '#'  # 标记已访问
            
            found = (dfs(i + 1, j, index + 1) or
                    dfs(i - 1, j, index + 1) or
                    dfs(i, j + 1, index + 1) or
                    dfs(i, j - 1, index + 1))
            
            board[i][j] = temp  # 恢复
            return found
        
        for i in range(m):
            for j in range(n):
                if dfs(i, j, 0):
                    return True
        
        return False
```


分割回文串
```bash
给定一个字符串，将字符串分割成若干子串，使得每个子串都是回文串。返回所有可能的分割方案。

输入: s = "aab"
输出: [["a","a","b"],["aa","b"]]

遍历所有可能的分割点，如果当前子串是回文，继续递归处理剩余部分。


class Solution:
    def partition(self, s: str) -> list[list[str]]:
        result = []
        
        def is_palindrome(sub):
            return sub == sub[::-1]
        
        def backtrack(start, path):
            if start == len(s):
                result.append(path[:])
                return
            
            for end in range(start + 1, len(s) + 1):
                substring = s[start:end]
                if is_palindrome(substring):
                    path.append(substring)
                    backtrack(end, path)
                    path.pop()
        
        backtrack(0, [])
        return result




```



RAG
```bash
RAG: 用户问题 -> 向量检索相关文档 -> 文档和问题给LLM -> LLM 回答

step1:切片
step2:向量化+存入VectorDB
step3:检索+生成

pip install chromadb sentence-transformers
# rag_demo.py  —— 最简 RAG，约 50 行

import chromadb
from sentence_transformers import SentenceTransformer

# ── 1. 准备知识库文档 ──────────────────────────────────────────
DOCS = [
    "doc1",
    "doc2",
    "doc3",
]

# ── 2. 初始化 embedding 模型 和 ChromaDB ──────────────────────
embedder = SentenceTransformer("all-MiniLM-L6-v2")  # 本地模型，首次自动下载

client = chromadb.PersistentClient(path="./chroma_demo")  # 持久化到本地
collection = client.get_or_create_collection("demo")

# ── 3. 索引（只做一次）────────────────────────────────────────
if collection.count() == 0:
    print("建立索引中...")
    embeddings = embedder.encode(DOCS, convert_to_numpy=True).tolist()
    collection.add(
        documents=DOCS,
        embeddings=embeddings,
        ids=[f"doc-{i}" for i in range(len(DOCS))],
    )
    print(f"索引完成，共 {len(DOCS)} 条")

# ── 4. 检索函数 ────────────────────────────────────────────────
def search(query: str, top_k: int = 2) -> list[str]:
    q_emb = embedder.encode([query], convert_to_numpy=True).tolist()
    results = collection.query(query_embeddings=q_emb, n_results=top_k)
    return results["documents"][0]  # list[str]

# ── 5. 模拟 RAG 问答（不接 LLM，直接打印检索结果）─────────────
if __name__ == "__main__":
    questions = [
        "blobsvc 线程太多怎么排查？",
        "怎么查看内存使用？",
    ]
    for q in questions:
        print(f"\n❓ 问题: {q}")
        chunks = search(q, top_k=2)
        for i, c in enumerate(chunks, 1):
            print(f"  [{i}] {c}")
        # 实际项目里这里把 chunks 拼成 prompt 发给 LLM
        prompt = f"根据以下资料回答问题：\n{''.join(chunks)}\n\n问题：{q}"
        print(f"  → 拼好的 Prompt (前100字): {prompt[:100]}...")
        
        
DOCS → encode() → embeddings (float 向量)
                        ↓
                 collection.add() → ChromaDB 存盘

用户问题 → encode() → 问题向量
                        ↓
                 collection.query() → 找最相近的 DOCS
                        ↓
               拼成 prompt → 发给 LLM
 
```



