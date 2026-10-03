"""Resolve source provenance in a Git checkout or an exported project archive."""
from pathlib import Path
import json
import subprocess

def source_commit(root):
    root=Path(root)
    try:
        result=subprocess.run(['git','rev-parse','HEAD'],cwd=root,capture_output=True,text=True,timeout=10)
        if result.returncode==0 and result.stdout.strip():return result.stdout.strip()
    except (OSError,subprocess.TimeoutExpired):pass
    checkpoint=root/'CHECKPOINT.json'
    if checkpoint.exists():
        try:
            data=json.loads(checkpoint.read_text())
            return str(data.get('sourceCommit') or 'unversioned')
        except (OSError,ValueError):pass
    return 'unversioned'
