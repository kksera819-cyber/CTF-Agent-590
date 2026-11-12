"""Restricted Docker Python executor for CTFTiny development experiments.

Only mounts the contestant workspace. Never mounts benchmark or Docker socket.
Docker is a useful isolation boundary, not a guarantee against hostile code.
"""
from pathlib import Path
import subprocess

IMAGE = 'python:3.11-slim'
MAX_CODE_BYTES = 12000


def run_python(code: str, workspace: str = 'agent-workspace', timeout: int = 15) -> dict:
    root = Path(workspace).resolve(strict=True)
    if not root.is_dir():
        raise ValueError('Workspace must be a directory')
    if not isinstance(code, str) or len(code.encode('utf-8')) > MAX_CODE_BYTES:
        raise ValueError('Invalid or oversized Python program')
    timeout = max(1, min(int(timeout), 20))
    cmd = [
        'docker', 'run', '--rm', '--network', 'none', '--read-only',
        '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges',
        '--pids-limit', '64', '--memory', '256m', '--cpus', '1',
        '--user', '65534:65534', '--tmpfs', '/tmp:rw,noexec,nosuid,size=16m',
        '--mount', f'type=bind,source={root},target=/workspace,readonly',
        '--workdir', '/workspace', '--env', 'PYTHONDONTWRITEBYTECODE=1',
        '--env', 'PYTHONUNBUFFERED=1', IMAGE,
        'python', '-I', '-B', '-c', code,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True,
                                timeout=timeout + 5, check=False)
        return {
            'exit_code': result.returncode,
            'stdout': result.stdout[:8000],
            'stderr': result.stderr[:4000],
            'timed_out': False,
        }
    except subprocess.TimeoutExpired:
        return {'exit_code': None, 'stdout': '', 'stderr': 'Execution timed out', 'timed_out': True}
