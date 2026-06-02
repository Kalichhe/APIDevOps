import pathlib
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "app.zip"

INCLUDE_FILES = [
    "Procfile",
    "requirements.txt",
    "Dockerfile",
]

INCLUDE_DIRS = [
    "app",
]


def iter_files(base_dir: pathlib.Path):
    for path in base_dir.rglob("*"):
        if path.is_file():
            yield path


def to_posix_relative(path: pathlib.Path) -> str:
    return path.relative_to(ROOT).as_posix()


with zipfile.ZipFile(OUTPUT, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
    for rel_file in INCLUDE_FILES:
        file_path = ROOT / rel_file
        if file_path.exists() and file_path.is_file():
            zf.write(file_path, arcname=to_posix_relative(file_path))

    for rel_dir in INCLUDE_DIRS:
        dir_path = ROOT / rel_dir
        if dir_path.exists() and dir_path.is_dir():
            for file_path in iter_files(dir_path):
                zf.write(file_path, arcname=to_posix_relative(file_path))

print(f"Created {OUTPUT}")
