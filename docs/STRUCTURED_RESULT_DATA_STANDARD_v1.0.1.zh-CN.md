# 结构化科研结果数据规范 v1.0.1

**状态：** **已于 2026-11-23 由项目负责人正式采用**，自该日起适用于新的重要数值计算、模拟、参数扫描和计算验证。正式采用记录见[中央正式采用记录](https://github.com/lm846802297-bit/high-energy-theory-research/blob/main/docs/governance/RCRPS_V1.0.1_ADOPTION_RECORD.md)。历史结果不追溯改写。  
**规范版本：** `1.0.1`；JSON Schema：Draft 2020-12。  
**适用边界：** 本规范统一数据结构、运行来源和归档方式；它不把软件测试通过等同于物理结论成立。

## 1. 标准结果包

重要计算的规范结果目录采用以下角色分离。实际项目可以按专题目录组织，不要求每个任务机械地创建所有文件。

```text
results/<run_label>/
├── run_manifest.json       # 本次真实执行的来源、配置、环境、命令和输出清单
├── result_summary.json     # 物理/数值结果摘要及其适用范围
├── validation_report.json  # 实际执行的解析、数值、收敛和独立验证
├── *.csv                   # 可直接分析的逐点数据、扫描表或积分表
├── SHA256SUMS.txt          # 结果文件的 SHA-256
└── README.md               # 人类可读的结论、复算命令和状态
```

- 对重要运行，必须有 `run_manifest.json` 或字段等价的机器可读运行清单。
- 对正式数值结果，必须有 `result_summary.json`；现有项目中已承担相同角色的 JSON 可以保留原文件名。
- 进行了验证时，应记录 `validation_report.json`，或在运行清单中完整保存同等检查信息。
- 存在逐点数值、能谱、径向曲线、参数扫描或响应网格时，优先保存原生 CSV/ROOT/HDF5/Parquet 等数据文件，不把大数组全部塞入 JSON。
- `README.md` 解释结果；它不能代替底层 JSON、CSV、脚本和输入数据。

## 2. 三类 JSON 的职责

### 2.1 `run_manifest.json`：这次计算是怎样产生的

至少记录：

- `schema_version`、`record_type=run_manifest`、稳定的 `run_id` 和 UTC 时间；
- 仓库、项目和工作流标识；
- 实际运行所用 Git commit SHA、分支、入口脚本路径及脚本指纹；
- 输入文件的来源、版本、格式、路径/URI、大小、SHA-256，以及所有数据转换；本地输入必须同时提供仓库相对路径和 SHA-256；输入字节不可取得时，必须提供不可变 URI 和明确版本；
- 物理参数、数值参数和约定：质量、耦合、单位、近似、网格、求积阶数、精度、容差、边界条件、随机种子等；
- 操作系统、运行时、依赖包版本、硬件；Schema 要求提供入口脚本 SHA-256，并显式记录 runtime、dependencies 和 hardware；
- 精确命令、开始/结束时间、退出码和运行时长；
- 每个输出文件的相对路径、角色、格式、字节数、SHA-256；CSV 还记录行数、列名和单位；
- 验证状态、各项检查的实际结果，以及 Git 归档状态。

运行清单记录**实际执行的版本**，不能写当前分支最新 SHA 来替代计算发生时的源码 SHA。

### 2.2 `result_summary.json`：计算得到了什么

至少记录：

- `run_id`，并与运行清单一一对应；
- 计算对象、过程、模型分支和研究范围；
- benchmark 的完整物理参数与单位；
- 关键可观测量：数值、单位、定义、误差/不确定度，以及必要的维度标签（例如极化、同位素、通道、耦合点）；
- 对应逐点数据文件的路径、SHA-256、行数、列名和单位；
- 科学状态：`diagnostic`、`provisional`、`reproducible`、`validated`、`historical` 或 `superseded`；
- 结果解释、适用范围和明确排除的内容。

数值应保存为 JSON number，不要把数值写成带单位的字符串。单位放在独立字段。未计算的量使用 `null` 并标注 `not_computed`；不得用 0 代表缺失或未执行。每个 observable 都必须有 `status`：`computed`、`not_computed` 或 `not_applicable`。

下面是**纯格式示例**，数值为人为构造，不是科研结果：

```json
{
  "schema_version": "1.0.0",
  "record_type": "result_summary",
  "run_id": "EXAMPLE-RUN-001",
  "created_at": "2026-11-20T00:00:00Z",
  "project": {
    "repository": "example/research",
    "project_id": "example-project"
  },
  "calculation": "Synthetic schema fixture only",
  "scope": {
    "included": ["data-format validation"],
    "excluded": []
  },
  "benchmark": {
    "mass": {"value": 1.0, "unit": "MeV"}
  },
  "observables": [
    {
      "name": "example_quantity",
      "value": 1.0,
      "unit": "arb.",
      "status": "computed"
    }
  ],
  "data_files": [],
  "scientific_status": "diagnostic",
  "interpretation": "Synthetic example; not a physical result."
}
```

### 2.3 `validation_report.json`：哪些检查实际通过

每项检查记录唯一 ID、名称、类别、状态、方法、观测值、阈值、单位和证据路径。至少区分：

- 解析恒等式和极限；
- 单位、量纲和归一化；
- 软件单元/回归测试；
- 数值积分和网格收敛；
- 独立实现或文献基准交叉验证；
- 物理适用范围检查；
- 文件完整性和哈希检查。

不能用一个总的 `PASS` 替代检查明细，也不能把未执行的检查标成通过。

## 3. 源码控制与检出来源（v1.0.1）

每一个新建的 v1.0.1 `run_manifest` 都必须包含 `execution.source_control`，且下面 14 个字段全部必填。实际检出的 Git commit 唯一记录在 `source.commit_sha`，不再增加重复的 `checked_out_sha`。

| 字段 | 含义 |
|---|---|
| `event` | 实际执行事件，例如 `pull_request`、`pull_request_target`、`push`、`workflow_dispatch`、`schedule`、`workflow_run`、`merge_group` 或 `local` |
| `checkout_mode` | `pull_request_merge`、`pull_request_head`、`pull_request_base`、`branch_commit`、`detached_commit` 或 `unknown` |
| `checkout_ref` | `refs/` 下完整限定且符合 Git ref 命名规则的检出 ref；detached 或无法获取时为 null |
| `pr_number` | PR 编号；非 PR 事件为 null |
| `pr_url` | PR 规范 URL；非 PR 事件为 null |
| `pr_head_sha` | PR 源分支 HEAD SHA；非 PR 事件为 null |
| `base_sha` | PR 目标分支基准 SHA；非 PR 事件为 null |
| `tested_merge_sha` | 仅当实际检出并执行了合成 merge commit 时记录其 SHA，否则为 null |
| `head_ref` | 符合 Git 分支命名规则的 PR 源分支名称；非 PR 事件为 null |
| `base_ref` | 符合 Git 分支命名规则的 PR 目标分支名称；非 PR 事件为 null |
| `workflow_run_id` | Workflow 运行标识；不存在时为 null |
| `workflow_run_attempt` | 正整数形式的 Workflow 运行尝试次数；不存在时为 null |
| `working_tree_state` | `clean`、`dirty` 或 `unknown` |
| `dirty_paths` | dirty 工作树中发生修改或未跟踪的唯一仓库相对 POSIX 路径；clean 时为空数组 |

### PR 事件

对于 `pull_request` 和 `pull_request_target`，PR 编号、URL、head/base SHA 以及 head/base ref 必须非 null。`source.commit_sha` 记录实际检出的 commit；`checkout_mode` 描述该 commit 在 PR 事件中的角色，`checkout_ref` 则在可确定时单独记录精确 Git ref：

- `pull_request_merge`：`tested_merge_sha` 必须等于 `source.commit_sha`。
- `pull_request_head`：`source.commit_sha` 必须等于 `pr_head_sha`，且 `tested_merge_sha` 为 null。
- `pull_request_base`：`source.commit_sha` 必须等于 `base_sha`，且 `tested_merge_sha` 为 null。这覆盖 `pull_request_target` 工作流实际执行目标分支的情况。
- `unknown`：仍须记录实际的 `source.commit_sha`，并将 `tested_merge_sha` 设为 null；没有证据时不得声称检出了 merge commit。

当 `checkout_ref` 已知时，它必须与 checkout mode 一致：
- `pull_request_merge`：`refs/pull/{pr_number}/merge`；
- `pull_request_head`：`refs/pull/{pr_number}/head` 或 `refs/heads/{head_ref}`；
- `pull_request_base`：`refs/heads/{base_ref}`；
- `unknown`：可以记录任意符合 Git 规则的完整限定 ref。

当精确 ref 无法获取或检出为 detached 状态时，`checkout_ref` 可以为 null。

`head_ref`、`base_ref` 和 `checkout_ref` 含义不同。比如 `refs/pull/104/merge` 是检出 ref，不是贡献者的 `head_ref`。所有非 null 的 `checkout_ref` 必须是 `refs/` 下的完整限定 Git ref，并符合 Git ref 命名规则；`head_ref` 和 `base_ref` 必须是合法的 Git 分支名称。

PR merge 运行示例片段（值仅作说明）：

```json
{
  "source": {"commit_sha": "<tested-merge-sha>"},
  "execution": {
    "source_control": {
      "event": "pull_request",
      "checkout_mode": "pull_request_merge",
      "checkout_ref": "refs/pull/104/merge",
      "pr_number": 104,
      "pr_url": "https://github.com/example/research/pull/104",
      "pr_head_sha": "<pr-head-sha>",
      "base_sha": "<target-base-sha>",
      "tested_merge_sha": "<tested-merge-sha>",
      "head_ref": "feature/example",
      "base_ref": "main",
      "workflow_run_id": 123456,
      "workflow_run_attempt": 1,
      "working_tree_state": "clean",
      "dirty_paths": []
    }
  }
}
```

### 非 PR 事件

对于所有非 PR 事件，七个 PR 专用字段（`pr_number`、`pr_url`、`pr_head_sha`、`base_sha`、`tested_merge_sha`、`head_ref` 和 `base_ref`）都必须存在且显式设置为 `null`。不能省略，也不能填写占位 SHA。

根据实际情况使用 `branch_commit`、`detached_commit` 或 `unknown`。对于非 PR 事件，`branch_commit` 必须提供非 null 的 `checkout_ref`，而 `detached_commit` 的 `checkout_ref` 必须为 null；`unknown` 在实际 ref 已知时仍可记录该 ref。无论哪种情况，`source.commit_sha` 都记录实际使用的 commit。没有 Workflow 的本地运行将 `workflow_run_id` 和 `workflow_run_attempt` 同时设为 null；存在 Workflow 时二者必须同时填写。旧字段 `source.workflow_run_id` 为兼容 v1.0.0 而保留；如果它出现在 v1.0.1 manifest 中，其值和 JSON 类型必须与 `execution.source_control.workflow_run_id` 完全一致。新的 v1.0.1 记录应省略这个旧的重复字段，统一使用 execution 中的规范字段。

本地运行示例片段：

```json
{
  "source": {"commit_sha": "<actual-commit-sha>"},
  "execution": {
    "source_control": {
      "event": "local",
      "checkout_mode": "branch_commit",
      "checkout_ref": "refs/heads/main",
      "pr_number": null,
      "pr_url": null,
      "pr_head_sha": null,
      "base_sha": null,
      "tested_merge_sha": null,
      "head_ref": null,
      "base_ref": null,
      "workflow_run_id": null,
      "workflow_run_attempt": null,
      "working_tree_state": "clean",
      "dirty_paths": []
    }
  }
}
```

clean 工作树要求 `dirty_paths` 为空；dirty 工作树至少需要一个路径。路径必须规范化、唯一、相对于仓库根目录，采用 POSIX 格式，不能包含 NUL 字节，不能是绝对路径或包含向上遍历。如果 dirty 源文件影响了计算，必须归档并指纹化实际修改内容或可复现补丁/快照；仅记录路径名称不足以复现 dirty 源码。

v1.0.1 Schema 是向后兼容的校验超集：它继续接受符合原要求的 v1.0.0 记录，同时只对 v1.0.1 的 `run_manifest` 强制要求 `execution.source_control`。`result_summary` 和 `validation_report` 不增加源码控制字段。v1.0.0 Schema 保持不变，历史记录不重写。

## 4. CSV 与数值数组规范

1. 第一行为稳定列名；每列只表达一个物理量。
2. 单位必须明确：优先在列名中使用 `r_km`、`omega_MeV`、`ER_keV` 等，或在 JSON 的 `units` 字典中逐列声明。不得依赖读者猜测单位。
3. 多维数据采用 long/tidy format：每行对应一个网格点/样本，极化、同位素、过程、耦合等作为独立维度列；不要把不同极化或同位素混在无标签的数组里。
4. 数值列只放数值；不把单位、注释或状态文字混入数值列。缺失值与物理零值必须区分。
5. 不写入 NaN 或 Infinity。缺失项使用空字段并在数据字典中说明，或使用单独状态列。
6. 保留足以复现计算的有效数字；不得在归档时擅自降低精度、改变列顺序或重采样。
7. JSON/CSV 中的数值、行数、单位、积分网格和结果摘要必须相互一致。

对大数组和大型事件样本，使用项目允许的原生二进制格式或 Git LFS/持久版本化存储，并在清单中记录格式、记录数、大小、不可变位置和 SHA-256。

## 5. 三种状态必须分开

| 字段 | 含义 | 推荐值 |
|---|---|---|
| `execution.status` | 程序是否实际执行 | `succeeded`、`partial`、`failed`、`cancelled`、`blocked`、`running`、`not_started` |
| `validation.status` | 已执行的检查结果 | `passed`、`partial`、`failed`、`blocked`、`inconclusive`、`not_run` |
| `scientific_status` | 结果支持的科学成熟度 | `diagnostic`、`provisional`、`reproducible`、`validated`、`historical`、`superseded` |
| `archive.status` | 文件实际归档位置 | `local_only`、`committed_to_pr_branch`、`merged_and_verified_on_main` |

程序正常退出不等于数值收敛；测试通过不等于物理结论已经验证；文件上传成功不等于已经在 main 上完成归档。

## 6. 项目扩展方式

公共字段放在规范顶层；研究领域特有字段放入 `extensions`，使用稳定的领域名称作为命名空间。不要为了统一格式而丢弃物理上必要的变量，也不要把不同物理层级混为一个观测量。

## 7. Schema 校验和归档验收

本仓库配套的 `docs/schemas/research-result-record-v1.0.1.schema.json` 使用 JSON Schema Draft 2020-12，支持 `run_manifest`、`result_summary` 和 `validation_report` 三类记录。安装依赖并执行本仓库校验器：

```bash
python -m pip install -r docs/schemas/requirements-result-validation.txt
python docs/schemas/validate_result_records.py --schema docs/schemas/research-result-record-v1.0.1.schema.json --repo-root . results/<run_label>/run_manifest.json results/<run_label>/result_summary.json results/<run_label>/validation_report.json
```

校验器检查 Schema、严格 JSON 数值、引用文件路径/字节数/SHA-256，以及 CSV 的行数、列名、逐列单位和非有限数值。只传入本次实际存在的 JSON 文件。

使用 `python -m unittest discover -s docs/schemas/tests -v` 运行回归测试，覆盖非标准 JSON 常量、浮点溢出/下溢以及输入来源定位规则。

`status=passed` 仅在至少有一项检查且所有检查均为 `passed` 时允许使用；部分完成或含失败项必须使用 `partial`、`failed` 或 `inconclusive`。

归档前逐项检查：

- JSON 能严格解析且通过 Schema；
- CSV 列名、单位、行数、数值有限性和网格覆盖正确；
- 所有引用文件存在，字节数、行数和 SHA-256 相符；
- 运行清单的源码 SHA、输入指纹、参数和命令对应真实执行；
- 验证状态只反映实际执行的检查；
- 推送后重新从 GitHub 读取文件，核对路径、大小、数量和 SHA-256。

## 8. 历史结果迁移

本规范从采用后的新运行开始执行。既有 JSON、CSV、日志、图像和历史运行记录保持原样，不为满足新格式而重写原始数据、改变精度或伪造缺失字段。旧文件可由新的索引/运行清单引用，并明确标记为 legacy；只有在能从原始记录中核实的字段才允许补充。

---

## 本仓库的领域扩展

### 对撞机 Monte Carlo / 论文复现

现有 `progress/run_manifest.yaml` 可继续作为运行中的进度记录；每次重要运行归档时，应同时导出符合本规范的最终 `run_manifest.json`，并与 `result_summary.json`、`validation_report.json` 及原生事例文件一起归档。

`extensions.collider_mc` 应记录：

- 模型/UFO 名称、版本和文件指纹，过程定义与粒子多重态；
- collider 类型、束流能量、$\sqrt{s}$、PDF set/version、重整化/因子化尺度；
- generation cuts、匹配/合并、衰变链、宽度方案、随机种子；
- MadGraph、Pythia8、Delphes、MadAnalysis5、FeynRules、LHAPDF 等实际使用版本；
- requested/generated/selected event counts、event weights、截面和统计误差；
- shower tune、detector card、pile-up、object definitions、cutflow 和系统误差；
- LHE/HepMC/ROOT 等数据所处的 parton/hadron/reconstruction 层级。

cutflow、直方图、截面扫描优先用 CSV；大型 event sample 使用原生 LHE/HepMC/ROOT 或 Parquet，并记录事件数、权重约定、大小和 SHA-256。工具/blueprint 成功、模型验证、事例生成、分析验证和论文复现状态必须分别记录。
