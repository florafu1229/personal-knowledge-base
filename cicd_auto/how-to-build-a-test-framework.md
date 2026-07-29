# 如何从 0 到 1 搭建一个测试框架

这份文档总结如何从零搭建一个面向分布式系统的**诊断 / 自动化测试框架**。内容基于一个真实项目的设计经验,但去掉了所有公司和产品相关信息,只保留通用的框架设计思路,方便学习和面试讲解。

框架的核心定位:

- 面向一个运行在 Linux 集群上的**被测系统(SUT, System Under Test)**。
- 开发者的本地环境通常是 Windows/Mac,而被测节点是 Linux,存在**跨平台**问题。
- 既要能在本地远程连接集群做诊断,又要能把脚本**直接部署到节点上运行**,避免跨站点的慢速通信。
- 既是**诊断工具箱**,又是**自动化测试套件**,还能把结果同步到**测试管理平台**。

---

## 1. 先想清楚:框架要解决什么问题

搭框架之前,先明确痛点。这个框架要解决的核心问题有四个:

1. **参数层层透传(parameter drilling)**: 集群 IP、SSH 账号、被测系统的连接信息等在很多函数里都要用,如果一层层传参会非常啰嗦。
2. **同一逻辑多种执行方式**: 同一个"列出所有节点"的操作,在本地要走一种方式,在节点内部又要走另一种方式。
3. **跨平台依赖**: 有些 Python 模块(如 Linux 专用的 `fcntl`)在 Windows 上根本装不上,但代码又要在两边都能 import。
4. **远程执行环境受限**: 被测节点上可能没有 pip、没有第三方库、Python 版本也旧,不能假设能安装依赖。

框架的所有设计决策,都是围绕这四个问题展开的。

---

## 2. 第一原则:Function First(函数优先)

这个框架最重要的设计哲学是**函数优先**,而不是"类优先"。

- 业务能力尽量用**纯函数**表达,一个函数做一件事。
- 横切关注点(配置、缓存、模式切换、上报)用**装饰器**叠加到函数上,而不是塞进类的继承体系。
- 好处:函数容易测试、容易组合、容易被代码扫描工具分析,也容易被生成脚本工具打包。

这带来一个关键约束:**所有函数名全局唯一**。
框架在 CI 里会扫描所有模块,一旦发现两个模块里有同名函数就直接报错。
因为后面的"脚本生成"要靠函数名来定位和拼接代码,重名会导致歧义。

```python
def collect_all_fn_and_check_name_unique(modules):
    names = {}
    for module_name, module in modules.items():
        for name, fn in get_functions(module):
            names.setdefault(name, []).append(module_name)
    for fn_name, mods in names.items():
        if len(mods) > 1:
            raise RuntimeError("Found duplicated fn", fn_name, mods)
```

---

## 3. 目录结构(骨架)

一个清晰的分层结构是框架可维护的前提:

```text
project/
├── lib/            # 核心能力库:纯函数 + 领域逻辑(可被扫描、可生成脚本)
├── remote/         # 远程脚本引擎:AST 扫描、代码清理、脚本拼接
├── automation/     # 自动化测试用例(pytest / unittest),依赖 lib
├── ci/             # CI 脚本、脚本生成入口、流水线定义
├── dist/           # 自动生成的"全合一"脚本产物(由 ci 生成,纳入版本管理)
├── test/           # 框架自身的单元测试
├── docker/         # devkit 镜像,统一开发/CI 运行环境
├── pyproject.toml  # pytest 配置、marker 定义、Python 版本要求
└── setup.cfg       # 代码风格(行长、排除目录)
```

分层的关键点:

- `lib/` 里只放**可复用的纯能力**,不放测试用例。
- `automation/` 里放**测试用例**,它引用 `lib/` 的能力。
- `dist/` 是**生成物**,但要提交进 git,这样 CI 可以校验"生成物是否和源码同步"。

---

