# # cqlalchemy/scaffold/extension.py
#
# import argparse
# from pyscaffold.extensions import Extension
# from pyscaffold.api import create_project
#
# class CQLAlchemyExtension(Extension):
#     """
#     This is a custom extension for PyScaffold that adds support for CQLAlchemy.
#
#     This extension provides additional functionality to generate libraries with multiple STAC extensions.
#     """
#
#     def augment_cli(self, parser):
#         parser.add_argument(
#             '--input-files',
#             help='Paths to the input text files to be parsed',
#             nargs='+',  # This allows multiple inputs
#             required=False
#         )
#         parser.add_argument(
#             '--interactive-mode',
#             help='Enable interactive mode',
#             action='store_true'
#         )
#
#     def activate(self, actions):
#         # Add your custom actions here
#         return self.register(actions, add_cqlalchemy, after="define_structure")
#
# def add_cqlalchemy(struct, opts):
#     if opts.get('interactive_mode'):
#         input_files = []
#         while True:
#             input_file = input("Enter the path to an input file (or press Enter to finish): ")
#             if not input_file:
#                 break
#             input_files.append(input_file)
#         opts['input_files'] = input_files
#
#     input_files = opts.get('input_files')
#     if input_files:
#         for input_file in input_files:
#             with open(input_file, 'r') as file:
#                 content = file.read()
#                 # Implement your custom logic to parse the file content
#                 print(f"Parsing content of {input_file}:")
#                 print(content)
#     return struct, opts

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
            '--cqlactive',
            help='Enable interactive mode',
            action='store_true'
        )
        parser.add_argument(
            '--ignored-stac-fields-file',
            help='File with list of STAC item fields to not make accessible in query interface.',
            required=True
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
        return self.register(actions, self.add_files)

    def add_files(self, struct, opts):
        pyproject_toml_template = get_template("pyproject.toml", relative_to=templates.__name__)
        files = {
            "pyproject.toml": (pyproject_toml_template, no_overwrite())
        }

        return structure.merge(struct, files), opts


def add_cqlalchemy(struct, opts):
    if opts.get('cqlactive'):
        input_files = []
        while True:
            input_file = input("Enter the path to an input file (or press Enter to finish): ")
            if not input_file:
                break
            input_files.append(input_file)
        opts['input_files'] = input_files
    return struct, opts
