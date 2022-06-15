from gettext import gettext as _

import typer


from altic.utils import load_config
from altic.logging import print_logo

print_logo()

app = typer.Typer()

app_config = load_config()

from altic.commands.new import new
from altic.commands.build import build
from altic.commands.rebuild import rebuild
from altic.commands.shell import shell
from altic.commands.install import install
from altic.commands.deploy import deploy