## 4. 核心机制一:Context 上下文(消除参数透传)

为了解决"参数层层透传",框架引入了 **Context** 机制。

思路:把一个"在固定上下文里不变的值"声明成一个**函数**,再用装饰器 `@ctx` 把它变成一个**懒加载的单例**。

```python
@ctx(key="ssh.user")
def get_ssh_user() -> str:
    return "admin"          # 默认值

@ctx(key="ssh.ip")
def get_ssh_ip() -> str:
    ...                     # 没有默认值,必须先 setup
```

`@ctx` 做了什么:

- 第一次调用时执行原函数拿到值并缓存;之后直接返回缓存值。
- 提供 `update()` 用来在运行时注入值(比如连接集群时把真实 IP 塞进去)。
- 提供 `has()` 判断是否已经有值。
- 如果没有默认值又没被 setup,调用时直接抛错,**尽早失败**。

使用时,业务函数直接调用这些 context 函数,不需要把 `user/ip` 一路传下去:

```python
def api(path: str):
    call(f"{get_ssh_ip()}/{path}")   # 直接取,不透传
```

`update` 还支持 callback,值变化时可以触发副作用(例如重新建立连接、打印日志)。

### 4.1 Context 也能当命令行参数

再叠一个装饰器 `@ctx_arg`,同一个 context 就能自动变成 CLI 参数:

```python
@ctx_arg(str)
@ctx(key="ssh.user")
def get_ssh_user() -> str:
    return "admin"
```

框架维护一个全局的"参数注册表",每个 `@ctx_arg` 会往里注册两件事:

- 如何往 `argparse` 里 `add_argument`。
- 解析完命令行后,如何把值 `update` 回对应的 context。

这样"配置项"只声明一次,就同时拥有了:**默认值、运行时注入、命令行覆盖**三种能力。这是一个非常值得在面试里讲的设计。

---

## 5. 核心机制二:Mode 多模式分发(同名函数多实现)

被测系统往往有多种访问方式,例如:

- `local`: 脚本就跑在被测节点上,直接读本地文件。
- `remote`: 从开发机远程调用管理接口。
- `ssh`: 只通过 SSH 命令访问。

框架用 `@current_mode` + `register_mode` 实现"**一个函数名,多套实现,运行时按模式分发**"。这本质是"策略模式 + 多重分发"。

```python
@current_mode("local")
def list_nodes() -> list[str]:
    # 本地实现:直接读节点上的网络配置文件
    with open("/path/to/network.json") as f:
        return [n["ip"] for n in json.load(f)["cluster_info"]]

@register_mode(list_nodes, "remote")
def _():
    # 远程实现:调用管理接口拿节点列表
    return [n["ip"] for n in get_data_nodes()["node"]]
```

调用方永远只写 `list_nodes()`,框架根据当前 `mode.access` 这个 context 决定用哪套实现:

```python
def wrapper(*args, **kwargs):
    return mode_func[get_access_mode()](*args, **kwargs)
```

好处:

- 调用方**无感知**,业务代码不用写一堆 `if mode == ...`。
- 每种模式的实现独立、可单独测试。
- 新增一种访问模式,只要补一个 `register_mode` 即可,符合开闭原则。

---

## 6. 核心机制三:跨平台优雅降级

开发机是 Windows,被测节点是 Linux。有些模块只有 Linux 才有(例如 `fcntl`)。
框架用一个统一入口做**优雅降级**:能导入就用真的,导入不了就替换成一个"占位模块"。

```python
class PlatformModule:
    def __init__(self, name):
        self.name = name

try:
    import fcntl
    fcntl = fcntl
except ImportError:
    fcntl = _module_that_not_support("fcntl")   # 占位,真正调用时才报错
```

这样代码在 Windows 上也能正常 import、正常跑单元测试,只有真正用到该平台能力时才失败。避免了"因为一个平台专用依赖导致整个框架在开发机上跑不起来"。

---

