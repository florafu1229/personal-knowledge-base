# OBS-vectorDB 项目详解

## 项目概述

OBS-vectorDB 是一个为 OBS (ObjectScale) 存储团队打造的**内部知识库问答系统**，基于 **RAG (Retrieval-Augmented Generation)** 架构，使用向量数据库 (Vector Database) 和大语言模型 (LLM) 技术，实现了针对 ObjectScale/ECS 技术文档的智能问答。

**核心价值：** 将分散在 PDF、TXT 等文档中的技术知识转化为可检索的向量数据库，通过自然语言问答的方式快速获取技术信息，提升团队工作效率。

---

## 技术架构

### 1. RAG (Retrieval-Augmented Generation) 架构

```
用户问题 → 向量化 (Embedding) → 向量检索 (Top-K) → 上下文构建 → LLM 生成答案
                ↓                      ↓
          Embedding Model         ChromaDB
          (nomic-embed-text)    (Vector Store)
```

**工作流程：**
1. **文档摄取 (Ingestion)：** 将 PDF/TXT 文档切分成 chunks (1024 字符)，通过 Embedding 模型转换为向量，存储到 ChromaDB
2. **问题检索 (Retrieval)：** 用户提问时，问题同样被向量化，在 ChromaDB 中检索最相关的 Top-5 文档片段
3. **答案生成 (Generation)：** 将检索到的文档片段作为上下文 (Context)，结合用户问题，由 LLM 生成答案

### 2. 核心技术栈

| 组件 | 技术选型 | 作用 |
|------|---------|------|
| **向量数据库** | ChromaDB (Persistent Client) | 存储文档向量，支持相似度检索 |
| **Embedding 模型** | nomic-embed-text-v1-5 | 将文本转换为 768 维向量 |
| **LLM 模型** | llama-3-3-70b-instruct | 基于检索上下文生成答案 |
| **RAG 框架** | LlamaIndex | 提供文档加载、切分、索引、检索、查询引擎 |
| **前端界面** | Streamlit | 提供 Web 聊天界面 |
| **认证系统** | Dell SSO / Client Credentials | 访问 Dell AIA Gateway (GenAI 平台) |

### 3. 关键模块

#### 3.1 文档摄取 (Ingestion)
- **文件格式支持：** PDF, TXT
- **切分策略：** SentenceSplitter (chunk_size=1024, chunk_overlap=0)
- **批量插入：** 每次插入 30 个 chunks，避免内存溢出
- **增量摄取：** 通过 `ingested.txt` 记录已处理文件，避免重复摄取

```python
# 核心代码逻辑
documents = SimpleDirectoryReader(input_files=[file_path]).load_data()
nodes = splitter.get_nodes_from_documents(documents)
for start in range(0, len(nodes), INSERT_BATCH_SIZE):
    index.insert_nodes(nodes[start : start + INSERT_BATCH_SIZE])
```

#### 3.2 向量检索 (Retrieval)
- **检索策略：** 相似度检索 (Similarity Top-K)
- **Top-K 设置：** 默认返回 5 个最相关的文档片段
- **检索模式：** 支持两种模式
  - **Query Engine 模式：** LlamaIndex 内置查询引擎，自动处理检索 + 生成
  - **Manual Retrieval 模式：** 手动检索 → 过滤 → 生成（可自定义 prompt）

#### 3.3 答案生成 (Generation)
- **Prompt 设计：** 限定 LLM 只能基于检索到的上下文回答，避免幻觉 (Hallucination)
- **两阶段生成（可选）：**
  1. **过滤阶段：** LLM 筛选相关片段，生成摘要
  2. **回答阶段：** 基于摘要生成最终答案
- **兜底策略：** 如果检索不到相关内容，返回 "I don't know, please contact dev team"

```python
# Prompt 示例
answer_prompt = (
    "You are an expert at a storage product named ObjectScale.\n"
    "Answer the user's question using ONLY the SUMMARY below.\n"
    "If the SUMMARY does not contain the answer, say you don't know.\n\n"
    f"SUMMARY:\n{excerpts}\n\n"
    f"QUESTION: {question}\n"
)
```

#### 3.4 认证系统 (Authentication)
- **Dell SSO 登录：** 通过浏览器跳转到 Dell SSO 页面，获取 JWT token
- **Client Credentials：** 使用 Client ID + Secret 直接获取 token（无需浏览器）
- **Token 缓存：** JWT token 缓存到本地文件 (`sso_cache`)，自动刷新（过期前 120 秒）
- **证书管理：** 自动下载并安装 Dell PKI 证书到 certifi bundle

```python
# Token 缓存逻辑
def get_cached_sso_session_token(min_ttl_seconds: int = 120) -> str:
    cache = _read_sso_cache(path)
    token = cache.get("access_token")
    expires_at = cache.get("expires_at")
    
    if token and expires_at - now > min_ttl_seconds:
        return token  # 使用缓存
    
    # Token 过期，重新获取
    auth = authentication_provider.AuthenticationProvider()
    token = auth.generate_auth_token()
    _write_sso_cache(path, {"access_token": token, "expires_at": expires_at})
    return token
```

---

## 项目特色

### 1. 工厂模式 (Factory Pattern)
`vectorDBFactory.py` 实现了向量数据库的工厂模式，方便未来扩展支持其他向量数据库（如 Pinecone, Weaviate, Milvus）

```python
def get_vector_index(vector_db_type: str, *, vector_dir: str, collection_name: str):
    if vector_db_type in {"chroma", "chromadb"}:
        return _get_index_from_chroma(vector_dir, collection_name)
    # 未来可扩展其他数据库
    raise ValueError(f"Unsupported vector_db_type: {vector_db_type}")
```

