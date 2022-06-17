import shutil
import subprocess
import tarfile
import typer
import yaml

from git import Repo
from getpass import getpass
from pathlib import Path

from altic.logging import error, info, success, log, warning

RPM_LIB_DIR = Path("/usr/lib/rpm")


def validate_source(context, param, value):
    if not any([
        any([value.startswith(p) for p in ("https://", "git://", "http://")]),
        any([Path(value).is_dir(), Path(value).is_file()])
    ]):
        raise typer.BadParameter(f'"{value}" should be path to existing directory or file, or really working url link.')
    return value


def sudo_launch_in_shell(cmd, *args, **kwargs):
    kwargs['password'] = getpass(prompt="Enter root password: ")
    launch_in_shell("sudo", "-S", cmd, *args, **kwargs)


def load_config():
    config_path = Path(__file__).parent.parent / "config.yml"
    with open(config_path, "r") as config_file:
        try:
            return yaml.safe_load(config_file)
        except yaml.YAMLError as exc:
            error(exc)


def fetch_application_groups():
    group_file_path = RPM_LIB_DIR / "GROUPS"
    return group_file_path.read_text(encoding="utf8").split("\n")


def fetch_application_licenses():
    licenses_path = Path("/usr/share") / "license"
    return {
        directory.name
        for directory in licenses_path.glob("**/*")
    }


def fetch_architectures():
    platform_path = RPM_LIB_DIR / "platform"
    return {
        directory.name.split('-')[0] 
        for directory in platform_path.glob("**/")
    }


def launch_in_shell(cmd: str, *args, **params):    
    has_errors = False
    password = ""
    if "password" in params:
        password = params.pop("password")

    kwargs = [
        f"--{k}=\"{v}\"" if not isinstance(v, bool) else f"--{k}"
        for k, v in params.items()
    ]
    command = " ".join([cmd, *args, *kwargs])

    if password:
        log(f"Running command as sudoer: {command}", prefix="♝")
    else:
        log(f"Running command as user: {command}", prefix="♟")
    
    process_input = {}
    if password:
        process_input = {'stdin': subprocess.PIPE, 'input': password.encode()}
        
    process = subprocess.Popen(
        [cmd, *args, *kwargs],
        **process_input,
        stderr=subprocess.STDOUT,
        stdout=subprocess.PIPE,
        text=True
    )

    while True:
        out = process.stdout.readline()
        if not out: 
            break
        if "err" in out:
            error(out.capitalize(), prefix="")
        info(out.capitalize(), prefix="")

    success("Completed!") if not has_errors else error("Failed!")
    return not has_errors

def get_sandbox_config(sandbox_name: str):
    app_config = load_config()
    sandbox_config = app_config.get("sandboxes").get(sandbox_name)
    if not sandbox_config:
        error(f"Sandbox with name '{sandbox_name}' not found in config.yml!")
    return sandbox_config


def launch_hasher(*args, command: str = "hsh", sandbox: str = "default", with_gear: bool = True, **kwargs):
    cmd = [command]
    sandbox_config = get_sandbox_config(sandbox)
    if sandbox_config['build']['gear'] is True and with_gear:
        cmd = ['gear', '--hasher', '--', *cmd]
    return launch_in_shell(
        *cmd,
        *args,
        **kwargs
    )


def launch_gitery(*args, **kwargs):
    app_config = load_config()
    gitery_ssh_host = app_config['infrastructure']['ssh_gitery_hostname']
    return launch_in_shell("ssh", gitery_ssh_host, *args, **kwargs)


def pack_sources_to_tarball(
    source_dir, 
    result_file_path, 
    compress='gz',
    rm_source_dir=False
):    
    with tarfile.open(
        f"{source_dir}/{result_file_path}", 
        f"w{f':{compress}' if compress else ''}"
    ) as tar:
        tar.add(source_dir, recursive=True)
        success(f"Creating sources tarball @ {result_file_path}")
        if rm_source_dir:
            shutil.rmtree(source_dir)


def search_package_in_repo(package_name):
    res = launch_gitery("find-package", f"*{package_name}*")
    if not res:
        warning(f"Package '{package_name}' does not exists in repo!")
        return False
    return True


def get_packager_from_git():
    reader = Repo.init().config_reader()
    name = reader.get_value("user", "name")
    email = reader.get_value("user", "email")
    return f"{name} <{email}>"
