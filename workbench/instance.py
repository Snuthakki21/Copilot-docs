"""OS-owned single writer lock, released even when the process terminates."""
import os
from .domain import require, ValidationError

class InstanceLock:
    def __init__(self,root):
        root.mkdir(parents=True,exist_ok=True);state=root/'.migration';require(not state.is_symlink(),'Unsafe state path');state.mkdir(exist_ok=True)
        path=state/'coordinator.lock';require(not path.is_symlink(),'Unsafe lock path');self.file=path.open('a+b')
        try:
            if os.name=='nt':
                import msvcrt
                if path.stat().st_size==0:self.file.write(b'0');self.file.flush()
                self.file.seek(0);msvcrt.locking(self.file.fileno(),msvcrt.LK_NBLCK,1)
            else:
                import fcntl
                fcntl.flock(self.file.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
        except OSError as exc:self.file.close();raise ValidationError('Another workbench owns this workspace; stop it before opening a second writer') from exc
    def close(self):self.file.close()
