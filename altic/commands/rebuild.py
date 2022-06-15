from typing import Optional
import typer

from gettext import gettext as _

from altic.commands import app
from altic.logging import info
from altic.utils import launch_hasher


@app.command(short_help="Rebuilding package inside hasher", context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def rebuild(context: typer.Context, sandbox: Optional[str] = typer.Option("default")):
    args = context.args
    info(_(f"Rebuilding package in {sandbox} sandbox...\n"), prefix="♼", style="bold italic fg:cyan")
    launch_hasher(
        command="hsh-rebuild",
        sandbox=sandbox,
        *args
    )
