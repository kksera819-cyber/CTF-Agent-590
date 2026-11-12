
from pathlib import Path
import shutil

from nyuctf.dataset import CTFDataset
from nyuctf.challenge import CTFChallenge

BENCHMARK = "benchmark/ctftiny.json"
CHALLENGE_ID = "rev-baby-mult"

dataset = CTFDataset(dataset_json=BENCHMARK)
challenge = CTFChallenge(
    dataset.get(CHALLENGE_ID),
    dataset.basedir
)

workspace = Path("agent-workspace")

if workspace.exists():
    shutil.rmtree(workspace)

workspace.mkdir()

for filename in challenge.files:
    source = (challenge.challenge_dir / filename).resolve()
    relative = source.relative_to(
        challenge.challenge_dir.resolve()
    )

    destination = workspace / relative
    destination.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    shutil.copy2(source, destination)

(workspace / "description.txt").write_text(
    challenge.description,
    encoding="utf-8"
)

print("Challenge:", challenge.name)
print("Category:", challenge.category)
print("Workspace:", workspace.resolve())
print("Contestant files:")

for file in workspace.rglob("*"):
    if file.is_file():
        print(" -", file.name)

print("Workspace setup completed!")
