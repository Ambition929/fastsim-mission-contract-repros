# 两个独立问题

## 1. 目标物接触没有进入原生 CuRobo 抓取规划契约

### 最小现象

使用完整高度 G2 + 双 OP3 E、scene005 清桌、原始纸箱、60 Hz 物理/控制和 `accurate` 物理，固定 seed `20260922`：

1. `repro/grasp_target_present.yaml`：左箱在 `[5.55, 4.05, 0.735] m`。前 3 段原生 CuRobo 动作执行；第 4 段完整 13 关节闭指规划返回 `mission.curobo.plan.failed`、`plan_status=infeasible`。碰撞世界中包含 `objects.box_left`；禁用的碰撞 ID 数为 0。
2. `repro/grasp_target_moved.yaml`：只把左箱移至同一桌面的 `[5.55, 4.35, 0.735] m`，机器人、闭指目标和轨迹不变。5 段原生 CuRobo 动作完成，365 帧控制应用，末帧左指 `joint14≈0.398 rad`。目标箱不在抓取点，最大抬升 0 m，**这不是成功抓取**。
3. 官方 `type: grasp` 物理闭指在另一诊断中可以执行，但原箱指端与箱体 AABB 仍留约 4.10/4.48 mm 空隙；试抬起点检测到 6.421 mm 穿透，超过默认 2 mm。将公开 `JointMotion.max_initial_penetration` 调到 10 mm 后，试抬仍 `infeasible`，原箱最大抬升约 2.325 µm。`repro/grasp_start_contact_lift.yaml` 保留这一对照。

第 1/2 项说明目标物位姿改变会改变可行性；第 3 项说明放宽起点容限或换成物理关指命令，也没有证明真实夹持。不能据此断言所有任务侧物体尺寸/姿态都不可能成功，但已试的组合没有产出可生产配置。

### 已定位的契约

`FastSim-Plugins/packages/fastsim-plugin-mission/src/fastsim_plugin_mission/plugin.py::_grasp_collision_policy` 检查目标物在捕获世界中恰有一个对象且有几何 ID，但返回空 `CollisionPolicy()`；目标物仍是整段路径障碍。关节目标规划目前不能按目标物 ID、OP3 E 指端链路、阶段和容限声明预期终点接触。现有 `JointMotion` 的边界碰撞只可用 `none/start`；`PoseMotion` 的 `end` 并没有使上述接触动作可行。

### 最小修复与验收

由接口所有者在有授权的源仓库设计请求级接触契约：明确目标物稳定 ID、允许接触的指端链路、终点阶段、几何容限及同一捕获世界 revision；它必须传到 Mission 请求和 CuRobo 接受条件。路径中途穿箱、掌部/桌面/其他物体碰撞、错误或过期目标 ID 均拒绝。不得禁用整个目标物碰撞。后续携物试抬必须用真实 PhysX 接触与对象位移验收，并独立报告规划、控制、物理抬升、释放和 Mission 评价。

## 2. SceneQuery 世界帧与 Mission 评价的标识不一致

### 最小现象

`repro/frame_world_metric.yaml` 在 `settle` 用 `linear_speed` 评价苹果速度，后面用 `position_error` 检查抬升。配置解析通过；已有直接 FastSim GPU 运行返回 `ok=false`，错误 `metric requires an explicitly world-framed pose`。该错误发生在评价读取阶段，不能解释为速度不达标或抓取成功/失败。

后端规划世界帧是 `frame.world`；FastSim 公开 `scene.query` 保留该 frame ID。Mission 的 `evaluation/engine.py::_pose` 主分支只接受 `PoseFact.frame_id == "world"`；`evaluation_scene.py` 把 scene.query 的位姿帧原样交给引擎，而且没有检查 twist 的表达帧与 pose 一致。

### 最小修复与验收

应在 SceneQuery → EvaluationSnapshot 的正式边界用 `frame.query` 的唯一 `FrameKind.WORLD` 和一致的 `run_id`、`generation`、目录 revision/摘要确认世界帧，再对 pose 与 twist 一起归一化或传递可证明语义。单纯把 `{"world", "frame.world"}` 都当作世界帧只修复某一后端的字符串症状，不能证明伪造、未知或错代帧安全。

正例：目录声明 `frame.world` 为 WORLD，pose/twist 同帧、同代，速度/位置/姿态指标均返回 valid 和正确 SI 值；旧 `world` 用例在目录声明其为 WORLD 时继续通过。反例：局部/未知帧、pose/twist 异帧、伪造 `world`、目录过期或跨 generation 都必须 unavailable/invalid，不产出成功分数。最后以直接 FastSim GPU 复跑确认错误消失，并分别报告评价可用、指标通过和物理任务完成。

## 关系与放行条件

两个问题的修复均需由 FastSim 公共接口/插件所有者完成；本仓库只存复现。只修复帧评价不意味着箱子可抓；只修复接触规划不意味着 Mission 可以评价。需要至少一个完整任务在真实物理、原生 CuRobo、60/60 Hz `accurate` 下成功，再生成 1000 个生产配置。
