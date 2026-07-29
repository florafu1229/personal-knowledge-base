## 笔试 ##
### 递归 ###
```
void foo (int i){
if (i>1){
foo(i/2); foo(i/2);
}
cout<<"#"
}
一共打印了七次#
```
### 死锁 ###
```
7个线程，每个线程需要4个资源，每次只能acquire 1个，最少需要多少个资源才能保证不死锁？

答案：22个
``` 
### 数学推理 ###

```
问题：初始 a=22，b=75，每轮给任意其中一个数加上当前轮次（第1轮+1，第2轮+2，第3轮+3...），问第几轮两数可以相等？

答案：第 10 轮（第一次相等）
```

### 进程同步 ###

```
1. 题目描述
考虑两个进程 P1 和 P2 访问临界区的方法，共享布尔变量 S1 和 S2 初始值随机。
P1 的逻辑：
while(S1 == S2); （忙等待：若相等则阻塞）
Critical Section （进入临界区）
S1 = S2; （退出时：将 S1 设为与 S2 相等）
P2 的逻辑：
while(S1 != S2); （忙等待：若不等则阻塞）
Critical Section （进入临界区）
S2 = not(S1); （退出时：将 S2 设为与 S1 相反）
问题： 该算法实现了哪些性质？

答案：
满足互斥性 (Mutual Exclusion)
不满足前进性 (Progress)
```

### c 指针陷阱 ###
```
Segmentation Fault
int *ptr;    // ptr 是未初始化的野指针
*ptr = 10;   // 试图往野指针指向的地址写入数据
ptr 声明时没有指向任何合法的内存地址，它的值是随机的（垃圾值）。
*ptr = 10 试图把数据写入这个随机地址，这通常会导致段错误（Segmentation Fault），程序崩溃。
即使侥幸没崩溃，后续的 printf("hello", *ptr) 也会因为 ptr 非法而行为异常。
```

### 二叉搜索树&先序转后续 ###
```
BST 的定义性质
    二叉搜索树要求：左子树所有节点 < 根节点 < 右子树所有节点。
先序遍历（Pre-order Traversal）的特征
    顺序是：根 -> 左 -> 右。
    解题关键：序列的第一个数字一定是整棵树的根节点。
后序遍历（Post-order Traversal）的特征
    顺序是：左 -> 右 -> 根。
    解题目标：利用先序序列还原树的结构，然后按“左右根”的顺序输出。
二叉搜索树的前序遍历是： 15， 10， 12， 11，20， 18， 16， 19 
那么后序就是： 11 12 10 16 19 18 20 15
```

### 快排 ###

```
题目：对序列 {15, 11, 12, 10, 13, 8, 7, 19} 进行一趟快速排序后，下列哪个元素是本次排序的基准（Pivot）？
答案：19

解题思路：
快速排序一趟 Partition 结束后，基准元素会落在它的最终位置，且满足：
左边所有元素 < 基准
右边所有元素 > 基准
逐个检查：只有 19 满足左边所有数都比它小，所以 19 就是 Pivot。

```

