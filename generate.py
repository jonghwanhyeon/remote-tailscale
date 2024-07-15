import argparse
import getpass
import math
import os
import platform
import pwd
import re
import shlex
import shutil
import subprocess
from pathlib import Path
from typing import Optional

project_path = Path(__file__).parent.absolute()
template_path = project_path / "docker-compose.yaml.template"
output_path = project_path / "docker-compose.yaml"


def command(expression: str) -> str:
    arguments = shlex.split(expression)
    completed = subprocess.run(arguments, capture_output=True)
    return completed.stdout.decode().strip()


def get_prefix() -> Optional[str]:
    prefix = platform.node()
    if match := re.match(r"[a-z0-9]+-(.+)", prefix):
        return match.group(1)
    return None


def get_name() -> str:
    gecos = pwd.getpwuid(os.geteuid()).pw_gecos
    return gecos.split(",", maxsplit=1)[0]


def get_shm_size() -> int:
    if platform.system() == "Linux":
        usage = shutil.disk_usage("/dev/shm")
        return math.ceil(usage.total / 1024 / 1024 / 1024)
    elif platform.system() == "Darwin":
        output = command("sysctl hw.memsize")
        total = int(output.split(":")[1].strip())
        return math.ceil(total / 1024 / 1024 / 1024) // 2
    else:
        raise ValueError("Unable to determine shared memory size")


defaults = {
    "registry": "ghcr.io",
    "image": "jonghwanhyeon/ml:cuda11.8-python3.12-torch2.3",
    "uid": str(os.geteuid()),
    "gid": str(os.getegid()),
    "user": str(getpass.getuser()),
    "name": get_name(),
    "email": None,
    "prefix": get_prefix(),
    "project": project_path.name,
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", default=defaults["registry"], help=f"registry (default: {defaults['registry']})")
    parser.add_argument("--image", default=defaults["image"], help=f"image (default: {defaults['image']})")
    parser.add_argument("--uid", default=defaults["uid"], help=f"user id (default: {defaults['uid']})")
    parser.add_argument("--gid", default=defaults["gid"], help=f"group id (default: {defaults['gid']})")
    parser.add_argument("--user", default=defaults["user"], help=f"user login id (default: {defaults['user']})")
    parser.add_argument("--name", default=defaults["name"], help=f"full name (default: {defaults['name']})")
    parser.add_argument("--email", default=defaults["email"], help=f"email for git (default: {defaults['email']})")
    parser.add_argument(
        "--prefix", default=defaults["prefix"], help=f"prefix to container name (default: {defaults['prefix']})"
    )
    parser.add_argument("--project", default=defaults["project"], help=f"project name (default: {defaults['project']})")

    arguments = parser.parse_args()

    container_name = f"{arguments.user}-{arguments.project}"
    if arguments.prefix is not None:
        container_name = f"{arguments.prefix}-{container_name}"

    template = template_path.read_text(encoding="utf-8")
    output_path.write_text(
        template.format(
            project=arguments.project,
            registry=arguments.registry,
            image=arguments.image,
            container_name=container_name,
            container_image=f"{arguments.user}/{arguments.project}",
            user_id=arguments.uid,
            group_id=arguments.gid,
            user=arguments.user,
            name=arguments.name,
            email=arguments.email if arguments.email is not None else "",
            shm_size=get_shm_size(),
        ),
        encoding="utf-8",
    )
    print(f"Wrote docker-compose.yaml for container '{container_name}'")


if __name__ == "__main__":
    main()
