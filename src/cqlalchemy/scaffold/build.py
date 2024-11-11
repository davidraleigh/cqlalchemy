import pkgutil
from string import Template

enum_template = Template(pkgutil.get_data(__name__, "templates/enum.template").decode('utf-8'))
extension_template = Template(pkgutil.get_data(__name__, "templates/extension.template").decode('utf-8'))
ENUM_KEY_VALUES = "    {x} = \"{x}\"\n"
ENUM_QUERY_CLASS = "\n    def {x}(self) -> QueryBlock:\n        return self.equals({class_name}.{x})\n"
NUMBER_QUERY_FIELD = "        self.{partial_name} = NumberQuery.init_with_limits(\"{field_name}\", query_block, " \
                     "min_value={min_value}, max_value={max_value})\n"
STRING_QUERY_FIELD = "        self.{partial_name} = StringQuery(\"{field_name}\", self)\n"


def build_enum(enum_field_key: str, enum_object: dict, full_name=False, add_unique=False):
    prefix = ""
    if full_name and ":" in enum_field_key:
        prefix = enum_field_key.split(":")[0].upper()
    if ":" in enum_field_key:
        enum_field_key = enum_field_key.split(":")[1]
    class_name = prefix + "".join([x.capitalize() for x in enum_field_key.split("_")])

    enum_key_values = ""
    custom_methods = ""
    for x in enum_object["enum"]:
        enum_key_values += ENUM_KEY_VALUES.format(x=x)
        if add_unique:
            custom_methods += ENUM_QUERY_CLASS.format(x=x, class_name=class_name)

    return enum_template.substitute(class_name=class_name,
                                    enum_key_values=enum_key_values,
                                    custom_methods=custom_methods)


def build_extension(schema: dict, force_string_enum=False):
    description = schema["description"]
    definitions = schema["definitions"]
    field_names = list(definitions["fields"]["properties"].keys())
    field_names.sort()
    jsond_prefix = field_names[0].split(":")[0]
    extension_name = jsond_prefix.capitalize()
    if extension_name not in description:
        extension_name = extension_name.upper()

    field_instantiations = ""
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
            field_instantiations += NUMBER_QUERY_FIELD.format(field_name=field_name,
                                                              partial_name=partial_name,
                                                              min_value=min_value,
                                                              max_value=max_value)
        elif field_obj["type"] == "string":
            field_instantiations += STRING_QUERY_FIELD.format(field_name=field_name, partial_name=partial_name)

    return extension_template.substitute(extension_name=extension_name,
                                         description=description,
                                         field_instantiations=field_instantiations)
