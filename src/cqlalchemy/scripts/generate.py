import json
import logging
import pathlib
from json import JSONDecodeError

import click
import requests

from cqlalchemy.scaffold.build import build_query_file

logger = logging.getLogger(__name__)


def process_extension(extension, extensions):
    try:
        if not extension.startswith("http"):
            if "/" in extension:
                raise ValueError("path does not exist")
            ext_temp = extension
            extension = f"https://raw.githubusercontent.com/stac-extensions/{extension}/refs/heads/main/json-schema/schema.json"
            logger.warning(f"treating input {ext_temp} like extension json-ld code and querying {extension}")
        else:
            logger.warning(f"treating input {extension} like raw schema http endpoint")
        response = requests.get(extension)
        response.raise_for_status()
        extensions[extension] = response.json()
    except BaseException as be:
        click.echo(f"{extension} failed with '{be}' exception")
    return extensions


def add_extension(extension, extensions):
    if pathlib.Path(extension).exists():
        with pathlib.Path(extension).open() as fp:
            json_type = False
            try:
                extensions[extension] = json.load(fp)
                json_type = True
            except JSONDecodeError as je:
                click.echo(f"file {extension} is not formatted as json. attempting as list of extensions {je}")
            except BaseException as be:
                click.echo(f"file {extension} threw {be}")
        with pathlib.Path(extension).open() as fp:
            if not json_type:
                for line in fp:
                    if not line.strip():
                        continue
                    extensions = process_extension(line.strip(), extensions)
    else:
        extensions = process_extension(extension, extensions)

    return extensions


@click.command()
@click.option("--interactive", is_flag=True, default=False, help="Build query class from interactive mode")
@click.option("--definition", default=None, type=pathlib.Path, help="Path to query meta definition")
@click.option("--output", default=None, type=pathlib.Path, help="Output file location (only to be paired with --definition)")
def build(interactive, definition, output):
    """Create a cqlalchemy QueryBuilder class from STAC extensions."""
    extensions = {}
    stac_fields_to_ignore = set()
    home_dir = pathlib.Path.home()
    default_file_location = home_dir / "query.py"
    output_file_location = None
    if interactive:
        click.echo("Add extensions to the class, either the path to a local file, a url or the extension json-ld name (sar, sat, etc):")
        while True:
            extension = click.prompt('STAC extension name, raw schema url, or local json extension schema file', default='', show_default=False)
            if extension == '':
                break
            extensions = add_extension(extension, extensions)

        click.echo("Enter stac fields to omit from api or a path with a list of fields to omit:")
        while True:
            field = click.prompt('Field to ignore', default='', show_default=False)
            if field == '':
                break
            try:
                if pathlib.Path(field).exists():
                    with pathlib.Path(field).open("rt") as f:
                        for line in f.readlines():
                            click.echo(f"ignoring field {line.strip()}")
                            stac_fields_to_ignore.add(line.strip())
                else:
                    stac_fields_to_ignore.add(field)
                    click.echo(f"ignoring field {field}")
            except BaseException as be:
                click.echo(f"{field} with {be}")

        add_unique_enum = click.prompt('Add unique enum fields for equals operator',
                                       default=False, type=bool, show_default=True)

    elif definition:
        if not definition.exists():
            ctx = click.get_current_context()
            ctx.fail(f"input {definition} from --definition does not exist")
        elif not output.parent.exists():
            ctx = click.get_current_context()
            ctx.fail(f"output parent directory {output.parent} from --output {output} does not exist")
        with open(definition) as f:
            definition_obj = json.load(f)
        for extension in definition_obj["extensions"]:
            extensions = add_extension(extension, extensions)
        if "stac_fields_to_ignore" in definition_obj:
            for field in definition_obj["stac_fields_to_ignore"]:
                stac_fields_to_ignore.add(field)
        if "add_unique_enum" not in definition_obj:
            add_unique_enum = False
        else:
            add_unique_enum = definition_obj["add_unique_enum"]
        output_file_location = output
    else:
        ctx = click.get_current_context()
        ctx.fail("neither --interactive or --definition options were used")

    if not output_file_location and default_file_location.exists():
        output_file_location = click.prompt('Leave blank to overwrite. Or select a new location to save to',
                                            default=default_file_location, type=pathlib.Path, show_default=True)
    elif not output_file_location:
        output_file_location = click.prompt('Define save location',
                                            default=default_file_location, type=pathlib.Path, show_default=True)

    # Step 3: Create an array using the sorted keys and their corresponding values
    sorted_extensions = [extensions[key] for key in sorted(list(extensions.keys()))]
    sorted_extensions = sorted(sorted_extensions, key=lambda d: d['$id'])
    click.echo(f"Extensions: {[x['title'] for x in sorted_extensions if 'title' in x]}")
    click.echo(f"STAC fields to omit: {stac_fields_to_ignore}")
    query_file_data = build_query_file(sorted_extensions,
                                       fields_to_exclude=stac_fields_to_ignore,
                                       add_unique_enum=add_unique_enum)
    with pathlib.Path(output_file_location).open('wt') as f:
        f.write(query_file_data)


if __name__ == '__main__':
    build()
