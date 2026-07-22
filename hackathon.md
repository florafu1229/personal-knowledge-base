# AI ObjectScale Stability Insights - Hackathon 项目详解

## 项目背景

这是一个在 AI Hackathon 中开发的**智能化 DT (Directory Table) 稳定性分析系统**，旨在解决 ObjectScale/ECS 存储系统中 DT 初始化慢和稳定性问题的诊断难题。通过结合**日志可视化**和 **RAG (检索增强生成)** 技术，实现了从日志解析到智能问答的端到端自动化分析。

**核心问题：**
- DT 初始化慢是 ObjectScale 系统启动的主要瓶颈
- 多个 DT 类型（OB、CT、SS 等）之间存在复杂的依赖关系
- 传统人工分析日志耗时长、效率低、容易遗漏关键信息

**解决方案：**
- **可视化时间线：** 自动解析日志生成 DT 初始化时间线图表，直观展示各 DT 类型的启动顺序和耗时
- **AI 智能问答：** 基于 RAG 架构，结合向量化知识库和大语言模型，提供 DT 稳定性问题的智能诊断建议

---

## 技术架构

### 整体架构图

```
┌─────────────────────────────────────────────────────┐
│                 Frontend (UI)                       │
│  • Node-less UI: FastAPI-served HTML/JS + ECharts   │
│  • DT timeline visualization with merged events     │
│  • AI chat interface with streaming response        │
└─────────────────────────────────────────────────────┘
                         │ HTTP/REST
┌─────────────────────────────────────────────────────┐
│                Backend (FastAPI)                     │
│  • /api/charts/dt-init – DT init timeline chart     │
│  • /api/chat          – AI chat (RAG + AIA LLM)      │
│  • /api/models        – List available models        │
│  • /                  – Node-less UI entry point     │
└─────────────────────────────────────────────────────┘
                         │
┌─────────────────────────────────────────────────────┐
│               Core Services                         │
│  • charts.py        – DT init chart endpoint        │
│  • dt_parser.py     – Log parsing & event merging   │
│  • chat.py          – RAG + AIA LLM routing          │
│  • knowledge.py     – Vectorized DT handbook (ChromaDB)│
└─────────────────────────────────────────────────────┘
                         │
┌─────────────────────────────────────────────────────┐
│               Data & Knowledge                       │
│  • knowledge/dt_init_slow.md – DT init slowness guide│
│  • knowledge/system_handbook.md – System handbook   │
│  • knowledge/dt_patterns.yaml – Regex patterns      │
│  • knowledge/dt_types.yaml – DT type definitions    │
│  • sample-logs/           – Demo logs (blobsvc, cm, ssm)│
│  • data/chroma/           – ChromaDB vector store   │
└─────────────────────────────────────────────────────┘
```

### 技术栈

| 层次 | 技术选型 | 作用 |
|------|---------|------|
| **Web 框架** | FastAPI | 高性能异步 Web 框架，自动生成 API 文档 |
| **前端** | HTML/JS + ECharts | Node-less 架构，无需 npm/webpack，直接 CDN 加载 |
| **日志解析** | Python + YAML + Regex | 基于 YAML 配置的正则表达式模式匹配 |
| **可视化** | ECharts | 交互式时间线图表，支持缩放、拖拽、事件合并 |
| **向量数据库** | ChromaDB | 本地持久化向量存储，无需外部数据库 |
| **Embedding** | Nomic-embed-text-v1-5 (AIA Gateway) | 将文本转换为 768 维向量 |
| **LLM** | 多模型支持 (AIA Gateway) | gpt-oss-120b, llama-3-3-70b-instruct 等 |
| **认证** | aia-auth-client | Dell 企业 SSO 认证 |

---

## 核心功能模块

### 1. 日志解析与事件提取 (dt_parser.py)

**功能：** 从 ECS 服务日志中自动提取 DT 初始化事件

