# Continuous Testing 知识总结

本文档总结分布式对象存储项目的 Continuous Testing(持续测试)体系,内容来自内部 Wiki 的主页面及其子页面。

内容已脱敏:不包含任何真实内部系统地址、Jenkins/Grafana/Confluence 链接、真实集群名、人员姓名、Jira 编号、服务器 ID、包版本号或内部仓库地址。所有专有名词均以通用描述替代。

---

# 一、Continuous Testing 主页面

## 1. 背景 Context

组织正在向 IRC 发布模型(固定日期发布)转型。传统模型里,回归测试集中在发布周期后期,主要有几个测试迭代阶段:

- Feature Complete(主干分支)
- Test Iterations(主干分支)
- ZBB(发布分支)
- RC(发布分支)

这种“后期集中回归”的方式不适合固定日期发布,因此团队要转向 **Continuous Testing(持续测试)** 模型。

## 2. 持续测试 vs 传统测试

| 维度 | 持续测试(目标) | 传统测试(现状) |
|------|------------------|------------------|
| 时机与频率 | 持续、频繁、几乎一直在测 | 开发之后单独阶段 |
| 自动化 | 高度依赖自动化 | 有自动化但不普遍 |
| 反馈闭环 | 快速反馈给开发 | 反馈往往滞后 |
| 与 DevOps 集成 | 是 CI/CD 管线的一部分 | 与 DevOps 结合不好 |
| 速度与效率 | 为速度和效率设计 | 手工时耗时 |
| 风险控制 | 尽早发现和处理问题 | 问题可能到后期才暴露 |

## 3. 方法 Approach:分层测试 Tiered Testing

借鉴同公司另一存储产品的 Test Tiering 方法,并针对本产品做调整。

### Tier 定义

- **Tier 0 - Pre-build(构建前)**: 帮助团队随时安全合并代码,确保合并不破坏主干稳定性。
- **Tier 1 - Main Stability(主干稳定性)**: 主干稳定性验证。
- **Tier 2 - Continuous Regression(持续回归)**: 扩展功能与系统测试的持续回归。

### 与另一存储产品的 Tier 对比

| 另一产品 Tier | 本产品 Tier |
|---------------|-------------|
| Tier 0: 单元测试 | Tier 0: 构建前组件验证,始终作为组件构建一部分 |
| Tier 1: 非常基础的功能测试 | Tier 0: 构建后组件验证,作为 CI/acceptance 阶段 |
| Tier 2: 核心产品稳定性评估 | Tier 1: 构建验证,在物理集群安装产品包后执行 |
| Tier 3: 扩展特性测试 | Tier 2: 扩展构建验证,类似 Tier 1 执行 |

### Workflow 范围

Workflow 不仅用于发布测试,也用于主干测试,包括每日稳定性验证和特性级测试执行。

## 4. Tier 0 - Pre-build

- 组件级测试,集成在构建管线中(CI 和 acceptance 阶段)。
- 期望:所有团队组件都实现了全部测试阶段。
- Tier 0 是组件相关的,可以覆盖比另一产品 Tier 0/1 更广的范围。

## 5. Tier 1 - Main Stability

### 目的

对主干构建做稳定性验证,快速发现回归。

### 范围:测试用例选择标准

**应包含(DO include):**

- 验证特定特性、失败即视为 SEV-1/SEV-2 缺陷的用例(理想是 P0/P1)。
- 当前每日 workflow 中稳定运行的自动化用例。
- 验证特性广度的用例,包括依赖检查和与其他组件的 API/契约。
- happy path 和精选的关键失败/负向场景。
- 后续 Tier 中被识别为“功能逃逸”的用例(day-2 及以后过程)。

**不应包含(DONT include):**

- 破坏性用例(故障注入、混沌测试)。
- 非功能测试。
- 非确定性或模糊测试。
- 单元测试。
- 失败仅视为 SEV-3 的用例。

### 约束 Constraints

- 用例可并行或串行,但应支持与其他组件用例并行执行。
- 互斥场景(如升级与节点替换)需要防止并行冲突。
- 整体执行时间应有上限(文档中讨论从 8 小时收紧到更短,以便当天恢复)。
- 平台/部署模型特定的用例在其他平台应跳过而非失败。

