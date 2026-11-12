from pathlib import Path
from capstone import Cs, CS_ARCH_X86, CS_MODE_64

path = Path("/workspace/program.txt")
values = [int(x.strip()) for x in path.read_text().split(",") if x.strip()]
code = bytes(values)

md = Cs(CS_ARCH_X86, CS_MODE_64)

print("Total bytes:", len(code))
print("Instructions:")

for i, ins in enumerate(md.disasm(code, 0)):
    print(f"{ins.address:04x}: {ins.mnemonic:8} {ins.op_str}")
    if i >= 60:
        break
