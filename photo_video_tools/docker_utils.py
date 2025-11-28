"""Utility functions for Docker container management."""

from pathlib import Path
import subprocess
import shlex
from typing import Iterable


# Container registry: maps container name to its config
CONTAINERS = {
    "exiftool": {
        "image": "base-exiftool",
        "directory": "exiftool",
        "extra_hash_files": [],
    },
    "exiftool-nodejs": {
        "image": "base-exiftool-nodejs",
        "directory": "exiftool-nodejs",
        "extra_hash_files": [
            "DJI_SRT_Parser/package.json",
            "DJI_SRT_Parser/package-lock.json",
            "DJI_SRT_Parser/index.js",
        ],
    },
    "ffmpeg": {
        "image": "base-ffmpeg",
        "directory": "ffmpeg",
        "extra_hash_files": [],
    },
}

CONTAINERS_DIR = Path(__file__).parent / "containers"


def ensure_docker_available() -> None:
    proc = subprocess.run([
        "docker",
        "version",
        "--format",
        "{{.Server.Version}}",
    ], capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError("Docker is not available.")


def _compute_hash(paths: Iterable[Path]) -> str:
    import hashlib
    sha = hashlib.sha256()
    for p in paths:
        if p.exists():
            sha.update(p.read_bytes())
        else:
            sha.update(f"missing:{p}".encode())
    return sha.hexdigest()


def ensure_base_image(image_tag: str, dockerfile_dir: Path, extra_hash_files: Iterable[Path] | None = None) -> None:
    """
    Ensure a base image exists and is up to date based on a source hash.

    Hash includes the Dockerfile and any provided extra files (e.g., parser sources).
    """
    dockerfile = dockerfile_dir / "Dockerfile"
    files = [dockerfile]
    if extra_hash_files:
        files.extend(extra_hash_files)

    wanted_hash = _compute_hash(files)

    inspect = subprocess.run([
        "docker", "image", "inspect", image_tag, "--format",
        "{{ index .Config.Labels \"source_hash\"}}"
    ], capture_output=True, text=True)
    existing_hash = inspect.stdout.strip() if inspect.returncode == 0 else ""
    if existing_hash == wanted_hash:
        print(f"Docker image '{image_tag}' is up to date (source_hash={wanted_hash}). Skipping build.")
        return

    print(f"Building Docker image '{image_tag}' (source_hash={wanted_hash})...")
    build = subprocess.run([
        "docker", "build",
        "--label", f"source_hash={wanted_hash}",
        "-t", image_tag,
        str(dockerfile_dir),
    ], capture_output=True, text=True)
    if build.returncode == 0:
        print(f"Successfully built Docker image '{image_tag}'.")
    else:
        print(f"Failed to build Docker image '{image_tag}'.")
        print("Build output:")
        print(build.stdout)
        print("Build errors:")
        print(build.stderr)
        raise RuntimeError(f"Failed to build Docker image '{image_tag}'.")


def run_container(container_name: str, docker_options: list[str], command_and_args: list[str]) -> int:
    """
    Preflight and run a container by name.

    Args:
        container_name: Name identifying the container
        docker_options: List of docker run options (e.g., ["-v", "...", "--rm"])
        command_and_args: List of command and arguments to run inside the container (e.g., ["python", "script.py"])

    Returns:
        Exit code from the container process
    """
    if container_name not in CONTAINERS:
        raise ValueError(f"Unknown container: {container_name}. Valid containers: {list(CONTAINERS.keys())}")

    config = CONTAINERS[container_name]
    dockerfile_dir = CONTAINERS_DIR / config["directory"]

    # Build extra hash files as Path objects
    extra_files = [dockerfile_dir  / p for p in config["extra_hash_files"]] if config["extra_hash_files"] else None

    # Ensure Docker is available and the base image is up to date
    ensure_docker_available()
    ensure_base_image(config["image"], dockerfile_dir, extra_files)

    # Build docker run command: docker run [OPTIONS] IMAGE [COMMAND [ARG...]]
    cmd = ["docker", "run"] + docker_options + [config["image"]] + command_and_args
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result.returncode
