import json
from pathlib import Path

root = Path("benchmark")
data = json.loads(
    (root / "ctftiny.json").read_text(encoding="utf-8")
)

names = [
    "rev-checker",
    "rev-baby-mult",
    "cry-babycrypto",
    "msc-algebra",
    "for-whyos",
    "web-poem-collection",
]

for name in names:
    print("\n" + "=" * 55)
    print("Challenge:", name)

    info = data[name]
    path = root / info["path"]

    print("Category:", info["category"])
    print("Directory:", path)
    print("Exists:", path.is_dir())

    if path.is_dir():
        for item in sorted(path.iterdir()):
            print("  [DIR] " if item.is_dir() else "  [FILE]", item.name)