### 并发调度问题 ###
```
优先级继承可以解决优先级反转问题
Consider a complex multi-threaded Linux application that utilizes POSIX threads for parallel processing. The application has multiple threads executing concurrently, each accessing shared resources. One of the threads needs to perform a critical section of code protected by a mutex to ensure proper synchronization and prevent data corruption. However, the following challenges are there:

1.  The thread that holds the mutex enters a non-preemptive state and cannot be forcibly preempted by the scheduler.
2.  There is a real-time thread with higher priority that requires access to the same critical section protected by the mutex.
3.  The real-time thread needs to be granted access to the critical section within a fixed time frame, or it might cause a system failure.

Which of the following statements is true?

选项内容 (Options)

*   A. Since the thread holding the mutex cannot be preempted, the real-time thread will never be able to access the critical section.
*   B. The real-time thread will be granted access to the critical section, and the mutex will be released from the non-preemptive thread, causing potential data corruption.
*   C. To avoid deadlock, the real-time thread will forcefully acquire the mutex, overriding the non-preemptive thread's access and prioritizing... (text cut off)
*   D. Implementing priority inheritance protocol with the mutex will ensure the real-time thread's access to the critical section without corruption.

正确答案与详细解析

正确选项：D
(Implementing priority inheritance protocol with the mutex will ensure the real-time thread's access to the critical section without corruption.)

1. 核心考点：优先级反转 (Priority Inversion)
这道题描述了一个经典的实时系统问题——优先级反转。
*   场景：一个低优先级线程（题目中的非抢占线程）持有了锁（Mutex），而一个高优先级线程（实时线程）需要这把锁。
*   后果：高优先级线程被迫等待低优先级线程释放锁。如果此时还有一个中等优先级的线程插队运行，低优先级线程就永远无法运行来释放锁，导致高优先级线程无限期阻塞。这在实时系统中是致命的。

2. 为什么选 D？
*   优先级继承协议 (Priority Inheritance Protocol, PIP) 是解决这个问题的标准方案。
*   原理：当高优先级线程等待低优先级线程持有的锁时，系统会暂时将低优先级线程的优先级“提升”到高优先级线程的水平。
*   效果：这样，持有锁的低优先级线程就能尽快获得 CPU 资源（不被中等优先级线程打断），迅速执行完临界区代码并释放锁。一旦锁被释放，它的优先级恢复原状，高优先级线程获得锁并继续执行。这既保证了数据不损坏（互斥性），又满足了实时性要求。

3. 为什么其他选项是错的？
*   选项 A (Never access)：太绝对了。虽然会有延迟，但只要低优先级线程能运行结束，它最终会释放锁，高优先级线程并非“永远”无法访问。
*   选项 B (Causing corruption)：这是错误的互斥锁行为。标准的 Mutex 机制绝不会允许两个线程同时进入临界区。如果强行进入，那就不是 Mutex 的作用了，会导致严重的数据竞争和损坏。
*   选项 C (Forcefully acquire)：Mutex 的设计原则是互斥。高优先级线程不能“强行”抢夺锁，否则就破坏了同步机制，导致正在操作数据的低优先级线程状态不一致，引发系统崩溃或数据错误。


```
### fib 时间复杂度 ###
```
function fib(n):
if n <= 1 return n
else return fib(n-1) + fib(n-2)

时间复杂度 2的n次方

```

### linux操作 ###
```
考点
#解压
#find
#删除命令

解压归档文件：将归档文件解压到目录 /tmp/1817710-linux-clean-extraction-of-log-files-from-archive/logs 中。
这一步对于让文件可被访问至关重要。
识别并移除非日志文件：移除 /tmp/1817710-linux-clean-extraction-of-log-files-from-archive/logs 目录下所有不以 .log 为扩展名的文件。
此清理步骤是为了消除在低级磁盘导出过程中意外包含的任何不相关或潜在恶意文件。

#!/bin/bash

TARGET_DIR="/tmp/1817710-linux-clean-extraction-of-log-files-from-archive/logs"
ARCHIVE_FILE="your_archive_file.tar.gz" # 需替换为实际文件名

# 第一步：确保目录存在并解压
mkdir -p "$TARGET_DIR"
tar -xf "$ARCHIVE_FILE" -C "$TARGET_DIR"

# 第二步：删除非 .log 文件
# 使用 find 查找该目录下类型为文件且后缀不为 .log 的项目并删除
find "$TARGET_DIR" -type f ! -name "*.log" -delete

```
### Fib ###
```python
class Fib:
    def __init__(self, n:int):
        self.data = []
        a, b = 0, 1
        for _ in range(n):
            self.data.append(a)
            a, b = b, a+b
    def __iter__(self):
        return iter(self.data)
    def __getitem__(self, idx):
        return self.data[idx]
    def __len__(self):
        return len(self.data)
    def __repr__(self):
        return str(self.data)

if __name__ == "__main__":
    fib = Fib(10)
    print(fib)
    print(fib[5])
    print(len(fib))
    print(type(fib))
```

