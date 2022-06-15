from typing import Optional
import typer

from gettext import gettext as _

from altic.commands import app
from altic.logging import info
from altic.utils import launch_hasher


@app.command(short_help="Building package inside hasher", context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def build(context: typer.Context, sandbox: Optional[str] = typer.Option("default")):
    """
    Building package inside hasher for specified architecture

    Args:
        sandbox (str): selected sandbox for build
    """
    args = context.args
    info(_(f"Building package in {sandbox} sandbox ...\n"), prefix="✨")
    launch_hasher(sandbox=sandbox, *args)
