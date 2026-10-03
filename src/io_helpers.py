from pathlib import Path
import shutil,os,tempfile

def atomic_copy(source,dest):
    dest=Path(dest);dest.parent.mkdir(parents=True,exist_ok=True)
    fd,name=tempfile.mkstemp(prefix='.publishing-',dir=dest.parent);os.close(fd)
    try:
        shutil.copyfile(source,name);os.chmod(name,0o644);os.replace(name,dest)
    finally:
        if os.path.exists(name):os.unlink(name)
