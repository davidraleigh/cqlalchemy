import pkgutil
from string import Template

enum_template = Template(pkgutil.get_data(__name__, "templates/enum.template").decode('utf-8'))
ENUM_KEY_VALUES = "    {x} = \"{x}\"\n"
ENUM_QUERY_CLASS = "\n    def {x}(self) -> QueryBlock:\n        return self.equals({class_name}.{x})\n"


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