## 7. 核心机制四(杀手锏):远程 Python —— 把函数打包成"全合一"脚本

这是整个框架最有价值、面试最能打的部分。

### 7.1 要解决的问题

我想在开发机上写一个普通 Python 函数,然后**一键把它变成一个不依赖任何第三方库的单文件脚本**,直接扔到被测节点上用 `python3 xxx.tool.py` 跑。节点上:

- 没有这个项目的代码。
- 没有 pip、没有第三方库。
- Python 版本可能比较旧。

### 7.2 用法

给函数加一个装饰器,声明它是"工具函数":

```python
@tool_function()
def hello_world(user: str = None):
    return "hello world" if user is None else f"hello {user}"
```

跑一次扫描脚本,就会在 `dist/hello_world.tool.py` 生成一个**自包含**的脚本。文件名用 `.tool.py` 是个小技巧:避免 IDE 把它当成库来索引。

```bash
python3 hello_world.tool.py
python3 hello_world.tool.py --user alice
```

### 7.3 内部原理(重点)

生成过程分几步,核心是**用 AST 做静态分析**:

| 阶段 | 作用 |
|------|------|
| Clean up | 处理不同 Python 版本 AST 节点差异,保证生成的代码兼容旧版本 |
| Filter Decorator | 把框架自己的装饰器(如 `@tool_function`)从生成代码里剥掉 |
| Scan Code | 递归扫描函数用到的所有变量、子函数、import,收集依赖 |

关键逻辑:

1. 用 `inspect.getsource` 拿到函数源码,`ast.parse` 成语法树。
2. 遍历语法树里的每个 `Name` 节点,判断它是:
   - **标准库 / 白名单模块** → 记录成 `import`,允许。
   - **第三方非白名单模块** → 直接**报错**(远程环境没有,不能用)。
   - **项目内的其它函数** → 递归把那个函数也扫描进来。
   - **普通变量** → 把值序列化进脚本。
3. 把所有依赖去重后,拼成一个带 import、带函数声明、带 `if __name__ == '__main__'` 入口的完整脚本。
4. 如果函数有参数,自动生成 `argparse` 代码,让脚本支持命令行参数。

还有两个增强:

- `@tool_meta(saveOutput="result.json")`: 让脚本把返回值写成 JSON 文件,方便远程执行后把结果拉回本地。
- **inline tools**: 一个工具函数可以内联另一个工具函数,支持"节点上再去 SSH 别的节点"这种多跳场景。

### 7.4 本地/远程统一调用

框架还封装了 `ssh_remote_node(ip).exec(fn, **kwargs)`:

```python
node = ssh_remote_node(user, passwd, ip)
result = node.exec(collect_local_node_status)   # 直接拿到远程返回的对象
```

它内部做的事:

1. 把目标函数生成脚本 → 上传到远程 `/tmp`。
2. `ssh` 执行 `python3 script.tool.py ...`。
3. 如果声明了 `saveOutput`,把远程 JSON 结果下载回本地并反序列化返回。

调用方写起来就**像调用一个本地函数一样**,底层的"生成脚本 + 上传 + 执行 + 回传结果"全部被隐藏。

---

## 8. SSH 层封装

远程能力的底座是一层 SSH 封装(基于 `paramiko` + `scp`):

- `ssh_text_cmd`: 执行命令并返回 stdout,非 0 退出码时打印 stdout/stderr 并抛错。
- `ssh_cmd` / `ssh_call`: 分别返回输出 / 返回退出码。
- `ssh_upload` / `ssh_download` / `ssh_scp`: 文件传输。
- `ssh_upload_or_cache`: **带 sha256 缓存的上传**——先算本地文件哈希,和远程 `.sha256` 比对,一样就跳过上传。配合线程锁避免并发重复上传。

这个"上传前先比哈希"的小优化,在反复调试、频繁上传同一个脚本时能显著提速,是很实用的工程细节。

---