**技术实现：**
- **YAML 驱动的模式匹配：** 通过 `dt_patterns.yaml` 和 `dt_types.yaml` 定义不同 DT 类型的日志模式
- **多服务日志支持：** blobsvc.log (OB), cm.log (CT), ssm.log (SS)
- **正则表达式引擎：** 动态构建正则表达式，提取 DT ID、时间戳、事件类型
- **时间解析：** 使用 `dateutil.parser` 解析多种时间格式

**关键代码逻辑：**
```python
# 从 YAML 加载 DT 类型配置
dt_types = yaml.safe_load(types_file.read_text())

# 为每个 DT 类型构建正则表达式
for dt_type, config in dt_types.items():
    start_markers = config.get("log_patterns", {}).get("init_start", [])
    end_markers = config.get("log_patterns", {}).get("init_end", [])
    
    # 动态构建 DT ID 正则表达式
    dt_id_regexes = [
        re.compile(rf"(?P<dt_id>{prefix}_\d+_{suffix}_\d+)"),  # OB_*_128_0
        re.compile(rf"(?P<dt_id>urn:[^\s,]*{prefix}[^\s,]*)")   # urn:...OB_*
    ]
```

**支持的 DT 类型：**
- **OB (ObjectBucket):** 对象存储服务
- **CT (ContainerTable):** 容器元数据服务
- **SS (StorageSystem):** 系统协调服务
- **PR, RR, BR, MR, RT, LS, ET** 等其他 DT 类型

**事件合并功能：**
- 将同一 DT 类型的多个实例合并为一个时间线条目
- 显示最早开始时间和最晚结束时间
- 简化时间线可视化，突出关键依赖关系

### 2. 时间线图表生成 (charts.py)

**功能：** 生成交互式 DT 初始化时间线图表

**技术实现：**
- **FastAPI 端点：** `POST /api/charts/dt-init`
- **ECharts 集成：** 返回 JSON 数据，前端渲染为 Gantt 图
- **事件数据结构：**
  ```python
  @dataclass
  class DtInitEvent:
      dt_type: str          # DT 类型 (OB, CT, SS)
      dt_id: str            # DT 实例 ID
      start_ts: str         # 开始时间戳
      end_ts: Optional[str] # 结束时间戳
      duration_sec: float   # 持续时间（秒）
      service_name: str     # 服务名称
  ```

**图表特性：**
- **颜色编码：** 不同 DT 类型使用不同颜色（低饱和度灰蓝色系）
- **交互式：** 支持缩放、拖拽、悬停显示详情
- **事件合并：** 可选择是否合并同类型 DT 事件
- **时间轴：** 自动计算时间范围，精确到秒

### 3. RAG 智能问答 (chat.py + knowledge.py)

**功能：** 基于向量化知识库的 DT 稳定性问题智能问答

**RAG 工作流程：**
```
用户问题 → 向量检索 (Top-K) → 上下文构建 → LLM 生成答案
              ↓
         ChromaDB
     (DT Handbook 向量)
```

**技术实现：**

#### 3.1 知识库向量化 (knowledge.py)
```python
class DtKnowledgeBase:
    def __init__(self):
        # 使用 ChromaDB 本地持久化存储
        chroma_path = ai_chart_dir() / "data" / "chroma"
        self.client = chromadb.PersistentClient(path=str(chroma_path))
        self.collection = self.client.get_or_create_collection("dt_handbook")
        
        # 自动索引 knowledge/ 目录下的所有 .md 文件
        self._maybe_index()
    
    def _chunk(self, text: str, max_len: int = 200) -> list[str]:
        # 将文档切分成小块（200 字符），避免 payload 过大
        # 按段落切分，保持语义完整性
        
    def _embed(self, texts: list[str]) -> list[list[float]]:
        # 调用 AIA Gateway 的 Nomic-embed-text-v1-5 模型
        # 返回 768 维向量
```

