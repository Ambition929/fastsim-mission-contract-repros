# 直接 FastSim GPU 复现

## 输入与边界

`repro/` 是从已实际执行的诊断配置中抽出的 YAML，采用 FastSim 正式 `fastsim/2` schema。仓库没有上传约 2.8 GB 的资产/运行时交接包。GPU 复现需要数据准备方提供 `portable_delivery`，并放到本仓库的 `input/portable_delivery/`；包内应有 `workspace/fastsim_success_1e/` 与 `workspace/real_aligned_station_tasks/`。标准源场景来自固定 SVN r63，非标准任务侧薄 USD 和组件清单随该包提供。请用包内 `verify_inventory.py` 校验 SHA；没有这个包时，先运行不依赖资产的 `scripts/probe_contracts.py`，不要声称完成 GPU 复现。

还需要可工作的 `conda` 环境 `isaac6`、IsaacLab 源码和 GPU。把 `ISAACLAB_ROOT` 指向接收机器自己的 IsaacLab 源码根目录；下面没有本机固定路径。用户要求按 FastSim 原样以 60/60 Hz、`accurate` 运行，命令直接调用 `fastsim run`。

## 固定新版主分支源码

从本仓库根目录执行：

```bash
mkdir -p deps
git clone --branch main git@github.com:FastSim-Benchmark/FastSim.git deps/FastSim
git -C deps/FastSim checkout cef24ab537929b7974d1c241569acaa1fa72b46b
git clone --branch main git@github.com:FastSim-Benchmark/FastSim-Plugins.git deps/FastSim-Plugins
git -C deps/FastSim-Plugins checkout cc4d86b
git clone --branch main git@github.com:FastSim-Benchmark/curobo.git deps/curobo
git -C deps/curobo checkout c179b80

export REPRO_ROOT="$PWD"
export WORKSPACE="$REPRO_ROOT/input/portable_delivery/workspace/fastsim_success_1e"
export ISAACLAB_ROOT="${ISAACLAB_ROOT:?Set this to your IsaacLab source checkout}"
export PYTHONPATH="$REPRO_ROOT/deps/FastSim/src:$REPRO_ROOT/deps/FastSim-Plugins/packages/fastsim-plugin-mission/src:$REPRO_ROOT/deps/curobo:$WORKSPACE/production_runtime:$ISAACLAB_ROOT/source/isaaclab:$ISAACLAB_ROOT/source/isaaclab_physx:$ISAACLAB_ROOT/source/isaaclab_visualizers"
export FASTSIM_ASSETS_CACHE="$WORKSPACE/production_prep/op3_validation/cache"
export DISPLAY="${DISPLAY:-:1}"
mkdir -p "$REPRO_ROOT/outputs"
cp "$REPRO_ROOT/repro/grasp_target_present.yaml" "$WORKSPACE/production_prep/move_box_migration/repro_grasp_target_present.yaml"
cp "$REPRO_ROOT/repro/grasp_target_moved.yaml" "$WORKSPACE/production_prep/move_box_migration/repro_grasp_target_moved.yaml"
cp "$REPRO_ROOT/repro/grasp_start_contact_lift.yaml" "$WORKSPACE/production_prep/move_box_migration/repro_grasp_start_contact_lift.yaml"
cp "$REPRO_ROOT/repro/frame_world_metric.yaml" "$WORKSPACE/production_prep/op3_validation/repro_frame_world_metric.yaml"
cd "$WORKSPACE"
```

FastSim 主程序在交接包的 `production_runtime` 中固定于 `cef24ab537929b7974d1c241569acaa1fa72b46b`；IsaacLab 后端固定于 `717fef6ccb39e7ec0e403cc791b9f39d77502445`。运行前确认这些版本及 `PYTHONPATH` 导入来源；若接收机使用别的运行时版本，结果应单独记录，不能和本次固定版本混写。

## 两组直接命令

抓取：先解析，然后依次跑“目标在抓取位”和“目标移到同桌其他位置”的对照。固定 seed `20260922`。第二个配置的机械臂仍去原抓取位，所以它仅用于隔离障碍条件，不是抓取成功样本。

```bash
conda run -n isaac6 fastsim config validate production_prep/move_box_migration/repro_grasp_target_present.yaml --project production_prep/op3_validation/.fastsim/move_box_project.yaml --json
conda run -n isaac6 --no-capture-output fastsim run production_prep/move_box_migration/repro_grasp_target_present.yaml --asset-library production_prep/op3_validation --project production_prep/op3_validation/.fastsim/move_box_project.yaml --duration 300 --timeout 600 --output-root "$REPRO_ROOT/outputs/grasp_target_present" --json
conda run -n isaac6 --no-capture-output fastsim run production_prep/move_box_migration/repro_grasp_target_moved.yaml --asset-library production_prep/op3_validation --project production_prep/op3_validation/.fastsim/move_box_project.yaml --duration 300 --timeout 600 --output-root "$REPRO_ROOT/outputs/grasp_target_moved" --json
```

帧评价：固定 seed `20260924`。此配置用于复现评价读取错误，且仍包含旧水果诊断资产和抓取流程；它不是新场景的完整水果任务验收。

```bash
conda run -n isaac6 fastsim config validate production_prep/op3_validation/repro_frame_world_metric.yaml --project production_prep/op3_validation/.fastsim/scene_cleared_project.yaml --json
conda run -n isaac6 --no-capture-output fastsim run production_prep/op3_validation/repro_frame_world_metric.yaml --asset-library production_prep/op3_validation --project production_prep/op3_validation/.fastsim/scene_cleared_project.yaml --duration 120 --timeout 300 --output-root "$REPRO_ROOT/outputs/frame_world_metric" --json
```

预期基线：抓取目标在场时完整闭指 `plan_status=infeasible`；移箱后相同完整闭指可执行而目标箱最大抬升 0 m。帧评价在 `settle` 或之后返回 `metric requires an explicitly world-framed pose`。若结果变化，保留 FastSim JSON、FSR、代码提交与 GPU/驱动信息，并分别判断规划、控制、实际位移和指标评价。不能把 `config validate` 的 `ok=true` 当作任务成功。
