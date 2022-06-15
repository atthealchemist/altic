import copier
import typer

from alive_progress import alive_bar
from gettext import gettext as _
from git import Repo
from pathlib import Path

from altic.prompt import choose, prompt_multiple_values

from altic.utils import launch_in_shell, pack_sources_to_tarball, search_package_in_repo, validate_source
from altic.logging import info, success

from altic.commands import app, app_config


@app.command(short_help=_("Make new package from zero"))
def new(
    source: str = typer.Option(..., "--source", "-s", help=_("Sources path"), prompt=_("Specify source path of your new package"), callback=validate_source), 
    tag: str = typer.Option(..., "--tag", "-t", help=_("Version of sources"), prompt=_("Specify version of your new package")), 
    search_packages: bool = typer.Option(False, help=_("Search specified packages in repository"), prompt=_("Should i check your entered packages for existence in repository?"))
):
    choice_func = lambda _: True
    if search_packages:
        choice_func = search_package_in_repo
    
    template_type = choose(
        "Select type of package you like to build", 
        choices=(
            'python3-module',
            'rust',
            'other'
        )
    )
    
    groups = {
        "BuildRequires(pre)": [],
        "BuildRequires": [],
        "Requires(pre)": [],
        "Provides": [],
        "Conflicts": [],
        "Obsoletes": []
    }
    
    _stages = [
        "prep",
        "setup",
        "build",
        "install",
        "files"
    ]

    for idx, group in enumerate(groups):
        groups[group] = prompt_multiple_values(f"Filling group {group} [{idx + 1} / {len(groups)}]", choice_func=choice_func)
    
    template_dir = Path(__file__).parent.parent / "templates"/ f"{template_type}-template"
    info(f"Choosen template: {template_dir}")
    package_template = copier.run_auto(
        str(template_dir),
        data={
            'url': source,
            'version': tag,
            '_groups': groups,
            '_stages': _stages
        }
    )
    package_slug = package_template.answers.user.get("package_slug")
    package_dir = Path() / package_slug
    
    launch_in_shell("cleanup_spec", str(package_dir / f"{package_slug}.spec"))
    
    if any([source.startswith(p) for p in ("https://", "git://", "http://")]):
        package_tarball_stem = f"{package_dir.stem}-{tag}"
        with alive_bar(1, title=_("Cloning package sources from {source}...".format(source=source)), bar=None, monitor=False, stats=False) as bar:
            package_repo = Repo.clone_from(
                url=source, 
                to_path=package_dir / f"{package_dir.stem}-src",
                branch=tag,
                recursive=True
            )
            bar()
        info(_("Cloned repo {source} @ {working_dir}".format(source=source, working_dir=package_repo.working_dir)), new_line=True)
        pack_sources_to_tarball(package_dir, f"{package_tarball_stem}.tar.gz")
            
    elif Path(source).is_dir():
        pack_sources_to_tarball(Path(source), f"{package_slug}.tar.gz")

    
    success(_('Package "{package_slug}" was successfully created!'.format(package_slug=package_slug)))
    info(_("Adjust your {package_slug}/{package_slug}.spec file to your requirements and run:".format(package_slug=package_slug)), end=' ')
    info("altic build", prefix="", style="italic")