### 管理与治理 Governance

- **System team**: 维护基础设施,确保集群健康、运行最新构建(平台、OS、产品),保障管线运行,做框架级维护。
- **Main caretaker**: 来自功能团队(角色每 6 个月轮换),定期监控运行;运行完成后通知特性负责人并催促分析。
- **UoM(Unit of Maintenance,维护单元)**: 修复下游 job 失败,定期监控分析通道,为失败用例创建 Product/Test script 问题,按标准增删用例/Job。

### 测试管理

- **零噪音**: 所有测试不应有波动或间歇性失败。
- **加入测试**: 新特性测试规划时识别并在合并前认证进入 Main Stability;测试需在类似环境连续通过至少 10 次(无代码改动)。
- **移除测试**: 引起级联失败、被基础设施破坏且 24 小时 SLA 内无法修复、或在最新版本已废弃的测试应移除。
- **处理失败**: 测试脚本问题 24 小时 SLA 修复;产品问题跟踪到缺陷关闭。

## 6. Tier 2 - Continuous Regression

### 目的

Tier 2 在“已验证稳定(Verified Stable)”的构建上迭代执行,覆盖所有不够关键或过于昂贵不适合在早期 Tier 反复执行的扩展功能(如 longevity 长稳)。

### 范围

- 不太关键的功能区域。
- 组合与非确定性测试。
- 平台和配置变体。
- 完整负向测试、分支测试、边角场景。
- 资源/耗时太贵不适合早期 Tier 的测试。
- 复杂度高、依赖多的测试。

### 约束

- 与前面 Tier 一样,Tier 2 必须完全自动化(含 setup)。
- 可依赖外部服务/依赖,但要保持很高一致性。
- 若 Tier 2 发现 Sev 1/Sev 2 功能回归,应做 RCA-CA,分析为什么没有更早发现并制定改进计划。

### 治理

- System Team 与其他 UoM 负责:测试自动化与维护、硬件管理(识别/维护/管理)、测试执行(调度/执行/分析/多配置覆盖)、结果报告。

## 7. 运营化 Operationalization

- 借助 Scrum@Scale 模型和 Goal Zero 落地。
- 在一个总 Initiative 下,为每个 Tier 建 Feature,再拆成多个 Epic 分配到不同季度。

## 8. Combined 持续测试方案

平衡两个存储产品的持续测试方法,考虑本产品的现实:

- 组件化产品,多仓库、多团队负责。
- 当前发布 PR 合入主干,组件二进制从主干构建。
- UT 和额外构建期测试集成在构建管线。
- 打包仓库提交前有 CI 和 acceptance 阶段,阻止回归进入主包。
- 部分组件可在 VM 测,部分需要完整包安装(如监控和 Fabric)。

方案要点:

- 允许组件从主干构建、PR 合入主干。
- 增强 Tier 0 组件级测试(CI 和 acceptance)阻止回归进主包。
- 启用 Tier 1、Tier 2 构建验证和扩展构建验证。
- 团队可灵活决定测试放在管线哪个阶段。

## 9. 术语 Terminology

- **Test cycle(测试周期)**: 针对某个产品版本的一次完整测试;在不同集群上并行或互斥地运行多个 test job。输入是产品包目录,输出是通过/失败决定、结果登记、失败工单创建。
- **Test run(测试运行)**: 在单个集群上执行一个或一组 test job。输入是包 URL、集群名、测试列表;输出是把结果导出到调度器。
- **Test job(测试作业)**: 测试执行中的最小管理单元,产生结果(通过数/总数)。输入是集群名和参数,输出是执行结果文件。

## 10. Test Job / Executor 要求

### 对 test job 的要求

- 能被正确调度、正确报告(执行 vs 期望 vs 通过)。
- 可配置在开发或 QE 的 CI 实例。
- 以“字典列表”结构定义 job,每个 job 是一个元素,Tier 1/Tier 2 各有独立列表。
- job 属性建议包含:所有者/团队、执行模型(并行/串行/互斥)、稳定性状态(stable/unstable)等。

### 对 executor 的要求

- executor 读取某 tier 的 job 定义结构并执行。
- 支持稳定与不稳定两条执行流。
- 收集执行结果。
- 在结果/错误时发 Slack 通知并 @ 负责人。

