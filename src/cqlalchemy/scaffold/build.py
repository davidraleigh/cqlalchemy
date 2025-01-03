import datetime
import logging
import pkgutil
from string import Template

from cqlalchemy import __version__

logger = logging.getLogger(__name__)

enum_template = Template(pkgutil.get_data(__name__, "templates/enum.template").decode('utf-8'))
extension_template = Template(pkgutil.get_data(__name__, "templates/extension.template").decode('utf-8'))
query_template = Template(pkgutil.get_data(__name__, "templates/query.template").decode('utf-8'))
common_template = Template(pkgutil.get_data(__name__, "templates/common.template").decode('utf-8'))
common_docs_template = Template(pkgutil.get_data(__name__, "templates/common.docs.template").decode('utf-8'))
enum_custom_method_template = Template(pkgutil.get_data(__name__, "templates/enum.custom.method.template").decode('utf-8'))
number_query_attr_template = Template(pkgutil.get_data(__name__, "templates/number.query.attr.template").decode('utf-8'))
enum_query_attr_template = Template(pkgutil.get_data(__name__, "templates/enum.query.attr.template").decode('utf-8'))

ENUM_MEMBERS = "    {member} = \"{value}\"\n"
SORTABLE_IS_NULL_ATTR = "        self.{partial_name} = _NullCheck(\"{field_name}\", query_block)\n"
DATETIME_QUERY_EXT_ATTR = "        self.{partial_name} = _DateQuery(\"{field_name}\", query_block)\n"
BOOLEAN_QUERY_EXT_ATTR = "        self.{partial_name} = _BooleanQuery(\"{field_name}\", query_block)\n"
DATETIME_QUERY_ATTR = "        self.{partial_name} = _DateQuery(\"{field_name}\", self)\n"
STRING_QUERY_EXT_ATTR = "        self.{partial_name} = _StringQuery(\"{field_name}\", query_block)\n"
STRING_QUERY_ATTR = "        self.{partial_name} = _StringQuery(\"{field_name}\", self)\n"
GEOMETRY_QUERY_ATTR = "        self.{partial_name} = _SpatialQuery(\"{field_name}\", query_block)\n"
EXTENSION_ATTR = "\n        self.{jsond_prefix} = {class_name}(self)"
ATTR_DOC = "    {partial_name} : {class_name}\n        datetime query interface for searching items by the end_datetime field"


def build_enum(field_name: str, enum_object: dict, full_name=False, add_unique=False, field_description=""):
    prefix = ""
    if full_name and ":" in field_name:
        prefix = field_name.split(":")[0].upper()
    if ":" in field_name:
        field_name = field_name.split(":")[1]
    class_name = prefix + "".join([x.capitalize() for x in field_name.split("_")])

    member_definitions = ""
    custom_methods = ""
    for x in enum_object["enum"]:
        member = str(x).replace("-", "_").replace(" ", "_").strip()
        member_definitions += ENUM_MEMBERS.format(member=member, value=x)
        if add_unique:
            custom_methods += enum_custom_method_template.substitute(member=member, class_name=class_name) + "\n"

    field_description_name = " ".join([x.capitalize() for x in field_name.strip().split("_")])
    enum_query_description = f"\n    \"\"\"\n    {field_description_name} Enum Query Interface\n    \"\"\"\n"
    if field_description:
        enum_query_description = f"\n    \"\"\"\n    {field_description_name} Enum Query Interface\n    {field_description}\n    \"\"\"\n"
    enum_description = f"\n    \"\"\"\n    {field_description_name} Enum\n    \"\"\"\n"

    return enum_template.substitute(class_name=class_name,
                                    member_definitions=member_definitions,
                                    custom_methods=custom_methods,
                                    enum_query_description=enum_query_description,
                                    enum_description=enum_description), class_name


def other_attr_doc(partial_name, class_name, field_name):
    data_type = "enum"
    if class_name == "_DateQuery":
        data_type = "datetime"
    elif class_name == "_StringQuery":
        data_type = "string"
    elif class_name == "_SpatialQuery":
        data_type = "geometry"
    elif class_name == "_NullCheck":
        return f"    {partial_name} : {class_name}\n        field can be checked to see if {field_name} is null\n"

    return f"    {partial_name} : {class_name}\n        {data_type} query interface for searching items by the {field_name} field\n"


