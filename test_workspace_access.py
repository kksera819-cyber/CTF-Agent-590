from docker_python_tool_improved import run_python

code = """
from pathlib import Path

p = Path("program.txt")
print("exists:", p.exists())

if p.exists():
    print("preview:", p.read_text()[:200])
"""

result = run_python(
    code,
    workspace="agent-workspace",
    timeout=15
)

print(result)
