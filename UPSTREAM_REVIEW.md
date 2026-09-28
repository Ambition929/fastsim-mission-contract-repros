# FastSim-Benchmark 主分支更新核查（2026-09-25）

按仓库 origin 和干净工作区检查后，只对远端执行 `git fetch`，未修改原工作树源码。隔离副本用于探针。与本问题直接相关的主分支：

| 仓库 | 检查时主分支提交 | 相对上次本地版本 | 与本问题有关的变化 |
| --- | --- | --- | --- |
| FastSim | `cef24ab537929b7974d1c241569acaa1fa72b46b` | 无 | SceneQuery 帧映射无新变更 |
| FastSim-Plugins | `cc4d86b` | +1 提交 | 关节保持、物理 yaw 边界；`evaluation/engine.py::_pose` 仍只接受 `world`，`_grasp_collision_policy` 仍返回空策略 |
| curobo | `c179b80` | +3 提交 | 记录被拒绝轨迹的碰撞/IK 诊断；没有改变接触接受规则 |
| layoutgen | `b071cb5` | +1 提交 | 把 USD cube 纳入摆放障碍物筛选；不触及以上两项接口 |

其他已检出的 FastSim-Benchmark 仓库主分支无更新。核查范围为当时全部 17 个有提交的仓库；组织元数据仓库 `.github` 无可检出的提交。这里只评估**主分支**。

在隔离的 FastSim-Plugins 新主分支上，运行 `scripts/probe_contracts.py` 的实际结果：

```json
{
  "frame": [
    {"input_frame_id": "world", "validity": "valid", "passed": true, "value_m_s": 0.0, "error_code": null},
    {"input_frame_id": "frame.world", "validity": "unavailable", "passed": null, "value_m_s": null, "error_code": "FRAME_UNSUPPORTED"}
  ],
  "grasp_collision_policy": {
    "target_object_id": "objects.target",
    "target_collision_id": "target/body",
    "disabled_collision_ids": [],
    "policy_type": "CollisionPolicy"
  }
}
```

该无资产探针确认主分支接口行为，不能代替 GPU 物理验证。原版 GPU 对照结果详见 [ISSUES.md](ISSUES.md)；新主分支直接 GPU 复跑结果以本文后续记录为准。不会把代码检查称为真实任务成功。


## 新主分支 GPU 复跑

`repro/frame_world_metric.yaml` 固定 seed `20260924`，60/60 Hz `accurate`，使用 FastSim-Plugins `cc4d86b`、curobo `c179b80` 的隔离源码副本直接运行 `fastsim run`。配置解析通过；GPU 运行返回 `ok=false`，仍是 `BlueprintExecutionError: metric requires an explicitly world-framed pose`。运行中的其他 IK 诊断不能解释为评价错误已经消失，也不能证明物理任务成功。

目标在场的 GPU 复跑也完成：repro/grasp_target_present.yaml 使用同一新版主分支、固定 seed 20260922；正式配置解析 ok=true；运行到第 4 段完整闭指时返回 ok=false，报 Mission arm solver 'finger_left_actuate' for motion 'close' failed with status infeasible，墙钟约 172.4 秒。新版 CuRobo 诊断未使这条目标在场的接触路径可行。物理抓取与完整任务仍未成功。

移箱对照在同一新版主分支上也直接 GPU 复跑：repro/grasp_target_moved.yaml 正式解析通过；FSR 记录 5 次原生控制、365 帧应用和 5 次结果，左箱最大抬升 0 m。之后 Mission 评价仍因 world 帧错误返回 ok=false。目标在场的 FSR 只有 3 次控制、283 帧应用，左箱最大抬升同为 0 m。结构化、脱敏结果见 evidence/main_gpu.json。由此可以分开确认：目标在场的闭指规划仍不可行；移箱后相同控制可执行；两者都不构成物理抓取成功，且评价错误仍存在。

## 2026-09-28 主分支再核查

FastSim `5b8520b26f`、FastSim-Plugins `e683734e8a`、layoutgen `aaf3acdfdb`、curobo `f2e2278c14` 的主分支已核查；原有无资产契约探针仍显示 `frame.world` 被拒以及目标抓取接触策略为空。新增的独立运行时版本缺口、最小无资产复现与 GPU 启动观察见 [RUNTIME_RELEASE_SKEW.md](RUNTIME_RELEASE_SKEW.md)。这些探针都不代表五任务通过。

### 同日再次拉取与探针

18 个 FastSim-Benchmark 仓库中仅 FastSim-Plugins 从 `e683734e8a` 快进至 `d8b7294cd0`。该提交只涉及 Mission 导航 yaw 请求准入及相邻文档、测试；无资产 `scripts/probe_contracts.py` 在新的插件提交上复跑，`frame.world` 仍为 `FRAME_UNSUPPORTED`，目标抓取接触策略仍是空列表。三相机直接 Run 仍在 `CameraSpec.render_exclusions` 失败。无相机 Run 在包含正式 Record/Replay 分发入口的完整隔离路径下，仍因 Isaac Lab provider 精确版本不符而在 `runtime.prepare` 失败。路径不完整时出现的 Record 入口错误是诊断设置问题，不是独立的上游阻碍。