def number_attr_doc(partial_name, field_name, min_value=None, max_value=None, is_int=False, additional_info=""):
    doc = f"    {partial_name}: _NumberQuery\n        number query interface for searching items by the {field_name} field"
    if min_value is not None:
        doc += f" where the minimum value is {min_value}"
        if max_value is not None:
            doc += f" and the max value is {max_value}"
    elif max_value is not None:
        doc += f" where the maximum value is {max_value}"
    doc += ". Float input."
    if is_int:
        doc += ". Integer input."
    if additional_info:
        doc += additional_info
    return doc + "\n"


class ExtensionBuilder:
    extension = ""
    class_name = ""
    jsond_prefix = ""

    def __init__(self, extension_schema, force_string_enum=False, fields_to_exclude=None, add_unique_enum=False):
        schema_url = extension_schema['$id']
        if fields_to_exclude is None:
            fields_to_exclude = []
        if "description" in extension_schema:
            extension_description = extension_schema["description"]
        elif "title" in extension_schema:
            # TODO 'https://stac-extensions.github.io/storage/v2.0.0/schema.json' is the only reason for this if statement
            extension_description = extension_schema["title"]
        else:
            logger.error(f"schema contains no description or title {schema_url}")
            return
        defs_key = "definitions"
        if defs_key not in extension_schema:
            if "$defs" not in extension_schema:
                # TODO 'https://stac-extensions.github.io/item-assets/v1.0.0/schema.json#', not sure how to handle this
                logger.error(f"contains no definitions field in schema {schema_url}")
                return
            # TODO 'https://stac-extensions.github.io/mlm/v1.3.0/schema.json' is the only reason for this if block
            defs_key = "$defs"
        definitions = extension_schema[defs_key]

        field_names = []
        if "v0" in extension_schema["$id"]:
            logger.error(f"skipping any extensions that are ~v0. This extension is {schema_url}")
            return
        if "fields" in definitions and "properties" in definitions["fields"]:
            field_names = [x for x in list(definitions["fields"]["properties"].keys()) if ":" in x]
            if len(field_names) != len(list(definitions["fields"]["properties"].keys())):
                logger.warning(f"{field_names} less than {list(definitions['fields'].keys())}")
            if len(field_names) > 0 and field_names[0] not in definitions:
                definitions = definitions["fields"]["properties"]
            elif len(field_names) == 0:
                # TODO https://stac-extensions.github.io/render/v1.0.0/schema.json (no json-ld)
                #   https://stac-extensions.github.io/themes/v1.0.0/schema.json (no json-ld)
                #   'https://stac-extensions.github.io/version/v1.2.0/schema.json#'
                logger.error(f"skipping any extensions that are ~v0. This extension is {schema_url}")
                return
            else:
                # TODO 'https://stac-extensions.github.io/mlm/v1.3.0/schema.json'
                #   'https://stac-extensions.github.io/pointcloud/v2.0.0/schema.json#'
                #   'https://stac-extensions.github.io/raster/v2.0.0/schema.json#'
                #   'https://stac-extensions.github.io/pointcloud/v2.0.0/schema.json#'
                logger.warning(f"odd formating for {schema_url}")
        elif "v1" in extension_schema["$id"]:
            # TODO 'https://stac-extensions.github.io/osc/v1.0.0-rc.3/schema.json#'
            #   https://stac-extensions.github.io/tiled-assets/v1.0.0/schema.json
            #   https://stac-extensions.github.io/usfws-nwi/v1.0.0/schema.json
            #   https://stac-extensions.github.io/web-map-links/v1.2.0/schema.json
            #   https://stac-extensions.github.io/authentication/v1.1.0/schema.json
            #   https://stac-extensions.github.io/ml-model/v1.0.0/schema.json
            #   'https://stac-extensions.github.io/alternate-assets/v1.2.0/schema.json#'
            #   'https://stac-extensions.github.io/language/v1.0.0/schema.json#'
            logger.error(f"skipping any extensions that are v1 and missing definitions[\"fields\"][\"properties\"]. This extension is {schema_url}")
            return

        if "fields" in definitions and "properties" not in definitions["fields"]:
            # TODO 'https://stac-extensions.github.io/landsat/v2.0.0/schema.json'
            field_names = [x for x in list(definitions["fields"].keys()) if ":" in x]
            if len(field_names) != len(list(definitions["fields"].keys())):
                logger.warning(f"{field_names} less than {list(definitions['fields'].keys())}")
        elif len(field_names) > 0 and field_names[0] not in definitions:
            # TODO 'https://stac-extensions.github.io/storage/v2.0.0/schema.json'
            logger.error(f"no fields discoverable for schema {schema_url}")

        if len(field_names) == 0:
            # TODO 'https://stac-extensions.github.io/storage/v2.0.0/schema.json'
            logger.error(f"no jsonld ':' separators found in keys {definitions}")
            return

        if field_names[0] not in definitions:
            # TODO 'https://stac-extensions.github.io/landsat/v2.0.0/schema.json'
            definitions = definitions["fields"]

        field_names.sort()
        self.jsond_prefix = field_names[0].split(":")[0]
        extension_name = self.jsond_prefix.capitalize()
        if extension_name not in extension_description:
            extension_name = extension_name.upper()
        self.class_name = f"_{extension_name}Extension"

        enum_definitions = ""
        attribute_instantiations = ""
        extension_attr_docs = ""
        for field_name in field_names:
            if field_name in fields_to_exclude:
                logger.info(f"skipping the field {field_name} as it is included in {fields_to_exclude}")
                continue
            partial_name = field_name.split(":")[1]
            field_obj = definitions[field_name]
            min_value = None
            if "minimum" in field_obj:
                min_value = field_obj["minimum"]
            max_value = None
            if "maximum" in field_obj:
                max_value = field_obj["maximum"]
            if "type" not in field_obj:
                # TODO 'https://stac-extensions.github.io/mlm/v1.3.0/schema.json'
                if "oneOf" in field_obj:
                    for o in field_obj["oneOf"]:
                        if "type" in o and o["type"] != "null":
                            field_obj.update(o)
                elif "anyOf" in field_obj:
                    for o in field_obj["anyOf"]:
                        if "type" in o and o["type"] != "null":
                            field_obj.update(o)
                if "type" not in field_obj:
                    if "$ref" in field_obj and "geojson" in field_obj["$ref"]:
                        field_obj["type"] = "geometry"
                    elif "$ref" in field_obj and field_obj["$ref"].startswith("#/"):
                        keys = field_obj["$ref"].strip("#").strip("/").split("/")
                        d = extension_schema
                        for k in keys:
                            if k in d:
                                d = d[k]
                            else:
                                break
                        if "type" in d:
                            field_obj.update(d)
                    if "type" not in field_obj:
                        logger.warning(f"{field_obj} does not contain type. skipping")
                        continue
            if "description" in field_obj:
                field_description = field_obj["description"]
            elif "title" in field_obj:
                field_description = field_obj["title"]
            else:
                field_description = ""

            if isinstance(field_obj["type"], list):
                if "null" in field_obj["type"]:
                    field_obj["type"].remove("null")
                elif len(field_obj["type"]) > 1:
                    logger.warning(f"array of {field_obj['type']} not supported as type")
                    continue
                if len(field_obj["type"]) == 1:
                    field_obj["type"] = field_obj["type"][0]
                else:
                    logger.warning(f"array of {field_obj['type']} not supported as type")
                    continue
            if field_obj["type"] == "number" or field_obj["type"] == "integer":
                is_int = field_obj["type"] == "integer"
                attribute_instantiations += number_query_attr_template.substitute(field_name=field_name,
                                                                                  partial_name=partial_name,
                                                                                  min_value=min_value,
                                                                                  max_value=max_value,
                                                                                  is_int=is_int)
                extension_attr_docs += number_attr_doc(partial_name=partial_name,
                                                       field_name=field_name,
                                                       min_value=min_value,
                                                       max_value=max_value,
                                                       is_int=is_int)
            elif field_obj["type"] == "string" and "format" in field_obj and field_obj["format"] == "date-time":
                attribute_instantiations += DATETIME_QUERY_EXT_ATTR.format(field_name=field_name,
                                                                           partial_name=partial_name)
                extension_attr_docs += other_attr_doc(partial_name=partial_name, class_name="_DateQuery", field_name=field_name)
            elif field_obj["type"] == "string" and "enum" in field_obj and not force_string_enum and not any(s[0].isdigit() for s in field_obj["enum"]):
                # landsat enum -> not any(s[0].isdigit() for s in field_obj["enum"])
                enum_definition, class_name = build_enum(field_name, field_obj, add_unique=add_unique_enum, field_description=field_description)
                enum_definitions += enum_definition
                enum_definitions += "\n\n"
                attribute_instantiations += enum_query_attr_template.substitute(field_name=field_name,
                                                                                partial_name=partial_name,
                                                                                class_name=class_name)
                e_class = f"_{class_name}Query"
                extension_attr_docs += other_attr_doc(partial_name=partial_name, class_name=e_class, field_name=field_name)
            elif field_obj["type"] == "string":
                attribute_instantiations += STRING_QUERY_EXT_ATTR.format(field_name=field_name,
                                                                         partial_name=partial_name)
                extension_attr_docs += other_attr_doc(partial_name=partial_name,
                                                      class_name="_StringQuery",
                                                      field_name=field_name)
            elif field_obj["type"] == "boolean":
                attribute_instantiations += BOOLEAN_QUERY_EXT_ATTR.format(field_name=field_name,
                                                                          partial_name=partial_name)
                extension_attr_docs += other_attr_doc(partial_name=partial_name,
                                                      class_name="_BooleanQuery",
                                                      field_name=field_name)
            elif field_obj["type"] == "geometry":
                attribute_instantiations += GEOMETRY_QUERY_ATTR.format(field_name=field_name,
                                                                       partial_name=partial_name)
                extension_attr_docs += other_attr_doc(partial_name=partial_name,
                                                      class_name="_SpatialQuery",
                                                      field_name=field_name)
            elif field_obj["type"] in ["array", "object"]:
                attribute_instantiations += SORTABLE_IS_NULL_ATTR.format(field_name=field_name, partial_name=partial_name)
                extension_attr_docs += other_attr_doc(partial_name=partial_name,
                                                      class_name="_NullCheck",
                                                      field_name=field_name)
                logger.info(f"not producing type {field_obj['type']}")
            else:
                raise ValueError(f"{field_obj['type']} not a processed type")

        extension_attr_docs = extension_attr_docs.rstrip()
        self.extension = enum_definitions + extension_template.substitute(class_name=self.class_name,
                                                                          extension_description=extension_description,
                                                                          extension_attr_docs=extension_attr_docs,
                                                                          attribute_instantiations=attribute_instantiations)


