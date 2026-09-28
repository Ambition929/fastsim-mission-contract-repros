"""Asset-free check of the versions locked by current FastSim main."""
from __future__ import annotations

import json
from dataclasses import fields
from importlib import metadata

from fastsim.integrations.unirobosim.aliases import backend_alias
from unirobosim.api import CameraSpec


def installed(name: str) -> str | None:
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return None


def main() -> None:
    camera_fields = {field.name for field in fields(CameraSpec)}
    required_backend = backend_alias('isaaclab').provider_version
    actual_backend = installed('unirobosim-isaaclab')
    result = {
        'schema': 'fastsim-runtime-version-probe/1',
        'required_isaaclab_provider_version': required_backend,
        'installed_isaaclab_provider_version': actual_backend,
        'isaaclab_provider_version_match': actual_backend == required_backend,
        'installed_unirobosim_version': installed('unirobosim'),
        'camera_spec_fields': sorted(camera_fields),
        'camera_spec_has_render_exclusions': 'render_exclusions' in camera_fields,
        'scope': 'Public API and installed distribution metadata only; no GPU, asset loading, or task success.',
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
