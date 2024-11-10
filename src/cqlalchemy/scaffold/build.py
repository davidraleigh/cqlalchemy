import pkgutil
from string import Template

enum_template = Template(pkgutil.get_data(__name__, "templates/enum.template").decode('utf-8'))


def build_enum(enum_field_key: str, enum_object: dict, full_name=False, add_unique=False):
    prefix = ""
    if full_name and ":" in enum_field_key:
        prefix = enum_field_key.split(":")[0].upper()
    if ":" in enum_field_key:
        enum_field_key = enum_field_key.split(":")[1]
    class_name = prefix + "".join([x.capitalize() for x in enum_field_key.split("_")])

    enum_key_values = "\n".join([f"    {x} = \"{x}\"" for x in enum_object["enum"]])
    custom_methods = ""
    if add_unique:
        custom_methods = "\n"
        custom_methods += "\n".join([f"    def {x}(self) -> QueryBlock:\n        return self.equals({class_name}.{x})\n" for x in enum_object["enum"]])

    return enum_template.substitute(class_name=class_name,
                                    enum_key_values=enum_key_values,
                                    custom_methods=custom_methods)
