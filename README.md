# FastSim Mission 两个契约问题的最小复现

这个仓库记录两个阻碍真实数据生产的问题：G2 + OmniPicker3 E 对目标箱的原生 CuRobo 接触规划失败，以及 Mission 评价拒绝由 SceneQuery 返回的 `frame.world` 世界帧。两者独立：即使解决抓取，评价仍可能中止。

**当前结果：FastSim-Benchmark 主分支（2026-09-25）尚未解决这两项问题。**`scripts/probe_contracts.py` 可以无 GPU、无资产复现当前公开接口的行为；`repro/` 保留已经在 GPU 上触发问题的最小任务配置与移箱对照。配置解析、动作执行和真实物理抓取是不同验收层级，本仓库不把任何失败样本称为可生产配置。

## 一分钟契约探针

依赖已配置的 `isaac6` 环境与 FastSim-Plugins 主分支。以下命令在仓库根目录执行：

```bash
mkdir -p deps
git clone --branch main git@github.com:FastSim-Benchmark/FastSim.git deps/FastSim
git -C deps/FastSim checkout cef24ab537929b7974d1c241569acaa1fa72b46b
git clone --branch main git@github.com:FastSim-Benchmark/FastSim-Plugins.git deps/FastSim-Plugins
git -C deps/FastSim-Plugins checkout cc4d86b
PYTHONPATH="$PWD/deps/FastSim/src:$PWD/deps/FastSim-Plugins/packages/fastsim-plugin-mission/src:$PYTHONPATH" \
  conda run -n isaac6 python scripts/probe_contracts.py
```

已观察的主分支输出：字面 `world` 的零速度可评价并通过；相同事实改用 `frame.world` 后返回 `FRAME_UNSUPPORTED`；目标物已绑定一个碰撞几何 ID，但 `_grasp_collision_policy` 返回没有目标接触授权的空策略。第三项只是接口探针，真实轨迹失败由下述 GPU 对照证明，不能仅凭空策略推断任何物理抓取结果。

## GPU 对照复现

完整命令、资产前提和预期结果见 [GPU_REPRO.md](GPU_REPRO.md)。大型标准场景、机器人和任务资产没有上传到 Git；它们通过数据准备团队的 `portable_delivery` 资产包放入 `input/portable_delivery/`，或由有权限的同事从固定 SVN r63 重建。这个包约 2.8 GB；本仓库不包含任何本机绝对路径、内网 SVN 地址或凭证。

## 文件

- [ISSUES.md](ISSUES.md)：两个问题的因果证据、公共接口缺口和正反验收条件。
- [UPSTREAM_REVIEW.md](UPSTREAM_REVIEW.md)：2026-09-25 主分支更新核查、版本与实际检查边界。
- [GPU_REPRO.md](GPU_REPRO.md)：使用原生 `fastsim run` 的直接命令，不通过启动脚本。
- [OWNER_PROMPT.md](OWNER_PROMPT.md)：可交给接口契约所有者 Codex 的开发提示词。
- `repro/`：诊断配置，不是生产配置；`scripts/probe_contracts.py`：无资产的接口行为探针。

本仓库没有修改任何 FastSim-Benchmark 仓库源码，未通过插值、对象瞬移、全局关闭碰撞或模拟挂接伪造任务成功。目标仍是可物理抓起并放下的任务配置。