### 执行结果文件

- 所有 test job 生成统一的执行结果文件工件,供调度器汇总、报告和上传测试管理系统。

### Cluster pools(集群池)

- 通过集群池管理硬件资源,支持调度和锁定。

---

# 二、子页面总结

## 子页面 1:Advanced Development(高级开发)

描述持续测试的高级开发方向(部分为 WIP/草稿)。

### 执行队列 Queue of Execution

当前执行模型基于每日调度,问题:

- 按天调度,不保证一定执行(资源不足可能排不上)。
- 基础设施失败(OS、产品部署、CI、其他服务)导致非测试失败,且无重试,不保证执行。

引入执行队列后:

- test run 放入队列,只有完整执行或满足保留标准(类似 TTL 重试)后才移出。
- 队列持久化在独立于 CI 的存储中。
- 调度、队列处理、集群资源分配、执行是分离的独立过程。
- 通过消除固定时间调度的空隙,最大化资源利用。

### 动态硬件配置 Dynamic Hardware Configurations

因资源短缺和不同环境需求,希望同一集群能以不同配置复用:

- 一个集群既可作 8 节点,也可作 2×4 节点多 VDC 集群。
- 一个集群既可作 8 节点,也可作 2 个独立 4 节点单 VDC 集群。
- 以上组合,以及把大集群不同部分组合成独立集群(Intermix 配置)。

相关基础设施:存储/维护集群配置(inventory 仓库、Service console 的 CMS 库、脚本和管线)、查找可用资源并锁定/解锁独占使用。

需研究的问题:如何指定集群和配置(不同名字 vs 同名不同 profile)、如何与现有管线和 Service 过程代码兼容、如何挂接集群池、如何处理依赖名字的锁定。

## 子页面 2:失败时自动生成 STL/SRM Jira 工单

### 处理考量

- 每个 job 有 owner(邮箱)和 owner_team(受控字符串常量),用于确定目标团队和分派工程师。
- 后续可分析失败 job 的 console log,判断是否应分派给其他团队(如 devops)而非 owner_team。

### 流程

1. 调度器(scheduler)job 用 runner job 执行测试。
2. runner job 把执行结果回报给 scheduler。
3. scheduler 根据 job 状态等做测试结果决定。
4. scheduler 收集数据为 JSON(含待创建工单列表)。
5. 若列表非空,调用下游“Jira 工单创建 job”。
6. 创建 job 分析该问题是否已建过工单,需要时才新建。

### 判断工单是否已存在

1. 获取带特定标签(如 autogenerated)的所有未关闭工单。
2. 检查给定属性(失败 job、标签)是否已有打开的工单。
3. 已存在则不重复创建。

### 职责

- **Scheduler job**: 从下游收集失败详情;创建“failure records”结构;用该结构运行 Jira 创建下游。
- **Jira 创建 job**: 读取 failure records(JSON,作为多行字符串参数传入);读取已有工单避免重复;创建真正新的工单;把创建报告(工单列表 + 链接,HTML)存为工件。

### 测试场景

- 用相同 failure records 运行两次,第二次不应新建工单。
- 修改一个元素使其唯一后重跑,只应创建那一个工单。

### Failure records 结构

- **Header 部分**: 产品版本、包 URL、调度器构建链接、失败列表等。
- **failures 列表元素**: type(job=测试 job 失败 / run=测试运行失败,如产品部署失败)等;部分字段对 run 类型不适用。

## 子页面 3:持续测试的 CICD 过程与基础设施问题跟踪

### 已知问题(硬件相关)

- 记录了如 BIOS POST 循环等硬件已知问题及处置。

### CICD 过程

- **维护 Main stability 的集群池**: 通过监控面板确认集群“最近更新时间”在合理范围(如 <15 分钟)。
- **集群池含义**: 需同时设置 possible_purposes 和 purpose 为相同值。
- **不同集群池含义**: pillar 池用于实际测试;reserved 池是备用/待命,pillar 池集群损坏时可重新分配。
- **pillar 池集群损坏时的操作**: 有明确处置流程(替换、记录基础设施问题)。
- **如何创建测试池并分配 job**。
- **配置时间窗口以防止创建 SRM 工单**。

### 硬件过程