**知识库内容：**
- `dt_init_slow.md`: DT 初始化慢的 7 大根因分析
  1. **Large B+tree Size** - B+树过大导致加载慢
  2. **High Disk I/O Latency** - 磁盘 I/O 延迟高
  3. **Network Communication Delays** - 网络通信延迟
  4. **Resource Contention** - 资源竞争
  5. **Dependency Initialization** - 依赖初始化慢
  6. **Configuration Issues** - 配置问题
  7. **Software Bugs** - 软件缺陷

- `system_handbook.md`: 系统架构和组件说明

#### 3.2 RAG 检索与生成 (chat.py)
```python
@chat_router.post("/chat")
def chat(req: ChatRequest) -> ChatResponse:
    # 1. 向量检索：从知识库中检索最相关的 Top-K 文档片段
    results = _kb.query(req.message, top_k=5)
    
    # 2. 上下文构建：将检索到的片段拼接成上下文
    context = "\n\n".join([r["text"] for r in results])
    
    # 3. Prompt 构建：限定 LLM 只能基于上下文回答
    prompt = f"""
    You are an expert at ObjectScale DT stability analysis.
    Answer the user's question using ONLY the context below.
    If the context does not contain the answer, say you don't know.
    
    Context:
    {context}
    
    Question: {req.message}
    """
    
    # 4. LLM 生成：调用 AIA Gateway 的 LLM 模型
    response = _call_aia_llm(req.model, prompt)
    
    return ChatResponse(answer=response)
```

**支持的 LLM 模型（AIA Gateway）：**
- `gpt-oss-20b` / `gpt-oss-120b` - Dell 内部 GPT 模型
- `llama-3-3-70b-instruct` - Meta Llama 3.3 70B
- `codellama-13b-instruct` - Code-specialized Llama
- `gemma-3-27b-it` - Google Gemma 3 27B
- `mistral-small-3-1-24b-instruct-2503` - Mistral Small

### 4. Node-less 前端架构 (web_ui.py + static/)

**设计理念：** 无需 Node.js/npm/webpack，直接通过 FastAPI 提供静态 HTML/JS

**技术实现：**
```python
# web_ui.py
web_ui_router = APIRouter(tags=["web_ui"])

@web_ui_router.get("/")
def index():
    return FileResponse("app/static/index.html")

@web_ui_router.get("/static/{file_path:path}")
def static_files(file_path: str):
    return FileResponse(f"app/static/{file_path}")
```

**前端技术栈：**
- **HTML/CSS/JavaScript** - 原生 Web 技术
- **ECharts CDN** - 通过 CDN 加载图表库，无需本地打包
- **Fetch API** - 调用后端 REST API

**UI 功能：**
- **日志目录选择：** 输入本地日志目录路径
- **图表类型选择：** DT Timeline / Pass Rate Chart
- **DT 类型过滤：** 多选框选择要显示的 DT 类型
- **事件合并开关：** 是否合并同类型 DT 事件
- **AI 聊天界面：** 模型选择 + 问答输入框 + 流式响应显示

---

## 项目亮点

### 1. YAML 驱动的可扩展日志解析

**优势：**
- **配置化：** 新增 DT 类型无需修改代码，只需编辑 YAML 配置
- **灵活性：** 支持多种日志格式和正则表达式模式
- **可维护性：** 日志模式集中管理，易于更新和调试

**示例配置 (dt_types.yaml)：**
```yaml
dt_types:
  OB_128_0:
    service_name: "ObjectBucketService"
    log_file_prefix: "blobsvc"
    category: "Storage"
    priority: "High"
    chart_color: "#6B7280"
    log_patterns:
      init_start: "initialize DT|DT initialization started"
      init_end: "initialize done|DT initialization completed"
```

### 2. 事件合并算法

**问题：** 一个集群可能有数百个 OB DT 实例，时间线图表会非常拥挤

