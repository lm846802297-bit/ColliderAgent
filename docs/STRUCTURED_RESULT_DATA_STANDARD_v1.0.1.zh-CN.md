# ColliderAgent RCRPS v1.0.1 对撞机领域扩展

**状态：** 中央 RCRPS v1.0.1 的项目专属扩展。  
**中央规范提交：** 142267bc803c90aa681110293b66b73947bbcaa1

公共记录类型、通用字段、14 字段源码控制来源契约、状态语义和 JSON Schema 要求，统一由[中央结构化科研结果数据规范 v1.0.1](https://github.com/lm846802297-bit/high-energy-theory-research/blob/142267bc803c90aa681110293b66b73947bbcaa1/docs/STRUCTURED_RESULT_DATA_STANDARD_v1.0.1.md)定义。本文件只规定 ColliderAgent 专属扩展和运行约定，不再复制中央规范正文。

本地 Schema、Validator、固定版本验证依赖和回归测试位于 docs/schemas。v1.0.1 Schema 按原有要求兼容历史 v1.0.0 记录；新的重要运行使用 v1.0.1。

## 1. 进度记录与最终运行记录

- progress/run_manifest.yaml 继续作为增量编排进度记录，保存 run label、parent、时间戳和各流水线阶段状态。
- 每次重要数值计算、模拟、扫描或验证运行完成后，execution-summarizer 必须在结果目录生成最终 run_manifest.json、result_summary.json 和 validation_report.json。
- 最终 run_manifest.json 必须包含中央规范要求的完整 14 字段 execution.source_control 对象。应在创建输出文件前捕获，并保留运行时实际使用的 source.commit_sha。
- 不得覆盖之前的运行记录或输出。增量运行使用新 run label 并关联 parent。

## 2. 对撞机专属 extensions.collider_mc

将以下对撞机专属信息放在 extensions.collider_mc 中，中央 RCRPS 公共字段仍保留在顶层：

- 模型/UFO 名称、版本和文件指纹；过程定义及粒子多重态定义。
- 对撞机类型、束流能量、质心能量、PDF set/版本、重整化和因子化尺度。
- 产生级 cuts、匹配/合并设置、衰变链、宽度方案和随机种子。
- 实际使用的 MadGraph、Pythia8、Delphes、MadAnalysis5、FeynRules、LHAPDF 等工具版本。
- 请求、生成和选中的事例数；事例权重；截面；统计误差。
- Pythia 簇射 tune、强子化/衰变设置、Delphes 探测器卡、pile-up 假设、重建对象定义、cutflow 和系统误差。
- 每种事例输出的数据层级：LHE 为 parton level，HepMC 为 hadron level，LHCO/ROOT 为 reconstructed 或 detector-analysis level。其他格式也必须明确记录其层级映射。

## 3. 原生数据与分析约定

- cutflow、直方图表、截面扫描及其他便于直接检查的表格使用 CSV。
- 事例级输出保留 LHE、HepMC、ROOT 或 Parquet 原生格式，并记录事例数、权重约定、字节数和 SHA-256。
- 生成事例、簇射后事例、探测器/重建级事例、选中样本和派生直方图必须能够区分。
- 对结果有影响时，记录对象定义、cut 顺序、积分亮度、归一化、过滤效率、k-factor、分支比以及统计/系统误差。

## 4. 验证状态分离

根据任务类型使用中央 Research Quality Gate。以下 ColliderAgent 专属验证状态必须分别记录：

- 工具或 blueprint 执行；
- FeynRules 模型和 UFO 验证；
- MadGraph 事例产生验证；
- Pythia 簇射与 Delphes 探测器验证；
- MadAnalysis cutflow/直方图验证；
- 数值/统计验证；
- 论文复现的科学状态。

工具调用成功或 Schema 校验通过，不等于物理模型、事例产生、探测器响应、分析或科学复现结论已经验证。

## 5. 验证命令

安装固定版本依赖并运行本地回归测试：

    python -m pip install -r docs/schemas/requirements-result-validation.txt
    python -m unittest discover -s docs/schemas/tests -v
    python -m compileall -q docs/schemas

对本次运行实际存在的记录进行校验：

    python docs/schemas/validate_result_records.py --schema docs/schemas/research-result-record-v1.0.1.schema.json --repo-root . results/<run_label>/run_manifest.json results/<run_label>/result_summary.json results/<run_label>/validation_report.json

Validator 检查严格 JSON 解析、Schema、引用文件路径和哈希、CSV 维度/单位以及 v1.0.1 源码控制语义。通过 Validator 只证明这些结构和完整性属性，不证明物理正确性。

## 6. 历史 v1.0.0 记录

v1.0.0 规范和 Schema 仅为历史兼容而保留。不得重写历史事例输出，也不得伪造缺失的来源字段。新的重要运行采用中央 RCRPS v1.0.1 和本对撞机领域扩展。
