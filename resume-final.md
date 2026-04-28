# Professional Summary

## English Version

**INTRO:** Contribute to ECS/OBS (Object Storage System) as a QE (Quality Engineer), mainly focusing on feature validation, test automation, and continuous testing pipeline development for the Metadata Layer / DT (Directory Table) components.

**CONTRIBUTION:**

**Feature Validation:** Owned QE validation for multiple storage features including BFW, Topology (k8s), 12+4 EC scheme, Pravega drive removal, AFA regression, DT Health Check, and page table storage efficiency. For example, in **JA-5563 (Optimize DT Engine Thread Utilization)**, drove end-to-end validation including:
- **Comprehensive test coverage:** 40+ test cases across three page table states (UPGRADE_DONE, MAINTENANCE, UPGRADE) with single/multi-threaded dump and pagecopy scenarios
- **Performance benchmarking:** Compared pre/post-upgrade throughput with default vs. increased memory configurations, validated adaptive parameter effectiveness on both small-scale and large-scale clusters (HDD and AFA)
- **Functional validation:** Fiber dump/copy mechanisms, separate dump on AFA environments, SSDR integration, service restart resilience, DT ownership transfer (giveout), and B+tree/page table iteration verification
- **Automated monitoring:** Performance counter collection and automated Wiki upload integration for continuous performance tracking
- **Load injection framework:** Integrated mongoose/WET into Fortress for realistic workload simulation with configurable thread counts and object sizes
- **Adaptive parameter validation:** Verified dynamic parameter adjustment based on cluster scale (per-node DT count thresholds), ensuring correct activation/deactivation behavior and CMF history tracking

This validation ensured both functionality and performance met release criteria across different cluster configurations and upgrade scenarios.

**Test Automation & CI/CD:** Built and maintained Tier1/Tier2 continuous testing pipelines that significantly improved test coverage, execution reliability, and release quality, ensuring on-time TP/RC ZBB cycle completion; contributed to the Atlas test framework PoC for minimal regression and Atlas diagnostic tool API automation; served as Scrum Leader responsible for sprint ceremonies, cross-team communication, and pipeline stability monitoring.

**AI-Driven Quality Engineering:** Proactively explored AI agent-based workflows and contributed multiple production-ready AI skills and applications:

**RAG Application Development:**
- **OBS-vectorDB (ChatGC):** Designed and implemented an enterprise-grade RAG (Retrieval-Augmented Generation) knowledge base Q&A system for the ObjectScale storage team using ChromaDB vector database, LlamaIndex framework, and LLM (llama-3-3-70b-instruct). Key technical achievements include:
  - Implemented document ingestion pipeline with incremental processing (chunk_size=1024, batch insertion), supporting PDF/TXT formats
  - Designed two-stage retrieval-generation workflow: vector similarity search (Top-K=5) → context filtering → LLM answer generation with hallucination prevention via prompt engineering
  - Integrated Dell enterprise SSO authentication with JWT token caching and auto-refresh mechanism (120s TTL), including automated Dell PKI certificate installation
  - Applied factory pattern for vector database abstraction, enabling future extensibility to Pinecone/Weaviate/Milvus
  - Built Streamlit web interface with chat history persistence and Streamlit resource caching for performance optimization
  - Addressed technical challenges: SSL certificate validation, token expiration handling, memory-efficient batch processing, and LLM hallucination mitigation

**AI Skills Development:**
- **obs-dt-unready:** Developed a comprehensive DT unready diagnostic skill with staged workflow support (status collection → log analysis → automated root cause classification). Implemented automated log parsing for StopServing/InitFailed scenarios, exception pattern matching against knowledge base, and correlation analysis across multiple log sources. Supports both real-time diagnosis and historical time-window investigation with automatic DT priority selection.
- **obs-tier2-workflow-pr:** Built an end-to-end automation skill for Tier2 test job registration in the ECS/pipelines repository. Automatically generates correct Groovy entries for `tier_configs.groovy` and `workflows.groovy`, validates configuration, creates feature branches, and submits pull requests to GitHub Enterprise, reducing manual configuration errors and accelerating CI/CD pipeline onboarding.
- **obs-separate-vlan:** Created a network infrastructure automation skill for VLAN separation on rack switches (fox/hound), providing step-by-step checklist with safety guards, rollback procedures, and verification commands.

