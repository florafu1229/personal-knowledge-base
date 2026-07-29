# CI/CD Pipelines 仓库知识总结（pipeline_testing）

这份文档总结一个面向**分布式对象存储产品**的 **Jenkins Pipelines 自动化仓库**的设计与实践:它承载整个产品的自动化构建、打包、部署、升级和分层测试流程。

内容已脱敏:不含真实公司/产品名、Jenkins/Wiki/Artifactory/Git 地址、人员姓名邮箱、Slack 频道、集群 IP、包版本号。所有专有名词以通用描述替代。文末附一个可复用的 **prompt**,用于让 AI agent 帮你从零搭建/维护类似的 Pipelines 仓库。

---

# 1. 这是什么

- 一个集中存放**所有 Jenkins Pipeline 脚本和共享库**的仓库,用 **Groovy** 编写。
- 既有**可复用的库**(给开发者写新流水线用),也有**成品自动化脚本**(直接跑构建/测试/部署)。
- 覆盖产品全生命周期:PR 校验 → 组件构建 → 打包 → 部署 → 升级 → 分层测试 → 结果报告 → 失败三查 → 覆盖率统计。
- 规模量级:数百个 `.groovy` 文件,跨 40+ 目录。

**一句话定位**:整个产品 CI/CD 与持续测试的"编排中枢",把 Jenkins 当执行引擎,用 Groovy 库把构建/测试/部署的多阶段黏合起来。

---

# 2. 技术栈

| 项 | 内容 |
|---|---|
| 语言 | Groovy(Jenkins Pipeline / Shared Library) |
| 执行引擎 | Jenkins(多 agent,按 label 调度) |
| 构建 | Gradle |
| 静态检查 | CodeNarc(Groovy lint)、ShellCheck(shell 脚本) |
| 开发环境 | DevContainer(Java 21 + Groovy + Gradle + CodeNarc + ShellCheck) |
| 制品管理 | Artifactory + NFS 制品服务器 |
| 通知 | Slack / 邮件 |
| 源码托管 | 内部 Git(企业版) |

---

# 3. 目录结构(骨架)

```text
pipelines/
├── common.groovy          # 核心工具库(最大):制品配置、发布、label、git 等公共方法
├── cms.groovy             # CMS 封装:从 inventory 读集群拓扑
├── locks.groovy           # 集群加锁/预留(同步机制)
├── github.groovy          # Git API:PR 状态、提交、仓库操作
├── drpcheckers.groovy     # 恶意软件/合规扫描、制品校验
├── vars/                  # Jenkins Shared Library(loader.groovy 等)
├── src/                   # Pipeline 的 Groovy 类
├── acceptance/            # 验收/测试执行框架(含分层测试 test_tiers、三查 triage)
├── packaging/             # 制品打包流水线
├── flex/                  # 持续交付:部署/升级工作流
├── infra/                 # 基础设施与 DevOps:job 生成器、集群预留、PR 校验库
├── jobs/templates/        # Jenkins Job DSL 模板
├── service-console/       # 某控制台组件的构建/校验
├── fabric/ object/ os/ monitoring/ ...  # 各组件的构建/CI/验收脚本
├── tools/                 # CodeNarc、Artifactory 工具等
├── resources/             # 非 groovy 的文件和脚本
├── Makefile               # 本地校验入口(make check 等)
└── pipelines_pr_validation.Jenkinsfile  # 仓库自身的 PR 校验流水线
```

分层要点:
- **根目录的几个大库**(`common`/`cms`/`locks`/`github`/`drpcheckers`)是所有流水线的地基。
- **按组件/职能分目录**:每个组件有自己的 build/ci/acceptance 脚本。
- **`vars/` 是 Jenkins Shared Library 约定目录**,`src/` 放可复用的类。

---

# 4. 核心共享库

| 库 | 职责 |
|---|---|
| `common.groovy` | 最核心最大的库:Artifactory/制品地址配置、发布逻辑、Jenkins agent label 常量、git 相关方法(如 checkout、按路径变更轮询)、Slack 通知、失败步骤日志打印等 |
| `cms.groovy` | CMS(集群管理)封装,从 inventory 仓库读取集群拓扑(节点、网络等) |
| `locks.groovy` | 集群资源的加锁/预留/释放,保证多任务不抢占同一集群 |
| `github.groovy` | 与 Git 平台交互:PR 状态回帖、提交查询、仓库操作 |
| `drpcheckers.groovy` | 制品的安全/恶意软件扫描与校验 |

