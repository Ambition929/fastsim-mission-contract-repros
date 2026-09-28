# 给接口契约所有者 Codex 的提示词

> 我有两个可复现的 FastSim Mission 契约问题，另有一个已解除的主分支运行时版本缺口记录，资料都在本仓库。请先读 `README.md`、`ISSUES.md`、`UPSTREAM_REVIEW.md`、`GPU_REPRO.md`、`RUNTIME_RELEASE_SKEW.md`，然后在你有权限的 FastSim / FastSim-Plugins / curobo 源仓库按各自 AGENTS.md 检查 origin、工作区、README 和相邻测试。只处理主分支，保持正式公共接口；不要修改本仓库的诊断输入来掩盖失败。
>
> 问题一：OP3 E 对真实目标箱的完整 13 关节闭指原生 CuRobo 规划 infeasible，箱子移开后相同动作可执行，但目标物没有物理抬升。设计并实现最小请求级抓取接触契约，按对象 ID、允许的指端链路、路径阶段、容限和捕获世界版本约束，不准全局禁用目标、桌面或其他障碍碰撞，不准用插值、对象瞬移或模拟附件当抓取成功。正反测试须覆盖错误对象、掌部/桌面接触、中途穿箱、过期 revision 与实际 PhysX 抬升/释放。
>
> 问题二：`scene.query` 给出 `frame.world`，Mission 评价只认字面 `world`，导致 `linear_speed`/位姿评价不可用。请用正式帧目录和同一代证据确认唯一世界帧，同时检查 pose/twist 同帧；保留局部、未知、伪造或跨代帧的失败封闭语义。不要只添加字符串白名单。
>
> 运行时版本缺口：当前 FastSim 要求 UniRoboSim 0.10.9（相机的 `render_exclusions`）和 Isaac Lab provider 0.10.24（精确 alias 锁），该缺口已由官方 v0.10.9/v0.10.24 发布解除。先运行 `scripts/probe_runtime_versions.py`，固定使用上述官方标签并检查与 FastSim 的公共 API；不得伪造分发元数据、猴子补丁或去相机冒充生产修复。
>
> 所有 Python、CLI、测试用 `conda run -n isaac6`。先跑本仓库无资产探针，再按 `GPU_REPRO.md` 直接使用 `fastsim run` 复现；补齐公共 schema、请求传递、规划器实现和正反契约测试。分别报告配置解析、场景加载、原生 CuRobo 路径、物理抓取/放置、Mission 评价。明确兼容性和仍未验证项。不要声称生成了生产配置，除非完整任务真的成功。