- 硬件相关处置。
- **集群客户端安装**: 通过带外管理经 SSH 安装客户端、客户端主机配置、客户端错误处理、其他 OS 安装 Wiki。
- **错误与修复**。

## 子页面 4:持续回归运行时长(Continuous Regression Run Timings)

- 记录各 Tier 2 job 的运行时长、稳定性状态(stable/unstable)、是否可并行、负责领域。
- 涵盖领域示例:管理界面 GUI、supportability、监控 UI、IAM(单区多账户)、安全(DARE、FSA、IAM)、HDFS/S3A、S3 API(bucket、object、s3select、secretkey、smtp)、Atmos(FSA、geo)、AWS SDK(IAM / 非 IAM)等。
- 页面结构按控制路径、安全、对象、存储、基础设施等分区展示。
- 说明如何为 job 添加 badge/icon(复制 job 链接、插入网页图片、预览、插入)。
- 手工测试用例链接到测试管理系统(需将手工用例分离)。

## 子页面 5:如何搭建多 VDC 集群

多 VDC 集群由至少两个 VDC 集群组成。步骤:

1. **添加到 inventory 仓库**: 基于已有集群样例建 inventory 文件,合并到仓库。
2. **添加集群文件到 lab-tools 仓库**: 添加 ansible hosts 配置。
3. **更新并运行部署 Jenkins job**。
4. **测试过程**:
   - Full setup test:选择所有 VDC,取消勾选 DRYRUN 运行。
   - Single cluster test:单集群验证。

## 子页面 6:如何用虚拟集群做主干稳定性

### 概要

Tier(主干稳定性)job 可运行在虚拟集群上。

### 说明

- 通过 2 个参数控制;设置 virtual=true 会触发虚拟专用子 job(OS 与产品部署)。

### 部署细节

- 部署主要包含 OS 与产品两部分。

### 集群详情

- **可用集群**: 有若干可用虚拟集群;根据配置文件里设置的池选择集群。
- **如何创建更多集群**: 通过部署 Jenkins job。
- **如何搭建硬件集群**。
- **预留/释放集群**: 用预留 job 获取/释放。
- **加入/移出池**: 用专门 job,无需提 PR 改 purpose 注释。

## 子页面 7:OBS-Main Build Stability Process

(注:该页大部分内容已合并到主页面)

- **目标**: 大部分测试尽早执行,朝“稳定主干构建”推进。
- **目的**: 形成朝主干稳定性的分层测试方法。
- **三个 Tier**: Tier 0 构建前管线、Tier 1 主干稳定性、Tier 2 持续回归(功能 + 系统测试)。
- **过程范围**: 识别现有用例/套件与分层测试对齐的差距;定义 Tier 1 用例识别标准。
- **Tier 1 用例标准**: 从每日 workflow 识别;P0 & P1;当前每日 workflow 稳定;非破坏性;可与其他测试并行;由 UoM 提供包含这些用例的 Jenkins job。
- **约束**: 不含部署时应少于 8 小时执行完。
- **Tier 2**: 由 UoM 识别回归套件用例(功能 & 系统测试)。

## 子页面 8:Supporting Workflows in Continuous Testing(支持 Workflow)

### 什么是 Workflow

- Workflow 在已有 Test job 概念(定义 Jenkins job 及基础配置、所有权)之上组织测试。

### 要求

- job 若被 workflow 选中的 test run 使用,应从旧 test job 列表的调度中排除。

### Tier 2 test run 定义的创建

- 当前方式:为计划的 test run 维护列表;共享执行模式(sequential/parallel)下多个 test job 放进一个 test run;test run 由“集群池”和“Batch name”标识(exclusive 模式不用 batch name)。
- Workflow 支持的改动:可用单独的 job 表用于 workflow,逐步迁移。

### 格式与处理

- 用 groovy 定义;默认值定义在配置里的 TIER2_TEST_RUN_DEFAULTS。
- workflow 的元数据(如 name)应包含在 test run 的 META_DATA 参数中,用于构建报告和上传测试管理系统的工件。
- workflow 与 test run 的关系:test job 名字在 test run 内保持唯一。

### 用户指南