> 找东西的经验:制品 URL/仓库地址在 `common.groovy` 搜;集群加锁在 `locks.groovy`;job 在哪定义看 `infra/` 的 job 生成器或 `jobs/templates/`。

---

# 5. Loader 机制(流水线怎么加载库)

流水线不用传统 import,而是用一个 `loader` 从本仓库按分支拉取所需库并起别名:

```groovy
// 从 pipelines 仓库的某分支加载 common 库,起别名 common
loader.loadFrom('pipelines': [common: 'common'], branch: 'master')
common.slackSend(message: 'Hello World!')
```

- `loadFrom` 指定"仓库 → { 别名: 相对路径 }"和分支。
- 好处:流水线只声明依赖哪些库,版本随分支走,便于灰度和回滚。
- PR 校验时也会 loadFrom 一堆库,**仅为检查它们的语法能否编译通过**。

---

# 6. Job 命名约定

统一命名提升可读性和可搜索性:

```text
<component>-<branch>-<stage>[-<specific-name>]
```

- `<component>`:组件名(如 fabric、控制台、os、monitoring)。
- `<branch>`:组件 git 分支(master、release-x.y、custom)。
- `<stage>`:流水线阶段(pr-validation、build、ci、acceptance ...)。
- `<specific-name>`:可选,进一步区分功能。

示例:`fabric-release-x.y-build`、`<console>-custom-build-ci`、`<component>-pr-validation`。

---

# 7. Job 生成器(Job DSL)

Job 不是手工在 Jenkins 上建,而是**代码生成**:

- `infra/ecs_job_generator.groovy`、`infra/job_generator.groovy`:批量生成 job 定义。
- `flex/generator/`、`os/os_job_generator.groovy`、各组件的 `*_job_generator.groovy`:各域的 job 生成。
- `jobs/templates/`:30+ Job DSL 模板。

好处:job 配置纳入版本管理、可评审、可复现,避免"Jenkins 上手改导致漂移"。

---

# 8. 打包流程(packaging/)

把各组件二进制打成产品安装包:

| 脚本 | 用途 |
|---|---|
| `VI-packaging.groovy` | 主打包流水线,产出主安装包 |
| `custom_packaging.groovy` | 自定义分支打包(含 fingerprint 等通用方法) |
| `packaging_feature_branch.groovy` | 特性分支打包 |
| `packaging_with_upgrade.groovy` | 打包并带上 OS + 编排器升级包 |
| `publish_ecs_artifacts.groovy` | 制品发布 |
| `GA-release-tagger.groovy` | GA 发布打 tag |

**Fingerprint(指纹)**:用制品指纹做可追溯性(哪个 job 产出哪个制品、组件版本溯源)。

---

# 9. 分层测试框架(acceptance/test_tiers/)—— 重点

这是"持续测试"落地的核心引擎,和 Tier0/Tier1/Tier2 分层测试理念对应(见 `continuous_testing`)。

## 9.1 关键组件

| 文件 | 职责 |
|---|---|
| `tier_configs.groovy` | **测试分层配置**(极大文件):定义各 tier 的 test job、集群池、执行模式等 |
| `scheduler.groovy` | **调度器**:决定什么在什么集群上跑,汇总结果 |
| `runner.groovy` | **执行器**:在单集群上执行一个/一组 test job |
| `workflows.groovy` | **workflow 定义**:在 test job 之上组织成端到端测试流 |
| `validator.groovy` | 校验 job/workflow 配置合法性 |
| `lib_results.groovy` | 结果结构与汇总 |
| `shared_vars.groovy` | 共享变量/默认值 |
| `report_uploader.groovy` / `report_folders.groovy` / `gen_report_tier2.groovy` | 报告生成与上传 |

## 9.2 三级粒度(概念)

```text
Test cycle(一次完整测试周期,针对某产品版本)
  └── Test run(在单个集群上跑一组 test job)
        └── Test job(最小执行单元,产生 通过数/总数 结果)
```

## 9.3 覆盖率统计

