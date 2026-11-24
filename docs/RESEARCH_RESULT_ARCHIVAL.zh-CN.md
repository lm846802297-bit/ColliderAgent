# ColliderAgent 研究结果归档扩展规范

**状态：** 中央计算结果归档规范的项目专属扩展。  
**中央规范提交：** 14155487afc075d301fa7f6cf452c7bff137e869

原生文件归档、解压后提交、运行溯源、校验和、远端核验，以及归档状态与科学验证状态分离等共享要求，统一遵循[中央计算结果归档规范](https://github.com/lm846802297-bit/high-energy-theory-research/blob/14155487afc075d301fa7f6cf452c7bff137e869/docs/CALCULATION_RESULT_ARCHIVAL_POLICY.md)。本文件只规定 ColliderAgent 专属的结果位置、事例数据处理和 HEP 运行元数据。

## 1. 规范结果位置

- ColliderAgent 首先是可复现计算流程和 Agent 工具仓库。如果某项论文结果属于另一个研究项目，应将权威科学结果归档到该项目仓库，并在执行总结中记录不可变仓库路径、commit 和 PR。
- 如果明确决定将某项复现作为 ColliderAgent 示例维护，则使用 paper-reproduction/<arXiv-ID>/results/<run_label>/。
- 提示词、原始论文材料和生成结果分开保存。每次增量运行使用新的 run label，并记录 parent。
- 模型源码、UFO 目录、脚本/卡片、原始事例样本、处理后的分析表、图像、进度记录和最终总结应明确区分。

## 2. 对撞机原生输出

根据实际执行的阶段，保留可检查和复现的原生文件：

- FeynRules 模型源码和生成的 UFO 文件；
- 准确的 MadGraph 过程定义、脚本、参数卡、运行卡、banner 和日志；
- LHE、HepMC、ROOT 或 Parquet 等原生事例数据；
- Pythia8 设置、Delphes 探测器卡、MadAnalysis 脚本和分析代码；
- 截面表、cutflow、加权产额、直方图、图像和后处理输出；
- 进度记录、最终 RCRPS 记录、执行总结和校验和清单。

原始事例、簇射后事例、探测器/重建级数据、处理后的表格和图像必须分开保存。记录所有事例选择、过滤、归一化、直方图处理和其他数据转换。

## 3. Monte Carlo 与受限输出的三层存储

根据数据用途、体量、访问模式、持久性、许可和项目预算选择存储层。不得仅为了统一存储方式而迁移历史文件。

- **普通 Git：** 保留模型源码、脚本/卡片、Manifest、Provenance、验证报告、小型/中型 CSV/JSON 输出、cutflow、直方图，以及仍便于检查和 clone 的适量原生事例样本。
- **Git LFS：** 对需要与项目版本绑定、且仍适合随项目工作集获取的大型二进制事例样本或探测器级输出，可前瞻性采用。Git 中保留 LFS pointer，并记录对象 SHA-256/OID、字节数、格式、来源 run label 和引用该对象的 commit。必须实际下载对象并验证字节；仅有 pointer 不代表数据可用。
- **外部对象存储：** 对体量或访问模式已不适合 Git/LFS 的批量 LHE/HepMC/ROOT/Parquet 样本、大型扫描或长期数据集，使用持久对象存储。采用不可变对象/版本 ID，并在项目仓库保存清单，记录准确 URI/版本、文件名、字节数、事例/记录数量、格式、来源 run label、SHA-256、获取说明和保留责任。

对每个 LFS 或外部对象，上传后必须实际下载，并将精确字节与记录的 SHA-256 比较。不得将即将过期的 Magnus 工作区、临时 Runner 目录或 Actions artifact 作为唯一永久副本。不得提交凭据、私人数据或无权再分发的事例文件。没有明确的数据体量或保留需求时，不启用 Git LFS 或外部存储。

## 4. 对撞机运行元数据

现有 progress/run_manifest.yaml 继续作为增量编排和进度记录。每次重要运行完成后，还必须在结果目录中生成中央 RCRPS v1.0.1 要求的最终记录：

- run_manifest.json：实际源码 checkout、输入、参数、环境、命令、输出、来源和归档状态；
- result_summary.json：物理/数值结果、单位、不确定度、研究范围和科学状态；
- validation_report.json：仅记录实际执行的检查、方法、观测值、阈值和证据。

JSON 运行清单必须包含中央 RCRPS v1.0.1 要求的完整 14 字段 execution.source_control 对象。应在运行开始、生成输出文件之前捕获该对象，并保留运行时实际使用的 source.commit_sha。进度 YAML 不能代替最终 JSON 运行清单。

对撞机专属字段见本地 [RCRPS v1.0.1 ColliderAgent 扩展](STRUCTURED_RESULT_DATA_STANDARD_v1.0.1.zh-CN.md)。

## 5. 归档状态与科学状态

执行总结必须使用准确的归档状态：

- local only；
- committed to PR branch；
- merged and verified on main。

推送后从远端重新读取文件，比较路径、大小、数量和 SHA-256。不得将 Magnus 任务完成、上传命令成功或程序正常退出等同于 GitHub 永久归档。

归档状态必须与程序执行、模型验证、事例产生验证、探测器/分析验证、数值验证和科学复现状态分开。事例样本完整或哈希一致本身不能证明物理结论成立。
