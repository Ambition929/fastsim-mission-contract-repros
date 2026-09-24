"""Small, asset-free probes for two FastSim Mission contract gaps.

Run with the FastSim-Plugins source tree on PYTHONPATH. This script does not
patch or mutate FastSim; it reports observed behavior rather than claiming that
a geometry-free probe establishes physical grasp success or failure.
"""

from __future__ import annotations

import json
from types import SimpleNamespace

from fastsim_plugin_mission.evaluation import (
    EvaluationProgram,
    EvaluationSnapshot,
    EvidenceStamp,
    PoseFact,
    evaluate_metric,
)
from fastsim_plugin_mission.plugin import MissionPlugin


def frame_probe(frame_id: str) -> dict[str, object]:
    program = EvaluationProgram.from_document(
        {
            "schema": "mission-evaluation/1",
            "metrics": {
                "speed": {
                    "kind": "linear_speed",
                    "entity_id": "objects.target",
                    "tolerance": 0.05,
                }
            },
            "aggregate": {"weights": {}, "require_pass": ["speed"], "missing": "error"},
        }
    )
    snapshot = EvaluationSnapshot(
        EvidenceStamp("probe", 1, 1, 1 / 60, 1, 1, 1, "0" * 64, 1, 1),
        ("objects.target",),
        (),
        (PoseFact("objects.target", None, frame_id, (0.0, 0.0, 0.8),
                  (0.0, 0.0, 0.0, 1.0), (0.0, 0.0, 0.0)),),
        (),
        (),
    )
    result = evaluate_metric(program, "speed", snapshot)
    return {
        "input_frame_id": frame_id,
        "validity": result.validity,
        "error_code": None if result.error is None else result.error.code,
        "value_m_s": result.value,
        "passed": result.passed,
    }


def contact_policy_probe() -> dict[str, object]:
    collision = SimpleNamespace(collision_id="target/body")
    target = SimpleNamespace(
        object_id="objects.target",
        links=(SimpleNamespace(collisions=(collision,)),),
    )
    projection = SimpleNamespace(collision_world=SimpleNamespace(objects=(target,)))
    policy = MissionPlugin._grasp_collision_policy(projection, "objects.target")
    return {
        "target_object_id": "objects.target",
        "target_collision_id": collision.collision_id,
        "disabled_collision_ids": sorted(policy.disabled_collision_ids),
        "policy_type": type(policy).__name__,
    }


if __name__ == "__main__":
    print(json.dumps({
        "frame": [frame_probe("world"), frame_probe("frame.world")],
        "grasp_collision_policy": contact_policy_probe(),
    }, ensure_ascii=False, indent=2, sort_keys=True))
