#!/usr/bin/env bash
set -euo pipefail
SYSROOT="/home/dev/.local/sysroot"
if [[ -n "${BLENDER_BIN:-}" ]]; then
  BIN="$BLENDER_BIN"
elif [[ -x "$SYSROOT/usr/bin/blender" ]]; then
  BIN="$SYSROOT/usr/bin/blender"
  export BLENDER_SYSTEM_SCRIPTS="$SYSROOT/usr/share/blender/scripts"
  export BLENDER_SYSTEM_DATAFILES="$SYSROOT/usr/share/blender/datafiles"
else
  BIN="$(command -v blender || true)"
fi
if [[ -z "${BIN:-}" || ! -x "$BIN" ]]; then
  echo "Blender was not found. Set BLENDER_BIN to the Blender 4.0.2 executable." >&2
  exit 127
fi
export LIBGL_ALWAYS_SOFTWARE="${LIBGL_ALWAYS_SOFTWARE:-1}"
if [[ -z "${DISPLAY:-}" ]] && command -v xvfb-run >/dev/null; then
  exec xvfb-run -a "$BIN" --python-exit-code 1 "$@"
fi
exec "$BIN" --python-exit-code 1 "$@"