## 9. 测试层:pytest + 测试管理平台同步

框架本身是诊断工具,但上层用它写**自动化测试用例**。

### 9.1 用例写法

用例基于 `unittest.TestCase`,`setUp` 里统一连接集群:

```python
class CaseTemplate(unittest.TestCase):
    def setUp(self):
        setup_cluster()          # 注入 SSH / 管理接口 / 测试平台 token 等 context

    @qtest_case("Feature 名", "用例名", release_meta=..., type_name="Automation")
    def test_ok(self):
        print("Test OK")
```

`setup_cluster()` 是"连接编排",一次性把 SSH、管理网关、测试平台的 context 全部 setup 好——这正是第 4 节 context 机制的价值体现。

### 9.2 用装饰器把结果同步到测试管理平台

`@qtest_case` 装饰器把"执行用例"和"上报结果"解耦:

- 执行前:在测试管理平台按 `模块 / 特性 / 类型` 的层级**幂等地**创建 Test Case、Cycle、Suite、Run(存在就复用,不存在才创建)。
- 执行中:计时、捕获异常。
- 执行后:根据 pass/fail 调用平台 API 写回执行记录,并把结果存进一个全局列表。

它还支持**参数化用例**:用例名可以是一个函数,根据参数动态生成名字,这样一个 `test_xxx` 里循环跑多组数据,每组都在平台上是一条独立记录。

### 9.3 conftest 汇总结果

`conftest.py` 用 `pytest_sessionfinish` 钩子在整个测试会话结束时,把全局结果列表汇总成 `execution_results.json`(总数 / 通过数 / 明细),供流水线归档。

### 9.4 pytest 的两个关键配置

`pyproject.toml` 里有两个值得学的配置:

```toml
[tool.pytest.ini_options]
# 关掉 pytest 对普通 test_ 函数的自动收集,只跑 TestCase 里的方法
python_functions = "invalid_test_function_name_that_never_be_matched"
# 实时输出 stdout,长任务能看到进度,而不是跑完才一次性打印
addopts = "--capture=tee-sys"
markers = [ "smoke_tier1", "regression_tier2", ... ]   # 用 marker 分层/分类用例
```

用 `markers` 给用例打标签(冒烟、回归、按硬件类型等),运行时用 `-m "regression_tier2"` 选择性执行。

---

## 10. CI 流水线:三道质量闸门

CI(以 Jenkins 为例)在 Docker 里跑,保证环境统一。核心有三个 stage:

1. **CodeStyle**: 跑 `pycodestyle`,风格不合格直接失败,并把报告回帖到 PR。
2. **Test**: 先跑脚本生成(`scan_all.py`),再跑单元测试并产出 JUnit XML。
3. **Check(生成物一致性闸门)**: 重新生成 `dist/` 后执行 `git diff --exit-code`。如果生成物和提交的不一致,就说明有人改了工具函数但**没重新生成脚本**,直接失败并提示去跑"刷新脚本"的 Job。

第 3 点是这个框架很聪明的地方:**把"生成物必须和源码同步"变成一道自动化闸门**,避免生成脚本长期腐化。

统一的 devkit Docker 镜像保证了"本地、CI、被测环境"三方 Python 行为一致,减少"在我机器上是好的"这类问题。

---

## 11. 从 0 到 1 的搭建顺序(可直接照做)

如果让你从零重建这样一个框架,推荐顺序:

