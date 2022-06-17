import copier
import typer
import shutil

from alive_progress import alive_bar
from gettext import gettext as _
from git import Repo
from pathlib import Path
from altic.constants import GROUPS, STAGES, TEMPLATES

from altic.prompt import choose, prompt_multiple_values

from altic.utils import get_packager_from_git, launch_in_shell, pack_sources_to_tarball, search_package_in_repo, validate_source
from altic.logging import info, success, warning

from altic.commands import app, app_config


def choose_template():
    template_type = choose(
        "Select type of package you like to build", 
        choices=list(TEMPLATES.keys())
    )
    template_data = TEMPLATES.get(template_type)
    template_dir = Path(__file__).parents[2] / "templates"/ f"{template_type}-template"
    info(f"Chosen template: {template_dir}")
    return template_dir, template_type, template_data


def fill_groups(choice_func):
    groups = GROUPS
    for idx, group in enumerate(groups):
        groups[group] = prompt_multiple_values(
            f"Filling group {group} [{idx + 1} / {len(groups)}]",
            choice_func=choice_func
        )
    return groups


def make_package_template(template_dir, template_data, source, tag, groups):
    template_default_data = {
        'url': source,
        'version': tag,
        'packager': get_packager_from_git(),
        '_groups': groups,
        '_stages': STAGES
    }
    if not template_data:
        template_data = dict()
    package_template = copier.run_auto(
        str(template_dir),
        data=template_default_data,
        user_defaults=template_data,
        overwrite=True
    )
    package_slug = package_template.answers.user.get("package_slug")
    return package_slug


def clone_sources_from_repository(source, package_dir, package_slug, tag, make_tarball: bool = False):
    package_tarball_stem = f"{package_slug}-{tag}.tar"
    with alive_bar(1, title=_("Cloning package sources from {source}...".format(source=source)), bar=None, monitor=False, stats=False) as bar:
        package_repo = Repo.clone_from(
            url=source, 
            to_path=package_dir / package_slug,
            branch=tag,
            recursive=True
        )
        bar()
    info(_("Cloned repo {source} @ {working_dir}".format(source=source, working_dir=package_repo.working_dir)), new_line=True)
    shutil.move(package_dir / package_slug / ".git", package_dir)
    if make_tarball:
        pack_sources_to_tarball(package_dir, package_tarball_stem)
            
    elif Path(source).is_dir():
        if make_tarball:
            pack_sources_to_tarball(Path(source), package_tarball_stem)


def unpack_sources_from_archive(source, package_dir, package_slug):
    raise NotImplemented("Ability to unpack sources from archive will be implemented later")


def init_repository_for_gear(package_dir, package_slug_with_template):
    info(_(f"Initializing repository for package {package_slug_with_template}"))
    new_repo = Repo.init(package_dir)
    gitery_ssh_host = app_config['infrastructure']['ssh_gitery_hostname']
    git_repo_url = f"{gitery_ssh_host}:packages/{package_slug_with_template}.git"
    new_repo.create_remote(gitery_ssh_host, git_repo_url)
    info(_(f"Add remote '{gitery_ssh_host}' to {git_repo_url}. For pushing your repo use: git push {gitery_ssh_host} master"))


@app.command(short_help=_("Make new package from zero"))
def new(
    source: str = typer.Option(..., "--source", "-s", help=_("Sources path"), prompt=_("Specify source path of your new package (it could be directory with sources, path to remote repo and so on)"), callback=validate_source), 
    tag: str = typer.Option(..., "--tag", "-t", help=_("Version of sources"), prompt=_("Specify version of your new package")), 
    fill_groups_interactively: bool = typer.Option(True, help=_("Fill groups in interactive mode"), prompt=_("Should i fill groups (BuildRequires, Requires and so on) in interactive mode?")),
    search_packages: bool = typer.Option(False, help=_("Search specified packages in repository"), prompt=_("Should i check your entered packages for existence in repository?")),
    make_tarball: bool = typer.Option(False, help=_("Make tarball from downloaded repo"), prompt=_("Should i make tarball from downloaded repo?")),
    use_gear: bool = typer.Option(True, help=_("Use GEAR for packaging"), prompt=_("Should i use GEAR for packaging?")),
):
    choice_func = lambda _: True
    if search_packages:
        choice_func = search_package_in_repo
    
    template_dir, template_type, template_data = choose_template()
    
    groups = {}
    if fill_groups_interactively:
        groups = fill_groups(choice_func)
    
    package_slug = make_package_template(template_dir, template_data, source, tag, groups)
    package_slug_with_template = f"{template_type}-{package_slug}"
    package_dir = Path() / package_slug_with_template
    
    launch_in_shell("cleanup_spec", str(package_dir / f"{package_slug_with_template}.spec"))
    
    if any([source.startswith(p) for p in ("https://", "git://", "http://")]):
        clone_sources_from_repository(source, package_dir, package_slug, tag, make_tarball)   
    elif Path(source).is_dir():
        unpack_sources_from_archive(source, package_dir, package_slug)

    if use_gear:
        init_repository_for_gear(package_dir, package_slug_with_template)
    
    success(_('Package "{package_slug}" was successfully created!'.format(package_slug=package_slug_with_template)))
    info(_("Adjust your {package_slug}/{package_slug}.spec file to your requirements and run:".format(package_slug=package_slug_with_template)), end=' ')
    warning("altic build", prefix="", style="italic")
