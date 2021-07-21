from functools import reduce
from urllib.parse import unquote_plus

from py4web import request, Field
from py4web.utils.form import Form, FormStyleBulma


class GridSearchQuery:
    def __init__(self, name, query, requires=None, datatype="str", default=None):
        self.name = name
        self.query = query
        self.requires = requires
        self.datatype = datatype
        self.default = default

        self.field_name = name.replace(" ", "_").lower()


class GridSearch:
    def __init__(self, search_queries, queries=None, target_element=None):
        self.search_queries = search_queries
        self.queries = queries

        field_names = []
        field_requires = dict()
        field_datatype = dict()
        field_default = dict()
        for field in self.search_queries:
            field_name = "sq_" + field.name.replace(" ", "_").replace("/", "_").lower()
            field_names.append(field_name)
            if field.requires and field.requires != "":
                field_requires[field_name] = field.requires
            if field.datatype and field.datatype.lower() == "boolean":
                field_datatype[field_name] = "boolean"
            if field.default:
                field_default[field_name] = field.default

        field_values = dict()
        for field in field_names:
            if field in request.query:
                field_values[field] = unquote_plus(request.query[field])

        form_fields = []
        for field in field_names:
            label = field.replace("sq_", "").replace("_", " ").title()
            placeholder = field.replace("sq_", "").replace("_", " ").capitalize()
            if field in field_datatype:
                datatype = field_datatype[field]
            else:
                datatype = "str"

            if datatype == "boolean":
                if field_values.get(field):
                    default = field_values.get(field)
                else:
                    default = field_default.get(field)
                if default:
                    form_fields.append(
                        Field(
                            field,
                            type=field_datatype[field],
                            label=label,
                            _title=placeholder,
                            default=True,
                        )
                    )
                else:
                    form_fields.append(
                        Field(
                            field,
                            type=field_datatype[field],
                            label=label,
                            _title=placeholder,
                        )
                    )
            else:
                form_fields.append(
                    Field(
                        field,
                        length=50,
                        _placeholder=placeholder,
                        label=label,
                        requires=field_requires.get(field),
                        default=field_values.get(field, field_default.get(field)),
                        _title=placeholder,
                    )
                )

        if target_element:
            attrs = {
                "_hx-post": request.url,
                "_hx-target": target_element,
                "_hx-swap": "innerHTML",
            }
        else:
            attrs = {}

        self.search_form = Form(
            form_fields,
            keep_values=True,
            formstyle=FormStyleBulma,
            form_name="search_form",
            **attrs,
        )

        if self.search_form.accepted:
            for field in field_names:
                if (
                    field in field_datatype
                    and field_datatype[field].lower() == "boolean"
                ):
                    if field in self.search_form.vars:
                        field_values[field] = self.search_form.vars[field]
                    else:
                        field_values[field] = False
                else:
                    field_values[field] = self.search_form.vars[field]

        if not self.queries:
            self.queries = []

        for sq in self.search_queries:
            field_name = "sq_" + sq.name.replace(" ", "_").replace("/", "_").lower()
            if field_name in field_values and field_values[field_name]:
                self.queries.append(sq.query(field_values[field_name]))
            elif field_name in field_default and field_default[field_name]:
                self.queries.append(sq.query(field_default[field_name]))

        self.query = reduce(lambda a, b: (a & b), self.queries)


def apply_htmx_attrs(grid, target):
    myattrs = {"_hx-post": request.url, "_hx-target": target, "_hx-swap": "innerHTML"}

    grid.attributes_plugin["form"] = lambda attrs: attrs.update(myattrs)
    grid.attributes_plugin["link"] = lambda attrs: attrs.update(myattrs)
    grid.attributes_plugin["search_form"] = lambda attrs: attrs.update(myattrs)
    grid.attributes_plugin["button_sort_up"] = lambda attrs: attrs.update(myattrs)
    grid.attributes_plugin["button_sort_down"] = lambda attrs: attrs.update(myattrs)
    grid.attributes_plugin["button_delete"] = lambda attrs: attrs.update(myattrs)
    grid.attributes_plugin["button_page_number"] = lambda attrs: attrs.update(myattrs)


class GridActionButton:
    def __init__(
        self,
        url,
        text=None,
        icon=None,
        onclick=None,
        additional_classes="",
        message="",
        append_id=False,
    ):
        self.url = url
        self.text = text
        self.icon = icon
        self.onclick = onclick
        self.additional_classes = additional_classes
        self.message = message
        self.append_id = append_id