1. **定分层与规范**: 建 `lib / automation / ci / test` 目录,配 `pyproject.toml`(Python 版本、pytest、marker)和代码风格。
2. **做 Context**: 先实现 `@ctx`(懒加载单例 + update/has),这是消除参数透传的地基。
3. **做参数系统**: 加全局参数注册表和 `@ctx_arg`,让配置项同时支持默认值/注入/命令行。
4. **封装 SSH**: 基于 paramiko 封装命令执行、文件传输、带哈希缓存的上传。
5. **做 Mode 分发**: 实现 `@current_mode` / `register_mode`,支持同名函数多实现。
6. **做跨平台降级**: 用 try/except import 统一处理平台专用模块。
7. **做远程 Python(核心)**: 用 AST 扫描依赖 → 拼装自包含脚本 → 封装 `remote_node.exec()`。
8. **做脚本生成 + 唯一性校验**: 扫描全仓库工具函数,校验函数名唯一,生成到 `dist/`。
9. **搭测试层**: `TestCase + setUp 连接编排 + @结果上报装饰器 + conftest 汇总`。
10. **搭 CI 三闸门**: 风格、单测、生成物一致性;全部在统一 Docker 镜像里跑。

---

## 12. 这套框架的设计亮点小结(面试用)

- **Function First**: 用纯函数 + 装饰器组合能力,而不是庞大继承体系。
- **Context 机制**: 把配置声明成懒加载函数,消除参数透传,还能一键升级成 CLI 参数。
- **Mode 多重分发**: 一个函数名多套实现,调用方无感知,新增模式零侵入。
- **远程 Python 代码生成**: AST 静态分析把函数打包成零依赖单文件脚本,直接在受限的远程环境运行。
- **优雅降级**: 跨平台依赖不阻塞本地开发。
- **测试与上报解耦**: 装饰器负责同步测试管理平台,用例本身保持干净。
- **CI 生成物闸门**: 用 git diff 强制保证生成脚本与源码同步。

这些点合起来能证明一件事:**这个测试框架确实是从 0 到 1 自己设计并搭建的**,而不是套用现成模板。

---

# 附录:用 Vibe Coding 搭这个框架 —— 怎么写 Prompt

下面这部分是**给 AI coding agent(Cascade / Claude / Cursor 等)写提示词**的实战方法,目标是模仿上面这套框架,从零搭一个新的诊断 / 自动化测试框架。核心思路:**不要一句话让它全写完,而是给足上下文 + 分阶段 + 每阶段给验收标准**。

## A. 写 Prompt 的 6 条原则

1. **先给"总纲",再分阶段**: 先用一段 prompt 把项目背景、设计哲学、目录结构、技术栈、路线图讲清楚,让 agent 建立全局认知;然后一个机制一个 prompt 地推进。
2. **每个阶段都要有验收标准**: 明确"做完长什么样",最好带一个能跑的例子和一个单元测试。没有验收标准,agent 很容易写一半跑偏。
3. **给接口签名,不给实现**: 你来定装饰器 / 函数的**对外接口**(名字、参数、返回值),让 agent 填实现。接口是契约,能防止它乱发挥。
4. **强约束写进 prompt**: 例如"函数名全局唯一""生成脚本不能依赖第三方库""必须兼容 Python 3.6 的旧节点"——这些约束要反复强调,否则会被忽略。
5. **要求先写测试**: 让 agent 每个机制都配 `pytest` 单测,先测后写或同步写,保证可回归。
6. **让它自检**: 每阶段结束要求它跑测试 / 跑生成脚本 / 跑 `git diff`,把结果贴出来,而不是口头说"完成了"。

## B. 总纲 Prompt(第一条,复制即用)

