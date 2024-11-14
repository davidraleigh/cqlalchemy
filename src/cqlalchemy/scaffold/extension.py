from typing import List

from pyscaffold import structure
from pyscaffold.actions import Action
from pyscaffold.extensions import Extension
from pyscaffold.operations import no_overwrite
from pyscaffold.templates import get_template

from cqlalchemy.scaffold import templates


class CQLAlchemyExtension(Extension):
    """
    This is a custom extension for PyScaffold that adds support for CQLAlchemy.
    """
    def augment_cli(self, parser):
        parser.add_argument(
            '--ignored-stac-fields-file',
            help='File with list of STAC item fields to not make accessible in query interface.',
            required=False
        )
        parser.add_argument(
            '--ignored-stac-fields',
            help='List of STAC item fields to not make accessible in query interface.',
            nargs='+',  # This allows multiple inputs
            required=False
        )
        parser.add_argument(
            '--extension-url-file',
            help='File with a list of STAC extension urls to be queried and parsed.',
            required=False
        )
        parser.add_argument(
            '--local-extension-files',
            help='Path(s) to the local STAC extension files to be parsed',
            nargs='+',  # This allows multiple inputs
            required=False
        )
        parser.add_argument(
            '--internal-stac-extensions',
            help='json-ld strings for internal STAC extensions',
            nargs='+',  # This allows multiple inputs
            required=False
        )

    def activate(self, actions: List[Action]) -> List[Action]:
        actions = self.register(actions, self.add_files)
        return actions

    def add_files(self, struct, opts):
        pyproject_toml_template = get_template("pyproject.toml", relative_to=templates.__name__)
        files = {
            "pyproject.toml": (pyproject_toml_template, no_overwrite())
        }

        return structure.merge(struct, files), opts
