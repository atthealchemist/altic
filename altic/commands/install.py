import typer

from gettext import gettext as _

from altic.commands import app
from altic.logging import info
from altic.utils import launch_hasher


@app.command(short_help="Installing package from hasher to system", context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def install(context: typer.Context):
    args = context.args
    info(_("Installing new package in hasher virtual environment...\n"), prefix="⚛")
    launch_hasher(
        command="hsh-install",
        with_gear=False,
        *args
    )
