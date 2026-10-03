#!/usr/bin/env bash
set -euo pipefail
export BLENDER_SYSTEM_SCRIPTS=/home/dev/.local/sysroot/usr/share/blender/scripts
export BLENDER_SYSTEM_DATAFILES=/home/dev/.local/sysroot/usr/share/blender/datafiles
export LIBGL_ALWAYS_SOFTWARE=1
exec xvfb-run -a /home/dev/.local/sysroot/usr/bin/blender "$@"
