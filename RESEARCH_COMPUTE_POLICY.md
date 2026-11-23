# ColliderAgent execution adapter

**Status:** Project-specific extension to the central Research Compute Policy.  
**Central source commit:** 142267bc803c90aa681110293b66b73947bbcaa1  
**Scope:** Magnus and approved runner integration for the ColliderAgent HEP toolchain.

The shared rules for primary execution environment selection, GitHub archival, Actions-based independent verification, run provenance, fallback behavior, and execution security are defined by the [central Research Compute Policy](https://github.com/lm846802297-bit/high-energy-theory-research/blob/142267bc803c90aa681110293b66b73947bbcaa1/RESEARCH_COMPUTE_POLICY.md). The [central standards index](https://github.com/lm846802297-bit/high-energy-theory-research/blob/142267bc803c90aa681110293b66b73947bbcaa1/docs/governance/CENTRAL_STANDARDS_INDEX.md) and [research/standards-lock.yaml](research/standards-lock.yaml) identify the adopted revision.

This file defines only the ColliderAgent-specific execution adapter. It does not change the central distinction between ChatGPT Linux, Windows local execution, GPT-managed cloud computers, and GitHub Actions.

## 1. Magnus as an explicitly designated HEP backend

ColliderAgent uses Magnus to provide specialized stages involving FeynRules, Mathematica/Wolfram Engine, MadGraph5, Pythia8, Delphes, and MadAnalysis5.

- First use the primary execution environment selected under the central policy for tasks whose required tools, inputs, and resources are available there.
- Designate Magnus only for a pipeline stage that requires its specialized toolchain and cannot be run in the selected primary environment. The task brief or run record must explicitly identify the Magnus stage and why it is assigned to that backend.
- Magnus is an external execution backend. It is not the selected primary environment and is not GitHub Actions.
- Record the exact Magnus job/run identity, backend or image, source revision, model/UFO identity, process and cards, input artifacts, physical parameters, event counts and random seeds, tool versions, logs, output paths, and SHA-256 checksums.
- Keep independent checks separate from the Magnus production run. Use analytic/model checks, reduced local benchmarks, cross-section and normalization checks, regression tests, and downstream analysis validation as appropriate. Successful orchestration or remote job completion does not establish physical correctness.
- A Magnus working directory or downloadable job artifact is not a permanent archive. GitHub or the designated durable research repository remains the canonical record.

## 2. Approved self-hosted runner boundary

This repository is public. Do not register a persistent private Windows self-hosted runner directly with this repository.

If a task is explicitly approved to use the private Windows runner, dispatch it only through the approved private control workflow. The control path must use reviewed reusable workflows, full immutable commit SHAs, explicit checkout of the intended repository and revision, and least-privilege permissions. Do not execute untrusted pull-request code or arbitrary contributor commands on the persistent runner.

A self-hosted Actions runner remains a GitHub Actions execution even if it is physically hosted on the same Windows machine used for direct local work. Record it as an Actions run, not as direct Windows local execution or a GPT-managed cloud-computer run.

## 3. Security

- Never commit Magnus API keys, access tokens, credentials, private keys, local environment files, or machine-specific secrets.
- Keep restricted inputs and non-redistributable event samples outside public Git history; record authorized retrieval instructions and immutable checksums.
- Do not broaden runner permissions or change repository protection settings as part of an ordinary research task.

## 中文摘要

本文件只规定 ColliderAgent 的专用执行适配；主计算环境、GitHub 归档、Actions 独立验证和运行溯源以锁定版本的中央科研计算规范为准。

- 对于当前主计算环境能够完成的任务，优先在该环境执行。
- 只有需要专用 HEP 工具链且当前主环境无法提供时，才在任务说明中明确指定 Magnus 执行相应阶段。
- Magnus 运行必须记录 job/run 身份、环境、源码、模型、卡片、输入、参数、随机种子、工具版本、日志、原生输出和 SHA-256。
- 不得将私有 Windows self-hosted runner 直接注册到公开的 ColliderAgent 仓库。需要使用时，只能经批准的私有控制工作流调度，并固定完整源码 SHA、明确 checkout 和权限。
- Magnus 工作区和 Actions artifact 均不能替代 GitHub 上的永久结果归档；工具执行成功也不等于模型、事例产生、分析或物理复现已经验证。
