"""Process-level mutual exclusion lock to prevent concurrent pipeline runs."""

import fcntl
import os
import sys
from pathlib import Path


class ProcessLock:
    """Prevent multiple instances from running simultaneously via fcntl.flock."""

    def __init__(self, lock_file: str):
        self.lock_file = Path(lock_file)
        self.lock_fd = None

    def __enter__(self):
        self.lock_file.parent.mkdir(parents=True, exist_ok=True)
        self.lock_fd = open(self.lock_file, "w")

        try:
            fcntl.flock(self.lock_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.lock_fd.write(str(os.getpid()))
            self.lock_fd.flush()
        except BlockingIOError:
            print("\nError: Another download process is running")
            print(f"Lock file: {self.lock_file}")
            print("\nIf no other process is running, delete the lock file:")
            print(f"  rm {self.lock_file}")
            sys.exit(1)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.lock_fd:
            try:
                fcntl.flock(self.lock_fd.fileno(), fcntl.LOCK_UN)
                self.lock_fd.close()
            except Exception:
                pass

            try:
                self.lock_file.unlink(missing_ok=True)
            except Exception:
                pass
