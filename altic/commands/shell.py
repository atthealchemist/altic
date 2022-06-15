import os

from gettext import gettext as _

import typer

from altic.logging import info
from altic.commands import app


@app.command(short_help=_("Running a new hasher shell"), context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def shell(context: typer.Context):
    """
    Running a new hasher shell
    """
    args = context.args
    info(_("Starting hasher shell ...\n"), prefix="♦")
    os.system(" ".join(["hsh-shell", *args]))
    info(_("Exiting hasher shell ...\n"), prefix="♦")