> 你是一名资深 Python 框架工程师。我要从零搭建一个面向分布式系统的**诊断 + 自动化测试框架**,请严格按我给的设计哲学和路线图来,我会分阶段让你实现,现在只需要先搭骨架并确认理解。
>
> **背景**:
> - 被测系统(SUT)运行在 Linux 集群(多节点)上。
> - 开发机是 Windows/Mac,被测节点是 Linux,存在跨平台依赖问题(如 `fcntl` 只有 Linux 有)。
> - 既要能从开发机远程连集群诊断,又要能把脚本直接部署到节点上跑,规避跨站点慢通信。
> - 被测节点上没有 pip、没有第三方库、Python 版本可能很旧(假设最低 3.6)。
>
> **设计哲学(必须遵守)**:
> 1. **Function First**:业务能力用纯函数表达,一个函数做一件事;横切关注点(配置、缓存、模式切换、上报)用**装饰器**叠加,不要用庞大的类继承体系。
> 2. **函数名全局唯一**:CI 会扫描所有模块,发现重名函数直接报错(因为脚本生成靠函数名定位)。
> 3. **尽早失败**:缺配置、缺依赖时在调用点立刻抛错,给出清晰信息。
>
> **技术栈**:Python 3.11+ 开发;`paramiko` + `scp` 做 SSH;`pytest` + `unittest.TestCase` 做测试;`ast` / `inspect` 做代码生成;Docker 做统一 devkit;CI 用 Jenkins(Groovy Pipeline)。
>
> **目录结构**:
> ```text
> project/
> ├── lib/          # 核心能力库:纯函数 + 装饰器(context / mode / cross_platform / remote_python)
> ├── remote/       # 远程脚本引擎:AST 扫描、清理、拼接
> ├── automation/   # 自动化测试用例(TestCase),依赖 lib
> ├── ci/           # scan_all.py 脚本生成入口 + Jenkinsfile
> ├── dist/         # 自动生成的全合一脚本(纳入 git)
> ├── test/         # 框架自身单测
> ├── docker/       # devkit 镜像
> ├── pyproject.toml
> └── setup.cfg
> ```
>
> **路线图**(后面我会一个阶段一个阶段让你做,现在别提前写):
> Phase 0 脚手架 → 1 Context → 2 CLI 参数 → 3 SSH 封装 → 4 Mode 分发 → 5 跨平台降级 → 6 远程 Python 代码生成 → 7 scan_all + 唯一性校验 + dist → 8 测试层 + 结果上报 → 9 CI 三闸门。
>
> **现在只做 Phase 0**:创建上面的目录结构、空 `__init__.py`、`pyproject.toml`(配置 `requires-python`、pytest 的 `python_functions` 关闭自动收集、`addopts=--capture=tee-sys`、`markers`)、`setup.cfg`(pycodestyle 行长和排除目录)、一个 `README.md`。做完把目录树和两个配置文件内容贴出来,并复述你对设计哲学的理解。**先不要实现任何机制。**

## C. 分阶段 Prompt 模板

每个阶段都用同一个结构:**目标 → 接口契约 → 约束 → 验收(含单测)**。下面给出关键几阶段的现成 prompt。

### Phase 1 — Context(消除参数透传)

> 实现 `lib/context.py`,提供 `@ctx` 装饰器,把"在固定上下文里不变的值"声明成懒加载单例。
>
> **接口契约**:
> ```python
> @ctx(key="ssh.user")
> def get_ssh_user() -> str:
>     return "admin"        # 有默认值
>
> @ctx(key="ssh.ip")
> def get_ssh_ip() -> str:
>     ...                   # 无默认值,未 setup 时调用要抛错
> ```
> - 第一次调用执行原函数并缓存,之后返回缓存。
> - `get_ssh_user.update(value, callback=None)`:运行时注入值,值变化可触发 callback。
> - `get_ssh_user.has() -> bool`:是否已有值。
> - 无默认值且未 setup 时调用 → 抛 `RuntimeError`,信息里带 key。
>
> **验收**:写 `test/test_context.py`,覆盖默认值、update 后取值、has()、无默认值抛错、callback 被触发。跑 `pytest test/test_context.py` 并贴结果。

### Phase 2 — CLI 参数(ctx_arg)

> 在 `lib/context.py`(或 `lib/args.py`)增加 `@ctx_arg(type)`,叠在 `@ctx` 之上,让同一个 context 自动变成命令行参数。维护一个全局参数注册表,每个 `@ctx_arg` 注册:(1) 如何 `argparse.add_argument`;(2) 解析后如何 `update` 回 context。提供 `build_arg_parser()` 和 `apply_args(namespace)`。
>
> **约束**:配置项只声明一次,就同时具备"默认值 / 运行时注入 / 命令行覆盖"三种能力。
>
> **验收**:单测模拟 `--ssh-user alice`,断言解析后 `get_ssh_user()` 返回 `alice`。