- `collect_coverage.groovy` / `collect_coverage_tier0.groovy`:采集各 tier 覆盖率。
- `ecs_code_coverage_aggregator.groovy` / `*dashboard_uploader.groovy` / `*reporter.groovy`:聚合、上传看板、生成报告。
- 支持定期覆盖率任务(`init_periodical_coverage.groovy`)。

---

# 10. 失败三查(acceptance/triage/)

测试失败后自动分诊、归类、建单:

| 文件 | 职责 |
|---|---|
| `picker.groovy` | 挑出需要三查的失败 |
| `table_rules.groovy` / `code_rules.groovy` | 规则匹配(按已知模式归类失败) |
| `ai_triage/engine.groovy` | **AI 辅助三查引擎**:用规则+智能分析判断失败归属团队/类型 |
| `teams.groovy` | 团队映射(把失败分派到对应团队) |
| `result_beacon.groovy` | 结果信标/上报 |
| `defect_creation_maintenance/` + `jira_creator.groovy` | **自动建缺陷单**并去重维护 |
| `stl_notifications.groovy` | 失败通知(Slack/邮件,@负责人) |

> 亮点:把"失败 → 判类型 → 是否已建单 → 建单/通知"做成自动化流水线,减少人工分诊,和 `continuous_testing` 里"失败自动建单"一节对应。

---

# 11. 升级与部署工作流(flex/)

产品持续交付的核心(70+ 文件):

- `ecs-upgrade-workflow.groovy`:主升级工作流(部署 → 升级 → 验证)。
- `ecs_deployment_workflow.groovy`:部署工作流。
- `ecs_geo_upgrade_workflow.groovy`:多站点(geo)升级。
- `ecs-sc-procedures-upgrade-workflow.groovy`:升级中执行服务过程(如节点扩展/替换)。
- 子目录:`object/`(对象服务)、`kubernetes/`(K8s 平台)、`platform/`、`obs_system_test/`(系统测试)。

---

# 12. 仓库自身的质量保障(元测试)

这个仓库自己也有一套"测试流水线的测试",很值得学:

## 12.1 PR 校验流水线(`pipelines_pr_validation.Jenkinsfile`)

- 把每类校验封装成一个 **closure**,逐个作为一个 stage 执行,任一抛异常即该项失败。
- 校验项包括:**Job Configs**(必须先跑,因为会改后续 test run/job 定义)、**Workflow Code**、**Validator Code**、**Runner Code**、**Scheduler Code**。
- 全部通过才算 PR 校验成功;失败信息回写到 build description / PR。
- 还支持"只校验分支"(validateOnly)模式。

设计模式:**校验项 = 一组 closure**,`validationResults.every { it }` 判断是否全过——干净、可扩展(加一项只需往列表加一个 closure)。

## 12.2 本地/CI 静态检查

- **CodeNarc**:Groovy 静态分析(`tools/` 有规则,Gradle 任务 `codenarcPipelines`)。
- **ShellCheck**:shell 脚本检查。
- **语法检查脚本**:`pipeline_syntax_check.sh` / `.bat` 在 Jenkins host 上校验脚本语法。
- **DevContainer + Makefile**:统一环境本地校验。

```bash
make check           # 校验改动过的 Groovy 文件(容器里跑)
make check-changed   # 只校验已 staged 的文件
make check-repo      # 校验全仓库
make install-hook    # 装 git pre-commit hook,提交时自动校验
make build-container # 构建 devcontainer 镜像
```

DevContainer 内含:Java 21、Groovy 4.x、Gradle 8.x、CodeNarc、ShellCheck。

---

# 13. 代码规范(Groovy 最佳实践)

从贡献指南提炼的关键约定:

- **文件命名**:只用拉丁字母 + 下划线分词(`custom_packaging`,不要连字符),便于 Groovy 原生引用免加引号。
- **用真实类型,不要用 `def`,更不要省略类型**:
  ```groovy
  int a = 3          // ✔ 局部变量,类型明确
  a = 2              // ❌ 变成全局变量
  def a = 2          // ❌ 目的不清、可读性差
  collectionOfStrings.each { String it -> ... }   // ✔ 闭包也写类型
  ```
