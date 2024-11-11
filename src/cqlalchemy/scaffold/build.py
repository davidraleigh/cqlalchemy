import logging
import pkgutil
from string import Template

logger = logging.getLogger(__name__)

enum_template = Template(pkgutil.get_data(__name__, "templates/enum.template").decode('utf-8'))
extension_template = Template(pkgutil.get_data(__name__, "templates/extension.template").decode('utf-8'))
query_template = Template(pkgutil.get_data(__name__, "templates/query.template").decode('utf-8'))

ENUM_MEMBERS = "    {x} = \"{x}\"\n"
ENUM_QUERY_CLASS = "\n    def {x}(self) -> QueryBlock:\n        return self.equals({class_name}.{x})\n"
NUMBER_QUERY_ATTRIBUTE = "        self.{partial_name} = NumberQuery.init_with_limits(\"{field_name}\", query_block, " \
                     "min_value={min_value}, max_value={max_value})\n"
INTEGER_QUERY_ATTRIBUTE = "        self.{partial_name} = NumberQuery.init_with_limits(\"{field_name}\", query_block, " \
                     "min_value={min_value}, max_value={max_value}, is_int=True)\n"
DATETIME_QUERY_ATTR = "        self.{partial_name} = DateQuery(\"field_name\", self)"
STRING_QUERY_ATTRIBUTE = "        self.{partial_name} = StringQuery(\"{field_name}\", self)\n"
ENUM_QUERY_ATTRIBUTE = "        self.{partial_name} = {class_name}Query.init_enums(\"{field_name}\", query_block, " \
                   "[x.value for x in {class_name}])\n"
EXTENSION_ATTRIBUTE = "\n        self.{jsond_prefix} = {class_name}(self)"


def build_enum(field_name: str, enum_object: dict, full_name=False, add_unique=False):
    prefix = ""
    if full_name and ":" in field_name:
        prefix = field_name.split(":")[0].upper()
    if ":" in field_name:
        field_name = field_name.split(":")[1]
    class_name = prefix + "".join([x.capitalize() for x in field_name.split("_")])

    member_definitions = ""
    custom_methods = ""
    for x in enum_object["enum"]:
        member_definitions += ENUM_MEMBERS.format(x=x)
        if add_unique:
            custom_methods += ENUM_QUERY_CLASS.format(x=x, class_name=class_name)

    return enum_template.substitute(class_name=class_name,
                                    member_definitions=member_definitions,
                                    custom_methods=custom_methods), class_name


class ExtensionBuilder:
    def __init__(self, extension_schema, force_string_enum=False):
        description = extension_schema["description"]
        definitions = extension_schema["definitions"]
        field_names = list(definitions["fields"]["properties"].keys())
        field_names.sort()
        self.jsond_prefix = field_names[0].split(":")[0]
        extension_name = self.jsond_prefix.capitalize()
        if extension_name not in description:
            extension_name = extension_name.upper()

        if "v1" in extension_schema["$id"]:
            definitions = definitions["fields"]["properties"]

        enum_definitions = ""
        attribute_instantiations = ""
        for field_name in field_names:
            partial_name = field_name.split(":")[1]
            field_obj = definitions[field_name]
            min_value = None
            if "minimum" in field_obj:
                min_value = field_obj["minimum"]
            max_value = None
            if "maximum" in field_obj:
                max_value = field_obj["maximum"]
            if field_obj["type"] == "number":
                attribute_instantiations += NUMBER_QUERY_ATTRIBUTE.format(field_name=field_name,
                                                                          partial_name=partial_name,
                                                                          min_value=min_value,
                                                                          max_value=max_value)
            elif field_obj["type"] == "integer":
                attribute_instantiations += INTEGER_QUERY_ATTRIBUTE.format(field_name=field_name,
                                                                           partial_name=partial_name,
                                                                           min_value=min_value,
                                                                           max_value=max_value)
            elif field_obj["type"] == "string" and "format" in field_obj and field_obj["format"] == "date-time":
                attribute_instantiations += DATETIME_QUERY_ATTR.format(field_name=field_name, partial_name=partial_name)
            elif field_obj["type"] == "string" and "enum" in field_obj and not force_string_enum:
                enum_definition, class_name = build_enum(field_name, field_obj)
                enum_definitions += enum_definition
                enum_definitions += "\n\n"
                attribute_instantiations += ENUM_QUERY_ATTRIBUTE.format(field_name=field_name,
                                                                        partial_name=partial_name,
                                                                        class_name=class_name)
            elif field_obj["type"] == "string":
                attribute_instantiations += STRING_QUERY_ATTRIBUTE.format(field_name=field_name,
                                                                          partial_name=partial_name)
            elif field_obj["type"] == "array":
                logger.info(f"not producing type {field_obj['type']}")
            else:
                raise ValueError(f"{field_obj['type']} not a processed type")

        self.extension = enum_definitions + extension_template.substitute(extension_name=extension_name,
                                                                          description=description,
                                                                          attribute_instantiations=attribute_instantiations)
        self.class_name = f"{extension_name}Extension"


def build_query_file(extension_list: list[dict]):
    extension_definitions = ""
    extension_attributes = ""
    for extension_schema in extension_list:
        extension_builder = ExtensionBuilder(extension_schema)
        extension_definitions += f"\n\n{extension_builder.extension}"
        extension_attributes += EXTENSION_ATTRIBUTE.format(jsond_prefix=extension_builder.jsond_prefix,
                                                           class_name=extension_builder.class_name)

    return query_template.substitute(extension_definitions=extension_definitions,
                                     common_attributes="",
                                     extension_attributes=extension_attributes)