### Phase 3 — SSH 封装

> 实现 `lib/ssh.py`,基于 `paramiko` + `scp`:
> - `ssh_text_cmd(ip, cmd) -> str`:执行并返回 stdout;非 0 退出码打印 stdout/stderr 并抛错。
> - `ssh_cmd` / `ssh_call`:分别返回输出 / 退出码。
> - `ssh_upload` / `ssh_download` / `ssh_scp`:文件传输。
> - `ssh_upload_or_cache`:**带 sha256 缓存的上传**——先算本地哈希,和远程 `.sha256` 比对,一样就跳过;用线程锁避免并发重复上传。
> - SSH 账号/IP 从 Phase 1 的 context 取,不要透传。
>
> **验收**:用 mock(monkeypatch paramiko)写单测,验证缓存命中时不重复上传。

### Phase 4 — Mode 多模式分发

> 实现 `lib/mode.py`:`@current_mode("local")` 声明默认实现,`@register_mode(fn, "remote")` 注册同名函数的另一套实现;运行时按 context `mode.access` 分发。调用方只写 `list_nodes()`,不写 `if mode==`。
>
> **验收**:定义一个 `list_nodes`,注册 local/remote 两套,切换 mode context 断言走到不同实现。

### Phase 5 — 跨平台优雅降级

> 实现 `lib/cross_platform.py`:统一入口 import 平台专用模块(如 `fcntl`),能 import 就用真的,`ImportError` 时替换成占位对象——占位对象在**真正被调用时**才抛"当前平台不支持"的错。保证框架在 Windows 上能正常 import 和跑单测。
>
> **验收**:单测在模拟无 `fcntl` 时,import 不报错,调用占位属性才报错。

### Phase 6 — 远程 Python 代码生成(核心)

> 这是框架最核心的能力。实现 `remote/` 下的引擎和 `lib/remote_python.py` 的 `@tool_function()` 装饰器。
>
> **目标**:给一个普通函数加 `@tool_function()`,扫描后能生成一个**零第三方依赖的单文件脚本**,直接在旧版 Python 的远程节点上跑。
>
> **接口**:
> ```python
> @tool_function()
> def hello_world(user: str = None):
>     return "hello world" if user is None else f"hello {user}"
> ```
> 生成到 `dist/hello_world.tool.py`,支持 `python3 hello_world.tool.py --user alice`。
>
> **内部实现(必须用 AST)**:
> 1. `inspect.getsource` 拿源码,`ast.parse` 成语法树。
> 2. 遍历 `Name` 节点判断依赖:标准库/白名单 → 记 import;第三方非白名单 → **报错**;项目内其它函数 → 递归扫描;普通变量 → 序列化进脚本。
> 3. Clean up:抹平不同 Python 版本 AST 差异,保证兼容旧版本。
> 4. Filter Decorator:把框架自己的装饰器(`@tool_function` 等)从生成代码里剥掉。
> 5. 依赖去重后拼成完整脚本:import + 函数声明 + `if __name__ == '__main__'` 入口。
> 6. 函数有参数时自动生成 `argparse`。
>
> **增强**:`@tool_meta(saveOutput="result.json")` 让脚本把返回值写成 JSON;支持工具函数内联另一个工具函数(多跳 SSH)。
>
> **约束**:生成脚本严禁出现第三方 import;必须能在 Python 3.6 下运行。
>
> **验收**:对 `hello_world` 生成脚本,用子进程 `python3 dist/hello_world.tool.py --user alice` 跑,断言输出 `hello alice`;再写一个引用了第三方库的工具函数,断言生成时报错。

### Phase 6.5 — 本地/远程统一调用