- **用 `params` map 取 job 参数**:`params.SOME_PARAM`(不存在返回 null,直接引用未定义变量会抛 `MissingPropertyException`)。
- **库代码里禁止用 `stages`**(`stages` 属于 Jenkinsfile 层,不是可复用库该有的)。
- **用 fingerprint** 做制品可追溯。
- **用最合适的 git 方法**(仓库封装了 checkout、按路径变更轮询等,不要乱用原生 `git()`)。
- **用 `common.printFailedStepsLogsToBuildDescription()`** 把失败步骤日志打到 build description,便于定位。

---

# 14. 术语速查

| 术语 | 含义 |
|---|---|
| Loader / loadFrom | 按分支从本仓库加载 Groovy 库并起别名 |
| Shared Library(vars/) | Jenkins 共享库约定目录 |
| Job DSL / Job Generator | 用代码生成 Jenkins job 配置 |
| Stage | 流水线阶段 |
| Tier0/1/2 | 分层测试:构建阶段/主干稳定/持续回归 |
| Test cycle/run/job | 测试三级粒度 |
| Fingerprint | 制品指纹,做版本溯源 |
| CMS | 集群管理,读 inventory 拓扑 |
| Lock/Reservation | 集群加锁与预留 |
| Triage | 失败分诊归类 |
| CodeNarc | Groovy 静态检查 |

---

# 15. 可复用的设计亮点(面试/迁移用)

- **编排中枢**:一个仓库统管全产品 CI/CD + 持续测试,Jenkins 只当执行引擎。
- **库 + 成品分离**:底层大库(common/cms/locks)+ 上层成品流水线,复用性强。
- **Loader 分支化依赖**:流水线依赖随分支走,易灰度回滚。
- **Job 即代码**:Job DSL 生成,纳入版本管理,杜绝手工漂移。
- **分层测试引擎**:scheduler/runner/workflows/tier_configs 解耦,调度与执行分离。
- **失败自动三查 + 自动建单**:规则 + AI 引擎归类,自动分派团队、去重建单。
- **仓库自测**:PR 校验流水线用"closure 列表 + every"模式测自己的库,配 CodeNarc/ShellCheck/DevContainer/pre-commit 多道闸门。

---

# 附录:Prompt —— 用 Vibe Coding 搭/维护一个 Jenkins Pipelines 测试自动化仓库

下面是可直接复制给 AI coding agent 的 prompt,用于从零搭建或维护一个类似的 CI/CD + 持续测试编排仓库(已脱敏、通用化)。

## A. 总纲 Prompt

> 你是一名资深 CI/CD 与测试基础设施工程师。我要搭建一个用 **Groovy** 编写的 **Jenkins Pipelines 编排仓库**,统管一个分布式产品的自动化构建、打包、部署、升级和分层测试。请按我的设计哲学分阶段实现,现在先搭骨架并确认理解。
>
> **设计哲学(必须遵守)**:
> 1. **库与成品分离**:底层可复用大库(`common`/`cms`/`locks`/`github`)+ 上层成品流水线;库代码里**禁止用 `stages`**。
> 2. **Job 即代码**:所有 Jenkins job 用 Job DSL / 生成器生成,纳入版本管理,不手工在 UI 改。
> 3. **依赖分支化**:流水线用一个 `loader.loadFrom(repo, {别名:路径}, branch)` 按分支加载库。
> 4. **命名约定**:job 名 `<component>-<branch>-<stage>[-<specific>]`;文件名只用字母+下划线。
> 5. **代码规范**:用真实类型不用 `def`;用 `params.X` 取参数;能静态检查的都要过 CodeNarc + ShellCheck。
> 6. **仓库自测**:仓库自身要有 PR 校验流水线,校验项以 closure 列表组织,全部通过才算过。
>
> **目录结构**:
> ```text
> pipelines/
> ├── common.groovy / cms.groovy / locks.groovy / github.groovy   # 核心库
> ├── vars/                    # Jenkins Shared Library(loader 等)
> ├── src/                     # 可复用 Groovy 类
> ├── acceptance/test_tiers/   # 分层测试引擎(scheduler/runner/workflows/tier_configs/validator/results)
> ├── acceptance/triage/       # 失败分诊 + 自动建单
> ├── packaging/               # 制品打包
> ├── flex/                    # 部署/升级工作流
> ├── infra/                   # job 生成器、集群预留、PR 校验库
> ├── jobs/templates/          # Job DSL 模板
> ├── tools/                   # CodeNarc 规则等
> ├── Makefile                 # 本地校验入口
> └── pipelines_pr_validation.Jenkinsfile
> ```
>
> **路线图**(后面逐阶段做,现在别提前写):Phase 0 脚手架 + DevContainer + Makefile(check/check-repo)+ CodeNarc/ShellCheck → 1 loader + common 库 → 2 集群管理 cms + 加锁 locks → 3 Job 生成器 + 命名约定 → 4 打包流水线 → 5 部署/升级工作流 → 6 分层测试引擎(scheduler/runner/workflows/tier_configs)→ 7 失败三查 + 自动建单 → 8 覆盖率统计 → 9 仓库自身 PR 校验流水线。
>
> **现在只做 Phase 0**:建目录、`Makefile`(`check`/`check-changed`/`check-repo`/`install-hook`/`build-container`)、`.devcontainer`(Java+Groovy+Gradle+CodeNarc+ShellCheck)、CodeNarc 规则占位、一个 pre-commit hook 脚本。做完贴目录树和 Makefile,并复述设计哲学。**先不要实现任何流水线逻辑。**

