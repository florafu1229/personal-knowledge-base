## 笔试 ##

### 死锁 ###

```
7个线程，每个线程需要4个资源，每次只能acquire 1个，最少需要多少个资源才能保证不死锁？

答案：22个
```

### 数学推理 ###

```
问题：初始 a=53，b=22，每轮给其中一个数加上当前轮次（第1轮+1，第2轮+2，第3轮+3...），问第几轮两数可以相等？

答案：第 9 轮（第一次相等）
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
int *ptr;    // ptr 是未初始化的野指针
*ptr = 10;   // 试图往野指针指向的地址写入数据
ptr 声明时没有指向任何合法的内存地址，它的值是随机的（垃圾值）。
*ptr = 10 试图把数据写入这个随机地址，这通常会导致段错误（Segmentation Fault），程序崩溃。
即使侥幸没崩溃，后续的 printf("hello", *ptr) 也会因为 ptr 非法而行为异常。
这段关于“野指针”的解释挺关键的，需要我帮你整理一份《C语言常见内存错误速查表》方便复习吗？
```

### 二叉搜索树&先序转后续 ###
```
BST 的定义性质
    二叉搜索树要求：左子树所有节点 < 根节点 < 右子树所有节点。
    图片中的解析首先指出了数据本身的问题（出现了重复值 16），这违反了标准 BST 的定义，属于“陷阱”或“边界条件判断”。
先序遍历（Pre-order Traversal）的特征
    顺序是：根 -> 左 -> 右。
    解题关键：序列的第一个数字一定是整棵树的根节点。
后序遍历（Post-order Traversal）的特征
    顺序是：左 -> 右 -> 根。
    解题目标：利用先序序列还原树的结构，然后按“左右根”的顺序输出。
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
在一个实时操作系统中，有三个任务 A、B、C，优先级 A > B > C。
任务 C 持有一个互斥锁，任务 A 试图获取该锁而被阻塞。此时任务 B 就绪并抢占了 CPU。请问系统出现了什么问题
答案： 优先级反转 priority inversion

为什么会出现“高优等低优”？
根本原因：共享资源（如互斥锁）的持有与等待。
假设有一个低优先级任务 C 正在运行，并持有了某个共享资源（比如一把锁）。此时，一个高优先级任务 A 突然就绪，它也需要访问这个资源。由于资源被 C 占用，A 无法继续执行，只能进入“阻塞等待”状态。
→ 结果： 高优先级的 A 被迫等待低优先级的 C 释放资源，这就形成了“高优等低优”的局面。

为什么“中优”能抢到 CPU？
关键机制：抢占式调度 + 无关任务的干扰。
在 A 等待 C 释放锁的这段时间，如果系统中还有一个中等优先级的任务 B 就绪了，而 B 并不需要那个被 C 持有的资源，那么根据抢占式调度规则，B 会立即抢占 CPU 开始执行。
→ 结果： 本应让高优先级 A 尽快执行的 CPU 时间，被中优先级的 B “插队”占用了。而 B 的执行又进一步延迟了 C 的运行（因为 C 的优先级比 B 低，无法抢占 B），导致 C 更晚释放锁，A 也就被无限期拖延。
 
针对此问题的典型解决方案:
优先级继承(Priority Inheritance):低优先级线程临时继承高优先级线程的优先级，快速执行完临界区
并释放锁。
优先级天花板(Priority Ceiling):预先将锁的优先级设为最高，防止被中等优先级线程抢占。

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
1、类方法和实例方法区别
2、类方法和实例方法具体应用（举例）
3、__new__和__init__区别
4、深浅拷贝
5、哪些数据类型可变哪些不可变
6、可变与不可变类型区别
7、Python多线程
8、Python是否是脚本语言
9、Python是面向对象编程还是面向过程编程
10、什么是面向对象
11、函数传入列表用什么参数
12、传入字典用什么参数
13、判断None用==还是is、list和tuple的区别
14、什么场景下用dict、深浅拷贝、线程与进程、多线程与多进程、进程间通信、消息队列等
15 set 去重 O(n)
16 GIL

```

2. linux 常用命令
```
find 
grep lsof
awd
sed
ls 
tar 

```

3. 其他
```
包安装的工具有哪些
虚拟机和docker 区别
系统权限 
软链接

```

4. AI
```
RAG 
transformer


```