> 封装 `ssh_remote_node(user, passwd, ip).exec(fn, **kwargs)`:内部把目标函数生成脚本 → 上传远程 `/tmp` → `python3` 执行 → 若声明 `saveOutput` 则把 JSON 结果下载回本地反序列化返回。调用方像调本地函数一样。

### Phase 7 — scan_all + 唯一性校验 + dist 一致性

> 实现 `ci/scan_all.py`:扫描全仓库所有 `@tool_function`,**校验函数名全局唯一**(重名抛错),逐个生成到 `dist/`。生成物纳入 git。
>
> **验收**:跑 `python ci/scan_all.py` 生成 `dist/`,再 `git diff --exit-code` 应无差异;构造一个重名函数,断言 scan 报错。

### Phase 8 — 测试层 + 结果上报

> 实现 `automation/` 用例模板:基于 `unittest.TestCase`,`setUp` 里 `setup_cluster()` 一次性 setup 好 SSH / 管理接口 / 测试平台 token 的 context。实现 `@report_case(feature, name, type_name="Automation")` 装饰器:执行前在测试管理平台按 模块/特性/类型 层级**幂等**创建记录,执行中计时捕获异常,执行后按 pass/fail 写回并存进全局结果列表。支持参数化(name 可为函数)。`conftest.py` 用 `pytest_sessionfinish` 汇总成 `execution_results.json`。
>
> **验收**:mock 平台 API,跑一个通过和一个失败用例,断言 `execution_results.json` 里 total/passed/明细正确。

### Phase 9 — CI 三闸门

> 写 `ci/*.Jenkinsfile.groovy`,在统一 Docker devkit 里跑三个 stage:
> 1. **CodeStyle**:`pycodestyle`,不合格失败并回帖 PR。
> 2. **Test**:先 `python ci/scan_all.py`,再 `pytest` 出 JUnit XML。
> 3. **Check**:重新生成 `dist/` 后 `git diff --exit-code`,不一致则失败并提示去跑"刷新脚本"Job。
>
> **验收**:本地用 Docker 复现三个 stage 全绿。

## D. 迭代 / 调试时的 Prompt 技巧

- **贴报错原文**: 报错时把完整 traceback 贴给 agent,并说"只改导致这个错的最小范围,不要重构其它部分"。
- **钉住接口**: 如果它擅自改了你定义的装饰器签名,直接说"接口是契约,恢复成 XXX,只改内部实现"。
- **一次一个关注点**: 不要同一条消息里既让它加功能又让它改风格,容易互相干扰。
- **要求最小 diff**: "用最小改动修复,单行能解决就不要写十行。"(呼应本仓库的 bug fixing 原则)
- **让它自证**: "把你新增/修改的测试和 `pytest` 输出贴出来再说完成。"

## E. 最终验收 Checklist(交给 agent 逐条确认)

```text
[ ] 目录分层清晰:lib / remote / automation / ci / dist / test / docker
[ ] @ctx 懒加载单例,支持 update/has/callback,无默认值未 setup 调用即抛错
[ ] @ctx_arg 让配置项同时支持 默认值 / 注入 / 命令行
[ ] SSH 封装齐全,上传带 sha256 缓存 + 并发锁
[ ] @current_mode / register_mode 同名多实现,调用方无感知
[ ] cross_platform 优雅降级,Windows 上能 import 和跑单测
[ ] @tool_function 用 AST 生成零依赖单文件脚本,兼容旧 Python
[ ] 第三方依赖在生成时报错;@tool_meta(saveOutput) 可回传 JSON
[ ] scan_all 校验函数名全局唯一,dist 生成物与源码一致(git diff 干净)
[ ] TestCase + setUp 连接编排 + 结果上报装饰器 + conftest 汇总
[ ] CI 三闸门(风格 / 单测 / 生成物一致性)在统一 Docker 里全绿
```

把这份 Checklist 贴给 agent,让它逐条对照自查,是收尾时最高效的一步。
