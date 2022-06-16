from gettext import gettext as _

from altic.utils import launch_gitery
from altic.logging import info, success
from altic.commands import app, app_config


@app.command(short_help=_("Deploy built package to git.alt"))
def deploy(repository_name: str, commit_message: str = "Initial commit for Sisyphus"):
    """
    Deploy built package to git.alt

    Args:
        repository_name (str): name of repo with package
        commit_message (str): commit message of deployed package
    """
    gitery_ssh_host = app_config['infrastructure']['ssh_gitery_hostname']
    git_repo_url = f"{gitery_ssh_host}:packages/{repository_name}.git"
    info(_(f"Initializing new gitery repo @ {git_repo_url} ...\n"), prefix="♦")
    launch_gitery('init-db', repository_name)
    info(_("Created new repository @ git.alt:packages/{repository_name}".format(repository_name=repository_name)))
    
    success(f"Push your package to {git_repo_url} via: git push --force {gitery_ssh_host} master && git push --tags {gitery_ssh_host} master")