**解决方案：**
```python
def merge_events_by_type(events: list[DtInitEvent]) -> list[DtInitEvent]:
    """将同一 DT 类型的多个事件合并为一个"""
    grouped = {}
    for event in events:
        if event.dt_type not in grouped:
            grouped[event.dt_type] = []
        grouped[event.dt_type].append(event)
    
    merged = []
    for dt_type, group in grouped.items():
        # 找到最早开始时间和最晚结束时间
        start_ts = min(e.start_ts for e in group)
        end_ts = max(e.end_ts for e in group if e.end_ts)
        
        merged.append(DtInitEvent(
            dt_type=dt_type,
            dt_id=f"{dt_type} (merged {len(group)} instances)",
            start_ts=start_ts,
            end_ts=end_ts,
            duration_sec=(end_ts - start_ts).total_seconds()
        ))
    
    return merged
```

### 3. RAG 架构的智能问答

**相比纯 LLM 的优势：**
- **准确性：** 基于真实文档片段，减少幻觉
- **可解释性：** 可以追溯答案来源（哪个文档片段）
- **可更新性：** 新增文档后重新索引即可，无需重新训练模型

**Prompt Engineering：**
```python
# 限定上下文策略
prompt = f"""
You are an expert at ObjectScale DT stability analysis.
Answer the user's question using ONLY the context below.
If the context does not contain the answer, say you don't know and suggest contacting the dev team.

Context:
{retrieved_chunks}

Question: {user_question}
"""
```

### 4. Node-less 前端架构

**优势：**
- **零依赖：** 无需 Node.js、npm、webpack
- **快速部署：** 直接运行 FastAPI，无需前端构建步骤
- **简化维护：** 前后端在同一个 Python 进程中，统一管理

**适用场景：**
- 内部工具、Demo、Hackathon 项目
- 不需要复杂前端框架（React/Vue）的场景

### 5. 企业级认证集成

**Dell AIA Gateway 认证：**
```python
from aia_auth import auth

# 自动处理 SSO 登录和 token 刷新
http_client = httpx.Client(auth=auth.AiaAuth())

# 调用 AIA Gateway API
response = http_client.post(
    "https://aia.gateway.dell.com/genai/dev/v1/embeddings",
    json={"input": texts, "model": "nomic-embed-text-v1-5"}
)
```

---

## 使用场景

### 场景 1: DT 初始化慢诊断

**问题：** 集群启动后 DT 初始化耗时 10 分钟，影响业务恢复

**操作流程：**
1. 将日志目录设置为 `/var/log/vipr/`
2. 生成 DT Timeline 图表
3. 观察时间线，发现 OB DT 初始化耗时最长（8 分钟）
4. 在 AI 聊天中提问："Why is OB DT init slow?"
5. 系统检索知识库，返回可能的根因：
   - Large B+tree Size (检查 B+树大小)
   - High Disk I/O Latency (检查磁盘性能)
6. 根据建议执行诊断命令，定位到磁盘 I/O 瓶颈

### 场景 2: DT 依赖关系分析

**问题：** 不清楚 OB、CT、SS 之间的初始化依赖关系

**操作流程：**
1. 生成 DT Timeline 图表（不合并事件）
2. 观察时间线，发现 SS → CT → OB 的启动顺序
3. 在 AI 聊天中提问："What are the dependencies between OB, CT, and SS?"
4. 系统返回依赖关系说明：
   - SS 必须先初始化（系统协调服务）
   - CT 依赖 SS（元数据服务依赖系统服务）
   - OB 依赖 CT（对象存储依赖元数据服务）

### 场景 3: 新人 Onboarding

**问题：** 新加入团队的工程师不熟悉 DT 架构和诊断方法

**操作流程：**
1. 使用 sample-logs 生成示例图表，了解 DT 初始化流程
2. 通过 AI 聊天学习 DT 相关知识：
   - "What is DT in ObjectScale?"
   - "How to troubleshoot DT unready?"
   - "What are the common causes of DT init slow?"
3. 快速掌握 DT 稳定性分析的基础知识