### 2. 聊天历史持久化
- 支持将聊天记录保存到本地文件 (`history/chat_history_<timestamp>.txt`)
- 格式化输出：`### user query ###` + `### answer from bot ###`

### 3. Streamlit 缓存优化
- 使用 `@st.cache_resource` 缓存 Embedding 模型、LLM、向量索引
- 避免每次查询都重新加载模型，显著提升响应速度

### 4. 增量摄取 (Incremental Ingestion)
- 通过 `ingested.txt` 记录已处理文件路径
- 新增文档时只处理新文件，避免重复计算向量

---

## 使用场景

### 场景 1: 技术文档问答
**问题：** "How to check DT unready in ECS?"
**流程：**
1. 向量检索从知识库中找到相关的 DT unready 诊断文档片段
2. LLM 基于这些片段生成结构化答案（包含命令、步骤、注意事项）

### 场景 2: GC (Garbage Collection) 问题诊断
**问题：** "Why is GC not running on my cluster?"
**流程：**
1. 检索 GC 相关文档（配置、日志、常见问题）
2. 生成诊断步骤和可能的根因

### 场景 3: 新人 Onboarding
新加入团队的工程师可以通过 ChatGC 快速了解 ObjectScale 的架构、组件、常见问题，无需翻阅大量文档。

---

## 技术亮点

### 1. RAG 架构设计
- **检索增强：** 相比纯 LLM，RAG 通过检索真实文档片段，减少幻觉，提高答案准确性
- **知识库可更新：** 新增文档后重新摄取即可，无需重新训练模型

### 2. Prompt Engineering
- **限定上下文：** 强制 LLM 只能基于检索到的片段回答，避免编造信息
- **两阶段生成：** 先过滤相关片段，再生成答案，提高答案质量

### 3. 认证与安全
- **企业级 SSO 集成：** 支持 Dell SSO 登录，符合企业安全规范
- **Token 自动刷新：** 避免 token 过期导致请求失败
- **证书管理：** 自动安装 Dell PKI 证书，确保 HTTPS 通信安全

### 4. 可扩展性
- **向量数据库抽象：** 工厂模式支持未来切换到其他向量数据库
- **模型可配置：** Embedding 模型、LLM 模型可通过配置文件切换
- **前端可替换：** Streamlit 可替换为 Gradio、FastAPI + React 等

---

## 项目文件结构

```
OBS-vectorDB/
├── chromaDB_demo_v0.py          # 主程序 (Streamlit 应用)
├── vectorDBFactory.py           # 向量数据库工厂
├── auth_helper.py               # 认证辅助函数 (SSO token 缓存、证书管理)
├── authentication_provider.py   # 认证提供者 (SSO / Client Credentials)
├── requirements.txt             # Python 依赖
├── .env                         # 环境变量 (CLIENT_ID, CLIENT_SECRET, USE_SSO)
├── data/                        # 原始文档目录 (PDF, TXT)
├── chroma_db/                   # ChromaDB 持久化目录
├── history/                     # 聊天历史保存目录
├── ingested.txt                 # 已摄取文件记录
└── sso_cache                    # SSO token 缓存文件
```

---

## 运行方式

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量 (.env 文件)
CLIENT_ID=<your_client_id>
CLIENT_SECRET=<your_client_secret>
USE_SSO=true  # 或 false

# 3. 将文档放入 data/ 目录

# 4. 启动应用
python -m streamlit run chromaDB_demo_v0.py

# 5. 在 Web 界面点击 "Ingest documents now" 摄取文档

# 6. 开始提问
```

---

## 技术难点与解决方案

### 难点 1: Dell 企业网络证书问题
**问题：** 访问 Dell AIA Gateway 时 SSL 证书验证失败
**解决：** 自动下载 Dell PKI 证书并追加到 certifi bundle

### 难点 2: Token 过期导致请求失败
**问题：** JWT token 有效期 1 小时，过期后请求失败
**解决：** 实现 token 缓存 + 自动刷新机制（过期前 120 秒自动刷新）

### 难点 3: 大文档摄取内存溢出
**问题：** 一次性摄取大量文档导致内存不足
**解决：** 批量插入 (batch_size=30) + 逐文件处理

### 难点 4: LLM 幻觉问题
**问题：** LLM 可能编造不存在的信息
**解决：** Prompt 中强制限定 "只能基于检索到的片段回答"，并在检索不到时明确返回 "I don't know"

---

## 未来改进方向

1. **多向量数据库支持：** 扩展支持 Pinecone, Weaviate, Milvus
2. **混合检索：** 结合关键词检索 (BM25) 和向量检索，提高召回率
3. **Agent 架构：** 引入 LlamaIndex Agent，支持多步推理、工具调用
4. **评估体系：** 引入 RAGAS 等 RAG 评估框架，量化答案质量
5. **多模态支持：** 支持图片、表格的向量化和检索
6. **Fine-tuning：** 在 ObjectScale 领域数据上微调 Embedding 模型，提高检索准确率

---

## 总结

OBS-vectorDB 是一个完整的企业级 RAG 应用，展示了以下技术能力：
- **RAG 架构设计与实现**
- **向量数据库 (ChromaDB) 的使用**
- **LlamaIndex 框架的应用**
- **企业级认证系统集成 (Dell SSO)**
- **Prompt Engineering**
- **工厂模式等设计模式**
- **Streamlit Web 应用开发**

这个项目不仅解决了团队的实际问题（快速检索技术文档），也是学习和实践 RAG、向量数据库、LLM 应用开发的优秀案例。