def build_query_file(extension_list: list[dict], fields_to_exclude=None, add_unique_enum=False) -> str:
    if fields_to_exclude is None:
        fields_to_exclude = []
    else:
        fields_to_exclude = list(fields_to_exclude)

    extension_definitions = ""
    extension_attributes = ""
    for extension_schema in extension_list:
        extension_builder = ExtensionBuilder(extension_schema, fields_to_exclude=fields_to_exclude, add_unique_enum=add_unique_enum)
        extension_definitions += f"\n\n{extension_builder.extension}"
        extension_attributes += EXTENSION_ATTR.format(jsond_prefix=extension_builder.jsond_prefix,
                                                      class_name=extension_builder.class_name)

    common_props_lines = common_template.substitute().split("\n")
    common_docs_props_lines = common_docs_template.substitute().split("\n")
    common_props = "\n"
    common_docs_props = "\n"
    if fields_to_exclude is not None:
        common_props_lines = [line for line in common_props_lines if not any(field in line for field in fields_to_exclude)]
        for i in range(0, len(common_props_lines)):
            line0 = common_docs_props_lines[i * 2]
            line1 = common_docs_props_lines[i * 2 + 1]
            if not any(field in line0 for field in fields_to_exclude):
                common_docs_props += line0 + "\n"
                common_docs_props += line1 + "\n"
    else:
        common_docs_props = "\n" + common_docs_template.substitute()

    sorted_fields_to_include = sorted([f for f in fields_to_exclude if ":" not in f])
    sorted_fields_to_include.extend(sorted([f for f in fields_to_exclude if ":" in f]))
    common_props += "\n".join(common_props_lines)
    extension_list_comment = "# None" if len(extension_list) == 0 else "\n".join([f"# {e['$id']}" for e in extension_list])
    fields_to_exclude_comment = "# None" if len(fields_to_exclude) == 0 else "\n".join([f"# {f}" for f in sorted_fields_to_include])
    return query_template.substitute(cqlalchemy_version=__version__,
                                     extension_list=extension_list_comment,
                                     ignored_fields_list=fields_to_exclude_comment,
                                     today_date=datetime.date.today(),
                                     add_unique_enum=add_unique_enum,
                                     extension_definitions=extension_definitions,
                                     common_attributes=common_props,
                                     common_docs=common_docs_props.rstrip(),
                                     extension_attributes=extension_attributes)