**AI Hackathon Project:**
- **AI ObjectScale Stability Insights:** Developed a full-stack intelligent DT (Directory Table) stability analysis system combining log visualization and RAG architecture. Key achievements include:
  - Built YAML-driven log parsing engine with dynamic regex pattern matching, supporting multiple DT types (OB, CT, SS) and service logs (blobsvc, cm, ssm)
  - Implemented event merging algorithm to simplify timeline visualization by consolidating hundreds of DT instances into aggregated views
  - Designed interactive DT initialization timeline using FastAPI + ECharts, enabling zoom, drag, and event filtering
  - Integrated RAG-based AI assistant using ChromaDB vector store and AIA Gateway LLMs (gpt-oss-120b, llama-3-3-70b-instruct) for intelligent troubleshooting
  - Applied Node-less frontend architecture (FastAPI-served HTML/JS + ECharts CDN) for zero-dependency deployment
  - Addressed technical challenges: multi-format log parsing (dateutil), batch processing with auto-degradation for payload limits, Dell AIA authentication integration
  - Achieved significant efficiency improvement: reduced DT init slowness diagnosis from hours (manual log analysis) to minutes (automated chart + AI Q&A)

**Additional Experience:**
- Gained hands-on experience with agent architecture, skill development (PEP 723 inline dependencies, SSH automation via Paramiko), and workflow-level AI integration to improve testing efficiency and defect discovery.

---

## 中文版本

**简介：** 作为 QE（质量工程师）参与 ECS/OBS（对象存储系统）项目，主要负责 Metadata Layer / DT（Directory Table）组件的功能验证、测试自动化和持续测试流水线开发。

**贡献：**

**功能测试：** 作为 QE 负责人主导了多个存储特性的验证工作，包括 BFW、Topology（k8s）、12+4 EC 方案、Pravega 磁盘移除、AFA 回归、DT 健康检查及页表存储效率测试。以 **JA-5563（优化 DT 引擎线程利用率）** 为例，端到端推动了以下验证工作：
- **全面的测试覆盖：** 40+ 个测试用例覆盖三种页表状态（UPGRADE_DONE、MAINTENANCE、UPGRADE），包含单线程/多线程 dump 和 pagecopy 场景
- **性能基准测试：** 对比升级前后在默认内存 vs. 增加内存配置下的吞吐量，验证自适应参数在小规模和大规模集群（HDD 和 AFA）上的有效性
- **功能验证：** Fiber dump/copy 机制、AFA 环境下的分离 dump、SSDR 集成、服务重启恢复能力、DT 所有权转移（giveout）以及 B+树/页表迭代验证
- **自动化监控：** 性能计数器收集和自动上传至 Wiki 的集成，实现持续性能跟踪
- **负载注入框架：** 将 mongoose/WET 集成到 Fortress，支持可配置线程数和对象大小的真实工作负载模拟
- **自适应参数验证：** 验证基于集群规模（每节点 DT 数量阈值）的动态参数调整，确保正确的激活/停用行为和 CMF 历史记录跟踪

此验证工作确保了功能和性能在不同集群配置和升级场景下均达到发布标准。

**测试自动化与 CI/CD：** 构建并维护 Tier1/Tier2 持续测试流水线，显著提升测试覆盖率、执行可靠性和发布质量，保障 TP/RC ZBB 周期按时完成；参与 Atlas 测试框架 PoC（最小回归验证）和 Atlas 诊断工具 API 自动化；担任 Scrum Leader，负责 Sprint 各项会议、跨团队沟通和流水线稳定性监控。