- **workflow test jobs 定义**: 每个 test job 的参数应在唯一一个列表中定义(单一来源),由配置校验 job 验证。
- **从 Tier 2 列表迁移 job 到 workflow 列表**。
- **workflow test runs 定义**: 支持参数、no-dare 模式、provision 设置(可为同集群定义不同配置并用 config 选项选择)、feature flag 设置、为串行执行定义多个 test job 或 batch(整批可标记 unstable)。
- 正确性在管线仓库 PR 验证时自动校验。

### 受影响区域与增强

- 影响原持续测试设计中的初始 OS/产品版本(用于升级)等区域。
- 可能增强:workflow 级别的定义等。

## 子页面 9:Tier 1 Clusters

- 记录 Tier 1 集群到池的初始映射(会随实际测试需求变化)。
- 分区:使用中的集群(Clusters in use)、预留的集群(Clusters reserved)。

## 子页面 10:Tier 2 Shared Clusters

- **Tier2 共享集群状态表**: 各集群健康和使用状态。
- **移交给其他团队的集群**。
- **备注**:
  - **集群健康状态**: 含 excluded(不在池中)等。
  - **集群使用状态**: 含一致性失败(完全不工作、部署或服务过程持续失败)等。
  - **池容量状态**: 含 ALERT(即使允许 unstable 集群仍因等待集群超时而 job 失败)等。
  - **共享池目的**: 更有效利用资源,尤其对多 VDC 等大配置。
  - **可调度内容**: 按最小需求调度(如只需常规 4 节点的测试就调度到 4 节点常规池)。
  - **有用信息**: 多 VDC 搭建指引、共享池资源利用监控、集群监控。

## 子页面 11:OBS 持续测试(Tier2)与回归周期的统一报告

### 报告结构与命名约定

- 面向 Continuous Tier2 与 Regression Cycles 的统一报告。
- **Test Design Baseline(测试设计基线)**。
- **报告工具与自动化进度**: 提供测试管理系统上传器(可从制品库或 Docker 容器获取)。
  - Docker 容器快速上手。
  - 更新发布周期基线:各 pillar 上传各自的 Non_Tier2/Manual 设计基线到不同回归周期(passes、ZBB、RC)。
  - 把 Tier2 结果复制/移动到回归周期。

### 概览

- **术语**、**动机与目标**: OBS Continuous Tier2 应能在发布分支创建后同时针对主干和某个大版本并发运行。

### Continuous Tier2 报告 / 回归周期

- **回归周期对比与主要差异**。
- **从 Tier2 填充发布回归周期**: 可折叠多个 RC 构建为单个 RC 周期(属实现决策,不改变报告组织方式)。

### 回归基线与计划

- **回归基线**。
- **计划与 JIRA**。

---

# 三、核心要点速记

## 1. 一句话概括

```text
Continuous Testing 是为适配固定日期(IRC)发布而采用的分层持续测试模型:Tier 0 在组件构建阶段做构建前/后验证阻止回归;Tier 1 在物理集群上对主干构建做稳定性验证,只收高优先级、稳定、非破坏、可并行的用例,零噪音、24 小时 SLA;Tier 2 在已验证稳定的构建上迭代跑扩展功能、组合、平台变体和长稳等回归。整套体系由 System Team、Main caretaker 和各 UoM 治理,用 scheduler/runner job、集群池、执行队列、统一报告和失败自动建单支撑。
```

## 2. 三个 Tier 记忆

```text
Tier 0 = 构建阶段组件验证(CI/acceptance),阻止回归进主包。
Tier 1 = 主干稳定性,物理集群安装后跑 P0/P1 稳定非破坏用例,快速反馈。
Tier 2 = 持续回归,已验证稳定构建上跑扩展/组合/平台变体/长稳测试。
```

## 3. 关键概念

```text
Test cycle > Test run > Test job 三级粒度;scheduler job 调度并汇总,runner job 执行并回报;集群池 + 执行队列管理硬件资源和执行保证;失败自动生成 STL/SRM 工单并去重;虚拟集群和多 VDC 集群扩展资源;统一报告对接测试管理系统和回归周期。
```

## 4. 治理角色

```text
System Team 管基础设施和管线;Main caretaker(功能团队轮换)监控运行并催促分析;UoM 负责各自 job 的失败修复、用例增删和分析,测试脚本问题 24 小时 SLA 修复。
```