---

## 技术难点与解决方案

### 难点 1: 多种日志格式的统一解析

**问题：** 不同服务的日志格式不一致，时间戳格式多样

**解决方案：**
- 使用 `dateutil.parser` 自动识别多种时间格式
- YAML 配置中定义服务特定的日志模式
- 正则表达式动态构建，支持多种 DT ID 格式

### 难点 2: ChromaDB Payload Too Large

**问题：** 一次性索引大量文档时，Embedding API 返回 payload too large

**解决方案：**
```python
# 批量处理 + 自动降级
batch_size = 10  # 每次处理 10 个 chunks
for i in range(0, total_chunks, batch_size):
    try:
        embeddings = self._embed(batch_chunks)
        self.collection.add(...)
    except Exception as e:
        # 降级为单个 chunk 处理
        self._process_single_chunks(batch_chunks, ...)
```

### 难点 3: AIA 认证在 Windows 环境的兼容性

**问题：** `aia-auth-client` 需要 Dell 内部 PyPI 源，安装复杂

**解决方案：**
```powershell
# 单独安装 aia-auth-client，指定 Dell PyPI 源
pip install aia-auth-client==0.0.8 \
  --trusted-host artifacts.dell.com \
  --extra-index https://artifacts.dell.com/artifactory/api/pypi/agtsdk-1007569-pypi-prd-local/simple
```

### 难点 4: 前端图表性能优化

**问题：** 数百个 DT 事件渲染时，ECharts 性能下降

**解决方案：**
- 实现事件合并功能，减少渲染数量
- 使用 ECharts 的 dataZoom 组件，支持局部渲染
- 前端缓存图表配置，避免重复计算

---

## 项目成果

### Hackathon 期间完成的功能

1. **日志解析引擎：** 支持 OB、CT、SS 三种 DT 类型的日志解析
2. **时间线可视化：** 交互式 DT 初始化时间线图表
3. **RAG 智能问答：** 基于向量化知识库的 AI 助手
4. **Node-less UI：** 零依赖前端架构
5. **企业级认证：** Dell AIA Gateway 集成

### 技术创新点

1. **YAML 驱动的可扩展架构：** 新增 DT 类型无需修改代码
2. **事件合并算法：** 简化时间线可视化
3. **RAG + 日志分析结合：** 将静态知识库和动态日志分析结合
4. **Node-less 前端：** 简化部署和维护

### 实际价值

- **提升诊断效率：** 从人工分析日志（数小时）→ 自动生成图表 + AI 问答（数分钟）
- **降低学习成本：** 新人通过 AI 聊天快速了解 DT 架构和诊断方法
- **知识沉淀：** 将专家经验（7 大根因）向量化，形成可复用的知识库

---

## 未来改进方向

1. **更多 DT 类型支持：** 扩展到 PR、RR、BR、MR 等所有 DT 类型
2. **实时日志监控：** 支持实时日志流解析和告警
3. **根因自动推断：** 基于日志模式自动推断 DT init slow 的根因
4. **多集群对比：** 对比不同集群的 DT 初始化性能
5. **导出报告：** 生成 PDF/Excel 格式的诊断报告
6. **Agent 架构：** 引入 LangChain Agent，支持多步推理和工具调用

---

## 总结

**AI ObjectScale Stability Insights** 是一个完整的 Hackathon 项目，展示了以下技术能力：

- **全栈开发：** FastAPI (后端) + HTML/JS/ECharts (前端)
- **日志解析：** YAML + Regex + 时间解析
- **RAG 架构：** ChromaDB + Nomic Embedding + LLM
- **可视化：** ECharts 交互式时间线图表
- **企业级集成：** Dell AIA Gateway 认证
- **软件工程：** 可扩展架构、配置化设计、批处理优化

这个项目不仅解决了实际问题（DT 初始化慢诊断），也是学习和实践 **RAG、日志分析、可视化、全栈开发** 的优秀案例。