**AI 驱动的质量工程：** 主动探索基于 AI Agent 的工作流，并贡献了多个生产就绪的 AI 技能和应用：

**RAG 应用开发：**
- **OBS-vectorDB (ChatGC)：** 为 ObjectScale 存储团队设计并实现了企业级 RAG（检索增强生成）知识库问答系统，使用 ChromaDB 向量数据库、LlamaIndex 框架和 LLM（llama-3-3-70b-instruct）。主要技术成果包括：
  - 实现了支持增量处理的文档摄取流水线（chunk_size=1024，批量插入），支持 PDF/TXT 格式
  - 设计了两阶段检索-生成工作流：向量相似度检索（Top-K=5）→ 上下文过滤 → LLM 答案生成，通过 Prompt Engineering 防止幻觉
  - 集成了 Dell 企业 SSO 认证，实现 JWT token 缓存和自动刷新机制（120 秒 TTL），包括自动安装 Dell PKI 证书
  - 应用工厂模式实现向量数据库抽象，支持未来扩展到 Pinecone/Weaviate/Milvus
  - 构建了 Streamlit Web 界面，支持聊天历史持久化和 Streamlit 资源缓存以优化性能
  - 解决了技术难点：SSL 证书验证、token 过期处理、内存高效批处理、LLM 幻觉缓解

**AI 技能开发：**
- **obs-dt-unready：** 开发了全面的 DT unready 诊断技能，支持分阶段工作流（状态收集 → 日志分析 → 自动根因分类）。实现了 StopServing/InitFailed 场景的自动日志解析、基于知识库的异常模式匹配、以及跨多个日志源的关联分析。支持实时诊断和历史时间窗口调查，具备自动 DT 优先级选择功能。
- **obs-tier2-workflow-pr：** 构建了 Tier2 测试任务注册的端到端自动化技能。自动生成 `tier_configs.groovy` 和 `workflows.groovy` 的正确 Groovy 配置项、验证配置、创建功能分支并提交 Pull Request 到 GitHub Enterprise，减少手动配置错误并加速 CI/CD 流水线接入。
- **obs-separate-vlan：** 创建了机架交换机（fox/hound）VLAN 分离的网络基础设施自动化技能，提供分步检查清单、安全防护、回滚流程和验证命令。

**AI 黑客马拉松项目：**
- **AI ObjectScale Stability Insights：** 开发了结合日志可视化和 RAG 架构的全栈智能 DT（Directory Table）稳定性分析系统。主要成果包括：
  - 构建了 YAML 驱动的日志解析引擎，支持动态正则表达式模式匹配，覆盖多种 DT 类型（OB、CT、SS）和服务日志（blobsvc、cm、ssm）
  - 实现了事件合并算法，将数百个 DT 实例聚合为时间线视图，简化可视化展示
  - 设计了基于 FastAPI + ECharts 的交互式 DT 初始化时间线，支持缩放、拖拽和事件过滤
  - 集成了基于 RAG 的 AI 助手，使用 ChromaDB 向量存储和 AIA Gateway LLM（gpt-oss-120b、llama-3-3-70b-instruct）实现智能故障诊断
  - 应用了 Node-less 前端架构（FastAPI 提供 HTML/JS + ECharts CDN），实现零依赖部署
  - 解决了技术难点：多格式日志解析（dateutil）、批处理自动降级（payload 限制）、Dell AIA 认证集成
  - 显著提升诊断效率：将 DT 初始化慢诊断从数小时（人工日志分析）缩短至数分钟（自动图表 + AI 问答）

**其他经验：**
- 积累了 Agent 架构、Skill 开发（PEP 723 内联依赖、基于 Paramiko 的 SSH 自动化）和工作流级别 AI 集成的实践经验，提升测试效率和缺陷发现能力。
