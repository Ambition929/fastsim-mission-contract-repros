# 当前主分支运行时版本不闭合（2026-09-28）

FastSim-Benchmark/FastSim 主分支 `5b8520b26f` 的 `pyproject.toml` 指定 `unirobosim==0.10.9`；其 `integrations/unirobosim/projection.py` 读取 `CameraSpec.render_exclusions`，`aliases.py` 又把 Isaac Lab provider 精确固定为 `0.10.24`。可取得的 GitHofee/UniRoboSim 主分支 `12f7a9350b` 版本是 `0.10.8`，`CameraSpec` 没有该字段；GitHofee/UniRoboSim-isaaclab 主分支 `717fef6ccb` 版本是 `0.10.22`。这些是源码仓库的默认分支版本，不能冒充 FastSim 锁定的版本。

## 无资产复现

在本仓库根目录、已有 `isaac6` 环境中：

```bash
mkdir -p deps
git clone --branch main git@github.com:FastSim-Benchmark/FastSim.git deps/FastSim
git clone --branch main git@github.com:GitHofee/UniRoboSim.git deps/UniRoboSim
PYTHONPATH="$PWD/deps/FastSim/src:$PWD/deps/UniRoboSim/src" \
  conda run -n isaac6 python scripts/probe_runtime_versions.py
```

输出中的 `camera_spec_has_render_exclusions` 为 `false`，`required_isaaclab_provider_version` 为 `0.10.24`；安装版本与之不符时 `isaaclab_provider_version_match` 为 `false`。可用以下单行复现相机接口缺口：

```bash
PYTHONPATH="$PWD/deps/UniRoboSim/src" \
  conda run -n isaac6 python -c 'from unirobosim.api import CameraSpec; print(CameraSpec().render_exclusions)'
```

该调用报 `AttributeError`。这只是公共接口复现，不表示任何仿真任务实际运行或失败。

## GPU 运行时观察与边界

一份原先完整成功的四水果三相机任务，在新 FastSim 主分支、官方 Mission 0.1.23 及旧 UniRoboSim 0.10.5 下通过 `fastsim config validate` 和 Mission 编译，但直接 `fastsim run` 于 `application open_plan` 报 `CameraSpec` 缺少 `render_exclusions`。从诊断配置移除相机后，若提供官方插件正确的 `fastsim.plugins` distribution/entry point，执行进入 `runtime.prepare` 并因 Isaac backend 精确版本不符而报 `entry-point value/distribution/version differs from frozen alias metadata`。这两步都是**仿真启动前失败**，不能当作 CuRobo、抓取或相机采集的任务执行结果。

本公开仓库不包含用户的任务资产和 FSR，因此 GPU 配置/日志不在此复现包中；接口所有者可以先用无资产探针确认版本契约，再在其授权的标准资产环境跑含相机的最小 `fastsim run`。

## 所有者应完成的最小修复

1. 提供与 FastSim 当前主分支匹配且可固定来源的 UniRoboSim 0.10.9，包含 `CameraSpec.render_exclusions` 和对应公共 API 测试；或者把 FastSim 主分支的相机读取及版本约束收敛到已发布版本。
2. 提供精确 version/entry point 为 0.10.24 的 UniRoboSim-isaaclab，且真正声明并实现 `sensor.camera.render-exclusions@1`；或者同步修正 FastSim 的 alias 锁。
3. 用 `conda run -n isaac6` 分别验收无资产 API 探针、官方插件入口锁、含三相机的直接 FastSim Run、原 60/60 Hz accurate 物理和封口录像。不得通过改元数据版本号、运行时猴子补丁或关闭相机来冒充生产修复。

参考源码：[FastSim 当前主分支](https://github.com/FastSim-Benchmark/FastSim)、[UniRoboSim](https://github.com/GitHofee/UniRoboSim)、[UniRoboSim-isaaclab](https://github.com/GitHofee/UniRoboSim-isaaclab)。