### 自定义异常 ###
```commandline
Topic: Custom Exception (自定义异常)

任务目标：
实现一个名为 NegativeValueError 的自定义异常类，该类继承自内置的 ValueError 异常。同时实现一个函数 validate_positive。

具体要求：
1.  类 NegativeValueError：
    *   必须继承自 ValueError。
2.  函数 validate_positive(value)：
    *   如果输入的 value 是正数（大于 0），则返回该 value。
    *   如果输入的 value 是负数，则抛出 NegativeValueError 异常，且错误信息必须为 "Input value is negative"。

示例：
*   输入：value = -4
*   调用 validate_positive(-4) 应该抛出 NegativeValueError，消息为 "Input value is negative"。

Python 代码答案

#!/bin/python3

import math
import os
import random
import re
import sys

# Complete the 'NegativeValueError' class and 'validate_positive' function below.

# 1. 定义自定义异常类，继承自 ValueError
class NegativeValueError(ValueError):
    def __init__(self, message="Input value is negative"):
        super().__init__(message)

# 2. 定义验证函数
def validate_positive(value):
    # Write your code here
    if value  0，题目约束说 value != 0），则执行 return value。

```

### api : city weather ###
```python
import requests
import re
import os

def weatherStation(keyword):
    # 注意：这是 HackerRank 的模拟接口，实际使用时需确保网络通畅
    url = 'https://jsonmock.hackerrank.com/api/weather'
    res = []
    page = 1
    
    while True:
        try:
            # 发送请求并解析 JSON
            data = requests.get(url, params={'page': page}).json()
            
            # 遍历当前页的数据
            for item in data['data']:
                # 核心筛选逻辑：不区分大小写匹配城市名
                if keyword.lower() in item['name'].lower():
                    
                    # 1. 处理温度：去掉 " degree" 字符串
                    temp = item['weather'].replace(' degree', '')
                    
                    # 2. 处理风力：从 status[0] (如 "Wind: 5 km/h") 中提取数字
                    # 使用正则 r'(\d+)' 匹配第一个连续数字 
                    wind_match = re.search(r'(\d+)', item['status'][0])
                    wind = wind_match.group(1) if wind_match else "0"
                    
                    # 3. 处理湿度：从 status[1] (如 "Humidity: 45%") 中提取数字
                    humidity_match = re.search(r'(\d+)', item['status'][1])
                    humidity = humidity_match.group(1) if humidity_match else "0"
                    
                    # 格式化结果字符串
                    res.append(f"{item['name']},{temp},{wind},{humidity}")
            
            # 翻页控制：如果当前页 >= 总页数，停止循环
            if page >= data['total_pages']:
                break
                
            page += 1
            
        except Exception as e:
            print(f"请求出错: {e}")
            break
            
    return res

if __name__ == '__main__':
    # 获取用户输入的城市关键词
    keyword = input().strip()
    
    # 调用函数获取结果
    results = weatherStation(keyword)
    
    # 写入文件
    # 注意：这里使用了环境变量 OUTPUT_PATH，本地运行建议改为固定路径，如 'output.txt'
    output_path = os.environ.get('OUTPUT_PATH', 'output.txt') 
    
    with open(output_path, 'w') as fptr:
        for line in results:
            fptr.write(line + '\n')
```

## 面试问题 ##
1. python 八股
```
类方法和实例方法区别
__new__和__init__区别
深浅拷贝
哪些数据类型可变哪些不可变
Python多线程
Python是否是脚本语言, 好处是什么
Python是面向对象编程还是面向过程编程
什么是面向对象
函数传入列表用什么参数传入字典用什么参数
判断None用==还是is，is 和==区别， 
list和tuple的区别
set的时间复杂度 O(n)
GIL
Pytest session都有啥/fixture/装饰器怎么写
匿名函数什么时候用
```

2. linux 常用命令
```
find 
grep lsof
awd
sed
ls 
tar 
du df区别，
两个node怎么免密登陆
怎么看上个命令的返回码
环境变量怎么设置
系统权限 
软链接
如何看一个进程的状态
```

3. docker k8s
```
包安装的工具有哪些
虚拟机和docker 区别
docker file里面都有啥
docker 没起来啥原因
k8s 有一个public query过来具体流程 
pv pvc区别 怎么被应用的
container之间怎么通信


```

4. AI
```
RAG 
transformer
具体某个skill 是怎么被识别应用的
Agent里面的性能耗费点在哪里


```