## B. 分阶段 Prompt 模板(每阶段:目标 → 接口 → 约束 → 验收)

### 分层测试引擎(最核心阶段)

> 实现 `acceptance/test_tiers/` 下的分层测试引擎:
> - `tier_configs.groovy`:声明式定义各 tier 的 test job 列表,每个 job 含 owner/team、执行模式(parallel/sequential/exclusive)、集群池、stable/unstable 状态。
> - `scheduler.groovy`:读取 tier 配置 → 分配集群 → 触发 runner → 汇总结果。
> - `runner.groovy`:在单集群执行一组 test job,产出统一结果结构。
> - `workflows.groovy`:在 test job 之上组织端到端测试流(共享集群/批次)。
> - `validator.groovy`:校验 job/workflow 配置合法性(如 job 名全局唯一、必填字段)。
> - `lib_results.groovy`:结果结构(执行数/期望数/通过数)与汇总,导出 JSON 工件。
>
> **约束**:test job 名在一个 test run 内唯一;调度与执行解耦;支持 stable/unstable 两条流。
> **验收**:mock 一个 2-job 的 tier 配置,校验器通过,scheduler 能分配并汇总出结果 JSON;构造非法配置断言校验器报错。

### 失败三查 + 自动建单

> 实现 `acceptance/triage/`:`picker` 挑失败 → `table_rules`/`code_rules` 按已知模式归类 → `teams` 映射团队 → `jira_creator` 建缺陷单(先查是否已存在同类未关闭单,去重) → 通知负责人。
> **验收**:同一批失败跑两次,第二次不应重复建单;修改一个失败使其唯一后重跑,只建那一个单。

### 仓库自身 PR 校验流水线

> 实现 `pipelines_pr_validation.Jenkinsfile`:把每类校验封装成 closure,逐个作为 stage 执行,`results.every { it }` 判断整体是否通过;失败写回 build description。校验项至少含:Job Configs(首位)、Workflow Code、Validator/Runner/Scheduler Code 的语法与单元校验。
> **验收**:本地 `make check-repo` 全绿;故意引入语法错的库,PR 校验对应 stage 失败。

## C. 迭代技巧

- **贴报错原文**,要求"最小改动修复,不要重构其它库"。
- **钉住接口**:loader 别名、job 命名、结果 JSON 结构是契约,不许擅改。
- **让它自证**:每阶段跑 `make check` / CodeNarc / PR 校验,把输出贴出来再说完成。

## D. 收尾 Checklist

```text
[ ] 库与成品分离,库代码无 stages
[ ] loader 按分支加载,依赖清晰
[ ] Job 全部由生成器生成,命名遵守约定
[ ] 打包产出带 fingerprint 可溯源
[ ] 分层测试:scheduler/runner/workflows/tier_configs/validator 齐全,结果 JSON 统一
[ ] 失败三查 + 自动建单去重 + 通知
[ ] 覆盖率采集与看板
[ ] 仓库 PR 校验流水线(closure 列表 + every)+ CodeNarc + ShellCheck + DevContainer + pre-commit 全绿
```
