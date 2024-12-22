import copy

import ombott
from dateutil.parser import parse
from pydal.validators import IS_NULL_OR, IS_IN_DB
from yatl import TAG, XML, I

from py4web.utils.form import FormStyleBulma, Form, FormStyleFactory

from py4web import action, request, abort, redirect, URL, Field
from yatl.helpers import A

from py4web.utils.grid import (
    Column,
    Grid,
    GridClassStyleBulma,
    AttributesPluginHtmx,
    get_parent,
)
from .common import (
    db,
    session,
    T,
    cache,
    auth,
    logger,
    authenticated,
    unauthenticated,
    flash,
    GRID_DEFAULTS,
)
from .htmx import HtmxAutocompleteWidget
from .lib.grid_helpers import GridSearchQuery, GridSearch

BUTTON = TAG.button

CUSTOMER_DETAIL_FIELDS = [
    "name",
    "contact",
    "title",
    "address",
    "city",
    "region",
    "postal_code",
    "phone",
    "email",
]

CUSTOMER_NOTE_FIELDS = [
    "notes",
]

EMPLOYEE_DETAIL_FIELDS = [
    "first_name",
    "last_name",
    "title",
    "title_of_courtesy",
    "birth_date",
    "hire_date",
    "address",
    "city",
    "region",
    "postal_code",
    "country",
    "phone",
    "extension",
    "notes",
    "supervisor",
    "sales_region",
]

PRODUCT_DETAIL_FIELDS = [
    "name",
    "supplier",
    "category",
    "quantity_per_unit",
    "unit_price",
    "in_stock",
    "on_order",
    "reorder_level",
    "discontinued",
]


ORDER_DETAIL_FIELDS = [
    "customer",
    "employee",
    "order_date",
    "required_date",
    "shipped_date",
    "shipper",
    "freight",
    "ship_to_name",
    "ship_to_address",
    "ship_to_city",
    "ship_to_region",
    "ship_to_postal_code",
    "ship_to_country",
]

ORDER_DETAIL_DETAIL_FIELDS = ["product", "unit_price", "quantity", "discount"]


@unauthenticated("index", "index.html")
def index():
    user = auth.get_user()
    message = T("Hello {first_name}".format(**user) if user else "Hello")
    return dict(message=message)


@authenticated("setup", "setup.html")
def setup():
    return dict()


@action("setup/sales_regions", method=["POST", "GET"])
@action("setup/sales_regions/<path:path>", method=["POST", "GET"])
@action.uses(
    "htmx/grid.html",
    session,
    db,
    auth.user,
)
def sales_regions(path=None):
    queries = [db.sales_region.id > 0]

    search_queries = [
        GridSearchQuery(
            "Filter by sales_region", lambda value: db.sales_region.name.contains(value)
        )
    ]
    search = GridSearch(
        search_queries=search_queries,
        queries=queries,
        target_element="#sales-regions-target",
    )

    fields = [
        db.sales_region.name,
    ]

    gd = copy.deepcopy(GRID_DEFAULTS)
    gd["rows_per_page"] = 10

    grid = Grid(
        path,
        search.query,
        fields=fields,
        orderby=db.sales_region.name,
        details=False,
        search_form=search.search_form,
        auto_process=False,
        include_action_button_text=False,
        **gd,
    )

    grid.attributes_plugin = AttributesPluginHtmx("#sales-regions-target")
    attrs = {
        "_hx-get": URL("setup", "sales_regions"),
        "_class": "button is-default",
    }
    grid.param.new_sidecar = BUTTON("Cancel", **attrs)
    grid.param.details_sidecar = BUTTON("Cancel", **attrs)
    grid.param.edit_sidecar = BUTTON("Cancel", **attrs)

    grid.process()

    return dict(grid=grid)


@action("setup/territories", method=["POST", "GET"])
@action("setup/territories/<path:path>", method=["POST", "GET"])
@action.uses(
    "htmx/grid.html",
    session,
    db,
    auth,
)
def territories(path=None):
    queries = [db.territory.id > 0]

    search_queries = [
        GridSearchQuery(
            "Filter by territory", lambda value: db.territory.name.contains(value)
        )
    ]
    search = GridSearch(
        search_queries=search_queries,
        queries=queries,
        target_element="#territories-target",
    )

    fields = [
        db.territory.name,
        Column(
            "sales_region",
            lambda row: f"{row.sales_region.name}",
            required_fields=[db.sales_region.name],
            orderby=db.sales_region.name,
        ),
    ]
    left = db.sales_region.on(db.territory.sales_region == db.sales_region.id)

    gd = copy.deepcopy(GRID_DEFAULTS)
    gd["rows_per_page"] = 10

    grid = Grid(
        path,
        query=search.query,
        fields=fields,
        left=left,
        orderby=[db.territory.name],
        auto_process=False,
        details=False,
        search_form=search.search_form,
        include_action_button_text=False,
        **gd,
    )

    grid.attributes_plugin = AttributesPluginHtmx("#territories-target")
    attrs = {
        "_hx-get": URL("setup", "territories"),
        "_class": "button is-default",
    }
    grid.param.new_sidecar = BUTTON("Cancel", **attrs)
    grid.param.details_sidecar = BUTTON("Cancel", **attrs)
    grid.param.edit_sidecar = BUTTON("Cancel", **attrs)

    grid.process()

    return dict(grid=grid)


@action("setup/customer_types", method=["POST", "GET"])
@action("setup/customer_types/<path:path>", method=["POST", "GET"])
@action.uses(
    "htmx/grid.html",
    session,
    db,
    auth.user,
)
def customer_types(path=None):
    orderby = [db.customer_type.name]

    queries = [db.customer_type.id > 0]

    search_queries = [
        GridSearchQuery(
            "Filter by customer type",
            lambda value: db.customer_type.name.contains(value),
        )
    ]
    search = GridSearch(
        search_queries=search_queries,
        queries=queries,
        target_element="#customer-types-target",
    )

    fields = [
        db.customer_type.name,
    ]

    gd = copy.deepcopy(GRID_DEFAULTS)
    gd["rows_per_page"] = 10

    grid = Grid(
        path,
        search.query,
        fields=fields,
        orderby=orderby,
        details=False,
        search_form=search.search_form,
        auto_process=False,
        include_action_button_text=False,
        **gd,
    )

    grid.attributes_plugin = AttributesPluginHtmx("#customer-types-target")
    attrs = {
        "_hx-get": URL("setup", "customer_types"),
        "_class": "button is-default",
    }
    grid.param.new_sidecar = BUTTON("Cancel", **attrs)
    grid.param.details_sidecar = BUTTON("Cancel", **attrs)
    grid.param.edit_sidecar = BUTTON("Cancel", **attrs)

    grid.process()

    return dict(grid=grid)


@action("setup/categories", method=["POST", "GET"])
@action("setup/categories/<path:path>", method=["POST", "GET"])
@action.uses(
    "htmx/grid.html",
    session,
    db,
    auth,
)
def categories(path=None):
    queries = [db.category.id > 0]

    search_queries = [
        GridSearchQuery(
            "Filter by category", lambda value: db.category.name.contains(value)
        )
    ]
    search = GridSearch(
        search_queries=search_queries,
        queries=queries,
        target_element="#categories-target",
    )

    fields = [
        db.category.name,
    ]

    gd = copy.deepcopy(GRID_DEFAULTS)
    gd["rows_per_page"] = 10

    grid = Grid(
        path,
        query=search.query,
        fields=fields,
        orderby=[db.category.name],
        auto_process=False,
        details=False,
        search_form=search.search_form,
        include_action_button_text=False,
        **gd,
    )

    grid.attributes_plugin = AttributesPluginHtmx("#categories-target")
    attrs = {
        "_hx-get": URL("setup", "categories"),
        "_class": "button is-default",
    }
    grid.param.new_sidecar = BUTTON("Cancel", **attrs)
    grid.param.details_sidecar = BUTTON("Cancel", **attrs)
    grid.param.edit_sidecar = BUTTON("Cancel", **attrs)

    grid.process()

    return dict(grid=grid)


@action("setup/shippers", method=["POST", "GET"])
@action("setup/shippers/<path:path>", method=["POST", "GET"])
@action.uses(
    "htmx/grid.html",
    session,
    db,
    auth.user,
)
def shippers(path=None):
    orderby = [db.shipper.name]

    queries = [db.shipper.id > 0]

    search_queries = [
        GridSearchQuery(
            "Filter by customer type",
            lambda value: db.shipper.name.contains(value),
        )
    ]
    search = GridSearch(
        search_queries=search_queries,
        queries=queries,
        target_element="#shippers-target",
    )

    fields = [db.shipper.name, db.shipper.phone]

    gd = copy.deepcopy(GRID_DEFAULTS)
    gd["rows_per_page"] = 10

    grid = Grid(
        path,
        search.query,
        fields=fields,
        orderby=orderby,
        details=False,
        search_form=search.search_form,
        auto_process=False,
        include_action_button_text=False,
        **gd,
    )

    grid.attributes_plugin = AttributesPluginHtmx("#shippers-target")
    attrs = {
        "_hx-get": URL("setup", "shippers"),
        "_class": "button is-default",
    }
    grid.param.new_sidecar = BUTTON("Cancel", **attrs)
    grid.param.details_sidecar = BUTTON("Cancel", **attrs)
    grid.param.edit_sidecar = BUTTON("Cancel", **attrs)

    grid.process()

    return dict(grid=grid)


@action("customers", method=["POST", "GET"])
@action("customers/<path:path>", method=["POST", "GET"])
@action.uses(
    "customers.html",
    session,
    db,
    auth.user,
)
def customers(path=None):
    search_queries = [
        GridSearchQuery(
            "Filter by Name", lambda value: db.customer.name.contains(value)
        ),
    ]

    queries = [(db.customer.id > 0)]
    fields = [
        Column(
            "Name",
            represent=lambda row: XML(
                f"{row.name}<br />{row.address}<br />{row.city}, {row.region} {row.postal_code}"
            ),
            required_fields=[
                db.customer.name,
                db.customer.address,
                db.customer.city,
                db.customer.region,
                db.customer.postal_code,
            ],
            orderby=db.customer.name,
        ),
        Column(
            "Contact",
            represent=lambda row: XML(
                f"{row.contact}<br />{row.title}<br />{row.phone}"
            ),
            required_fields=[db.customer.contact, db.customer.title, db.customer.phone],
            orderby=db.customer.contact,
        ),
        Column(
            "Types",
            represent=lambda row: XML(
                ",<br />".join(
                    x.name
                    for x in db(
                        db.customer_type.id.belongs(
                            db(db.customer_customer_type.customer == row.id)._select(
                                db.customer_customer_type.customer_type
                            )
                        )
                    ).select(orderby=db.customer_type.name, distinct=True)
                )
            ),
        ),
    ]
    orderby = [db.customer.name]

    search = GridSearch(search_queries, queries)

    gd = copy.deepcopy(GRID_DEFAULTS)
    gd["rows_per_page"] = 8

    grid = Grid(
        path,
        search.query,
        fields=fields,
        orderby=orderby,
        editable=False,
        search_form=search.search_form,
        auto_process=False,
        **gd,
    )

    grid.param.details_submit_value = "Done"
    grid.process()

    parent_id = None
    customer = None
    if grid.action in ["details", "edit"]:
        parent_id = grid.record_id
        customer = db.customer(parent_id)
    elif grid.action in ["new"]:
        redirect(URL("customer_new"))

    return dict(grid=grid, parent_id=parent_id, customer=customer)


@action(
    "customer_new",
    method=["GET", "POST"],
)
@action.uses(
    "customer_new.html",
    session,
    db,
)
def customer_new():
    db.customer.id.readable = False

    form = Form(
        db.customer,
        formstyle=FormStyleBulma,
    )

    attrs = {
        "_onclick": "window.history.back(); return false;",
        "_class": "button is-default",
    }
    form.param.sidecar.append(BUTTON("Cancel", **attrs))

    if form.accepted:
        redirect(URL("customers/details/%s" % form.vars["id"]))

    return dict(form=form, DETAIL_FIELDS=CUSTOMER_DETAIL_FIELDS, tablename="customer")


@action("customer_detail/<customer_id>", method=["GET", "POST"])
@action.uses(
    "htmx/form.html",
    session,
    db,
    auth.user,
)
def customer_detail(customer_id=None):
    customer = db.customer(customer_id)
    if not customer:
        ombott.abort(
            code=401,
            text="Could not retrieve customer.  Please contact support.",
        )

    for field in db.customer.fields:
        if field not in CUSTOMER_DETAIL_FIELDS:
            db.customer[field].readable = False

    db.customer.id.readable = True

    attrs = {
        "_hx-get": URL("customer_detail_edit/%s" % customer_id),
        "_hx-target": "#details-target",
    }

    form = Form(
        db.customer,
        record=customer,
        readonly=True,
        deletable=False,
        formstyle=FormStyleBulma,
        dbio=False,
        submit_value="Edit",
        **attrs,
    )

    edit_button = BUTTON(
        I(_class="fa fa-edit"), _class="submit-edit box-shadow-y", **attrs
    )

    return dict(form=form, form_fields=CUSTOMER_DETAIL_FIELDS, edit_button=edit_button)


@action(
    "customer_detail_edit/<customer_id>",
    method=["GET", "POST"],
)
@action.uses(
    "htmx/form.html",
    session,
    db,
    auth.user,
)
def customer_detail_edit(customer_id=None):
    customer = db.customer(customer_id)
    if not customer:
        ombott.abort(
            code=401,
            text="Could not retrieve customer.  Please contact support.",
        )

    for field in db.customer.fields:
        if field not in CUSTOMER_DETAIL_FIELDS:
            db.customer[field].readable = False
            db.customer[field].writable = False

    db.customer.id.readable = True

    attrs = {
        "_hx-post": URL("customer_detail_edit/%s" % customer_id),
        "_hx-target": "#details-target",
    }

    form = Form(
        db.customer,
        record=customer,
        formstyle=FormStyleBulma,
        **attrs,
    )

    attrs = {
        "_hx-get": URL("customer_detail/%s" % customer_id),
        "_hx-target": "#details-target",
        "_class": "button is-default",
    }
    form.param.sidecar.append(BUTTON("Cancel", **attrs))

    if form.accepted:
        redirect(URL("customer_detail/%s" % customer_id))

    return dict(form=form, form_fields=CUSTOMER_DETAIL_FIELDS)


@action("customer_notes", method=["POST", "GET"])
@action("customer_notes/<path:path>", method=["POST", "GET"])
@action.uses(
    "htmx/grid.html",
    session,
    db,
    auth,
)
def customer_notes(path=None):
    #  set the default
    customer_id = get_parent(
        path,
        parent_field=db.customer_note.customer,
    )

    customer = db.customer(customer_id)
    db.customer_note.customer.default = customer_id

    if path and path.split("/")[0] in ["new", "details", "edit"]:
        db.customer_note.customer.readable = False
        db.customer_note.customer.writable = False

        db.customer_note.timestamp.readable = False
        db.customer_note.timestamp.writable = False

    query = db.customer_note.customer == customer_id

    left = (db.customer.on(db.customer_note.customer == db.customer.id),)

    grid = Grid(
        path,
        fields=[db.customer_note.timestamp, db.customer_note.note],
        orderby=~db.customer_note.timestamp,
        query=query,
        left=left,
        auto_process=False,
        details=False,
        include_action_button_text=False,
        **GRID_DEFAULTS,
    )

    grid.formatters_by_type["datetime"] = (
        lambda value: value.strftime("%m/%d/%Y %I:%M%p") if value else ""
    )

    grid.attributes_plugin = AttributesPluginHtmx("#notes-target")
    attrs = {
        "_hx-get": URL(
            "customer_notes",
            vars=dict(parent_id=customer_id),
        ),
        "_class": "button is-default",
    }
    grid.param.new_sidecar = BUTTON("Cancel", **attrs)
    grid.param.edit_sidecar = BUTTON("Cancel", **attrs)

    grid.process()

    return dict(grid=grid)


@action("customer_customer_types", method=["POST", "GET"])
@action("customer_customer_types/<path:path>", method=["POST", "GET"])
@action.uses(
    "htmx/grid.html",
    session,
    db,
    auth,
)
def customer_customer_types(path=None):
    #  set the default
    customer_id = get_parent(
        path,
        parent_field=db.customer_customer_type.customer,
    )

    customer = db.customer(customer_id)
    db.customer_customer_type.customer.default = customer_id

    if path and path.split("/")[0] in ["new", "details", "edit"]:
        db.customer_customer_type.customer.readable = False
        db.customer_customer_type.customer.writable = False

    query = db.customer_customer_type.customer == customer_id

    left = (
        db.customer_type.on(
            db.customer_customer_type.customer_type == db.customer_type.id
        ),
    )

    grid = Grid(
        path,
        fields=[db.customer_type.name],
        orderby=db.customer_type.name,
        query=query,
        left=left,
        auto_process=False,
        details=False,
        include_action_button_text=False,
        **GRID_DEFAULTS,
    )

    grid.attributes_plugin = AttributesPluginHtmx("#types-target")
    attrs = {
        "_hx-get": URL(
            "customer_customer_types",
            vars=dict(parent_id=customer_id),
        ),
        "_class": "button is-default",
    }
    grid.param.new_sidecar = BUTTON("Cancel", **attrs)
    grid.param.edit_sidecar = BUTTON("Cancel", **attrs)

    grid.process()

    return dict(grid=grid)


def get_products_for_row(row):
    products = []
    for od in db(db.order_detail.order == row.id).select():
        if od.product.name not in products:
            products.append(od.product.name)

    return XML(",<br />".join(products))


@action("customer_orders", method=["POST", "GET"])
@action("customer_orders/<path:path>", method=["POST", "GET"])
@action.uses(
    "htmx/grid.html",
    session,
    db,
    auth,
)
def customer_orders(path=None):
    #  set the default
    customer_id = get_parent(
        path,
        parent_field=db.order.customer,
    )

    query = db.order.customer == customer_id

    grid = Grid(
        path,
        fields=[
            db.order.id,
            Column(
                "Order Date",
                represent=lambda row: row.order_date.strftime("%m/%d/%Y")
                if row.order_date
                else "",
                required_fields=[db.order.order_date],
            ),
            db.order.subtotal,
            db.order.freight,
            db.order.total,
        ],
        orderby=[~db.order.order_date, ~db.order.id],
        query=query,
        show_id=True,
        auto_process=False,
        create=False,
        details=False,
        editable=False,
        deletable=False,
        include_action_button_text=False,
        **GRID_DEFAULTS,
    )

    # grid.formatters_by_type["date"] = (
    #     lambda value: value.strftime("%m/%d/%Y") if value else ""
    # )

    grid.attributes_plugin = AttributesPluginHtmx("#orders-target")
    grid.process()

    return dict(grid=grid)


@action("employees", method=["POST", "GET"])
@action("employees/<path:path>", method=["POST", "GET"])
@action.uses(
    "employees.html",
    session,
    db,
    auth.user,
)
def employees(path=None):
    search_queries = [
        GridSearchQuery(
            "Filter by Name city or region",
            lambda value: f"first_name || ' ' || last_Name LIKE '%%{value}%%'"
            | db.employee.city.contains(value)
            | db.employee.region.contains(value),
        ),
    ]

    queries = [(db.employee.id > 0)]
    fields = [
        Column(
            "Name",
            lambda row: XML(
                f"{row.first_name} {row.last_name}<br />{row.address}<br />{row.city}, {row.region} {row.postal_code}"
            ),
            required_fields=[
                db.employee.first_name,
                db.employee.last_name,
                db.employee.address,
                db.employee.city,
                db.employee.region,
                db.employee.postal_code,
            ],
            orderby=db.employee.last_name,
        ),
    ]
    orderby = [db.employee.last_name, db.employee.first_name]

    search = GridSearch(search_queries, queries)

    gd = copy.deepcopy(GRID_DEFAULTS)
    gd["rows_per_page"] = 8

    grid = Grid(
        path,
        search.query,
        fields=fields,
        orderby=orderby,
        editable=False,
        search_form=search.search_form,
        auto_process=False,
        **gd,
    )

    grid.param.details_submit_value = "Done"
    grid.process()

    parent_id = None
    employee = None
    if grid.action in ["details", "edit"]:
        parent_id = grid.record_id
        employee = db.employee(parent_id)
    elif grid.action in ["new"]:
        redirect(URL("employee_new"))

    return dict(grid=grid, parent_id=parent_id, employee=employee)


@action(
    "employee_new",
    method=["GET", "POST"],
)
@action.uses(
    "employee_new.html",
    session,
    db,
)
def employee_new():
    db.employee.id.readable = False

    form = Form(
        db.employee,
        formstyle=FormStyleBulma,
    )

    attrs = {
        "_onclick": "window.history.back(); return false;",
        "_class": "button is-default",
    }
    form.param.sidecar.append(BUTTON("Cancel", **attrs))

    if form.accepted:
        redirect(URL("employees/details/%s" % form.vars["id"]))

    return dict(form=form, DETAIL_FIELDS=EMPLOYEE_DETAIL_FIELDS, tablename="employee")


@action("employee_detail/<employee_id>", method=["GET", "POST"])
@action.uses("htmx/form.html", session, db, auth.user)
def employee_detail(employee_id=None):
    employee = db.employee(employee_id)
    if not employee:
        ombott.abort(
            code=401,
            text="Could not retrieve employee.  Please contact support.",
        )

    for field in db.employee.fields:
        if field not in EMPLOYEE_DETAIL_FIELDS:
            db.employee[field].readable = False

    db.employee.id.readable = True

    attrs = {
        "_hx-get": URL("employee_detail_edit/%s" % employee_id),
        "_hx-target": "#details-target",
    }

    form = Form(
        db.employee,
        record=employee,
        readonly=True,
        deletable=False,
        formstyle=FormStyleBulma,
        dbio=False,
        submit_value="Edit",
        **attrs,
    )

    edit_button = BUTTON(
        I(_class="fa fa-edit"), _class="submit-edit box-shadow-y", **attrs
    )

    return dict(form=form, form_fields=EMPLOYEE_DETAIL_FIELDS, edit_button=edit_button)


@action(
    "employee_detail_edit/<employee_id>",
    method=["GET", "POST"],
)
@action.uses(
    "htmx/form.html",
    session,
    db,
    auth.user,
)
def employee_detail_edit(employee_id=None):
    employee = db.employee(employee_id)
    if not employee:
        ombott.abort(
            code=401,
            text="Could not retrieve employee.  Please contact support.",
        )

    for field in db.employee.fields:
        if field not in EMPLOYEE_DETAIL_FIELDS:
            db.employee[field].readable = False
            db.employee[field].writable = False

    db.employee.id.readable = True

    attrs = {
        "_hx-post": URL("employee_detail_edit/%s" % employee_id),
        "_hx-target": "#details-target",
    }

    form = Form(
        db.employee,
        record=employee,
        formstyle=FormStyleBulma,
        **attrs,
    )

    attrs = {
        "_hx-get": URL("employee_detail/%s" % employee_id),
        "_hx-target": "#details-target",
        "_class": "button is-default",
    }
    form.param.sidecar.append(BUTTON("Cancel", **attrs))

    if form.accepted:
        redirect(URL("employee_detail/%s" % employee_id))

    return dict(form=form, form_fields=EMPLOYEE_DETAIL_FIELDS)


@action("employee_territories", method=["POST", "GET"])
@action("employee_territories/<path:path>", method=["POST", "GET"])
@action.uses(
    "htmx/grid.html",
    session,
    db,
    auth,
)
def employee_territories(path=None):
    #  set the default
    employee_id = get_parent(
        path,
        parent_field=db.employee_territory.employee,
    )

    employee = db.employee(employee_id)
    db.employee_territory.employee.default = employee_id

    if path and path.split("/")[0] in ["new", "details", "edit"]:
        db.employee_territory.employee.readable = False
        db.employee_territory.employee.writable = False

    query = db.employee_territory.employee == employee_id

    left = (db.territory.on(db.employee_territory.territory == db.territory.id),)

    grid = Grid(
        path,
        fields=[db.territory.name],
        orderby=db.territory.name,
        query=query,
        left=left,
        auto_process=False,
        details=False,
        include_action_button_text=False,
        **GRID_DEFAULTS,
    )

    grid.attributes_plugin = AttributesPluginHtmx("#territories-target")
    attrs = {
        "_hx-get": URL(
            "employee_territories",
            vars=dict(parent_id=employee_id),
        ),
        "_class": "button is-default",
    }
    grid.param.new_sidecar = BUTTON("Cancel", **attrs)
    grid.param.edit_sidecar = BUTTON("Cancel", **attrs)

    grid.process()

    return dict(grid=grid)


@action("employee_orders", method=["POST", "GET"])
@action("employee_orders/<path:path>", method=["POST", "GET"])
@action.uses(
    "htmx/grid.html",
    session,
    db,
    auth,
)
def employee_orders(path=None):
    #  set the default
    employee_id = get_parent(
        path,
        parent_field=db.order.employee,
    )

    query = db.order.employee == employee_id

    grid = Grid(
        path,
        fields=[
            db.order.id,
            Column(
                "Order Date",
                represent=lambda row: row.order_date.strftime("%m/%d/%Y")
                if row.order_date
                else "",
                required_fields=[db.order.order_date],
            ),
            db.order.subtotal,
            db.order.freight,
            db.order.total,
        ],
        orderby=[~db.order.order_date, ~db.order.id],
        query=query,
        show_id=True,
        auto_process=False,
        create=False,
        details=False,
        editable=False,
        deletable=False,
        include_action_button_text=False,
        **GRID_DEFAULTS,
    )

    grid.formatters_by_type["date"] = (
        lambda value: value.strftime("%m/%d/%Y") if value else ""
    )

    grid.attributes_plugin = AttributesPluginHtmx("#orders-target")
    grid.process()

    return dict(grid=grid)


@action("products", method=["POST", "GET"])
@action("products/<path:path>", method=["POST", "GET"])
@action.uses(
    "products.html",
    session,
    db,
    auth.user,
)
def products(path=None):
    search_queries = [
        GridSearchQuery(
            "Filter by Supplier",
            lambda value: db.product.supplier == value,
            requires=IS_NULL_OR(
                IS_IN_DB(
                    db(
                        db.supplier.id.belongs(
                            db(db.product.id > 0)._select(
                                db.product.supplier, distinct=True
                            )
                        )
                    ),
                    "supplier.id",
                    "%(name)s",
                    zero="..",
                )
            ),
        ),
        GridSearchQuery(
            "Filter by Category",
            lambda value: db.product.category == value,
            requires=IS_NULL_OR(
                IS_IN_DB(
                    db(
                        db.category.id.belongs(
                            db(db.product.id > 0)._select(
                                db.product.category, distinct=True
                            )
                        )
                    ),
                    "category.id",
                    "%(name)s",
                    zero="..",
                )
            ),
        ),
        GridSearchQuery(
            "Filter by Name", lambda value: db.product.name.contains(value)
        ),
    ]

    queries = [(db.product.id > 0)]
    fields = [
        db.product.name,
        Column(
            "supplier",
            lambda row: row.supplier.name if row.supplier else "",
            required_fields=[db.supplier.name],
            orderby=db.supplier.name,
        ),
        Column(
            "category",
            lambda row: row.category.name if row.category else "",
            required_fields=[db.category.name],
            orderby=db.category.name,
        ),
    ]
    orderby = [db.product.name]

    left = [
        db.supplier.on(db.product.supplier == db.supplier.id),
        db.category.on(db.product.category == db.category.id),
    ]

    search = GridSearch(search_queries, queries)

    grid = Grid(
        path,
        search.query,
        fields=fields,
        left=left,
        orderby=orderby,
        editable=False,
        search_form=search.search_form,
        auto_process=False,
        **GRID_DEFAULTS,
    )

    grid.param.details_submit_value = "Done"
    grid.process()

    parent_id = None
    product = None
    if grid.action in ["details", "edit"]:
        parent_id = grid.record_id
        product = db.product(parent_id)
    elif grid.action in ["new"]:
        redirect(URL("product_new"))

    return dict(grid=grid, parent_id=parent_id, product=product)


@action(
    "product_new",
    method=["GET", "POST"],
)
@action.uses(
    "product_new.html",
    session,
    db,
)
def product_new():
    db.product.id.readable = False

    form = Form(
        db.product,
        formstyle=FormStyleBulma,
    )

    attrs = {
        "_onclick": "window.history.back(); return false;",
        "_class": "button is-default",
    }
    form.param.sidecar.append(BUTTON("Cancel", **attrs))

    if form.accepted:
        redirect(URL("products/details/%s" % form.vars["id"]))

    return dict(form=form, DETAIL_FIELDS=PRODUCT_DETAIL_FIELDS, tablename="product")


@action("product_detail/<product_id>", method=["GET", "POST"])
@action.uses(
    "htmx/form.html",
    session,
    db,
    auth.user,
)
def product_detail(product_id=None):
    product = db.product(product_id)
    if not product:
        ombott.abort(
            code=401,
            text="Could not retrieve product.  Please contact support.",
        )

    for field in db.product.fields:
        if field not in PRODUCT_DETAIL_FIELDS:
            db.product[field].readable = False

    db.product.id.readable = True

    attrs = {
        "_hx-get": URL("product_detail_edit/%s" % product_id),
        "_hx-target": "#details-target",
    }

    form = Form(
        db.product,
        record=product,
        readonly=True,
        deletable=False,
        formstyle=FormStyleBulma,
        dbio=False,
        submit_value="Edit",
        **attrs,
    )

    edit_button = BUTTON(
        I(_class="fa fa-edit"), _class="submit-edit box-shadow-y", **attrs
    )

    return dict(form=form, form_fields=PRODUCT_DETAIL_FIELDS, edit_button=edit_button)


@action(
    "product_detail_edit/<product_id>",
    method=["GET", "POST"],
)
@action.uses(
    "htmx/form.html",
    session,
    db,
    auth.user,
)
def product_detail_edit(product_id=None):
    product = db.product(product_id)
    if not product:
        ombott.abort(
            code=401,
            text="Could not retrieve product.  Please contact support.",
        )

    for field in db.product.fields:
        if field not in PRODUCT_DETAIL_FIELDS:
            db.product[field].readable = False
            db.product[field].writable = False

    db.product.id.readable = True

    attrs = {
        "_hx-post": URL("product_detail_edit/%s" % product_id),
        "_hx-target": "#details-target",
    }

    form = Form(
        db.product,
        record=product,
        formstyle=FormStyleBulma,
        **attrs,
    )

    attrs = {
        "_hx-get": URL("product_detail/%s" % product_id),
        "_hx-target": "#details-target",
        "_class": "button is-default",
    }
    form.param.sidecar.append(BUTTON("Cancel", **attrs))

    if form.accepted:
        redirect(URL("product_detail/%s" % product_id))

    return dict(form=form, form_fields=PRODUCT_DETAIL_FIELDS)


@action("product_orders", method=["POST", "GET"])
@action("product_orders/<path:path>", method=["POST", "GET"])
@action.uses(
    "htmx/grid.html",
    session,
    db,
    auth,
)
def product_orders(path=None):
    #  set the default
    product_id = get_parent(
        path,
        parent_field=db.order_detail.product,
    )

    query = db.order_detail.product == product_id

    gd = copy.deepcopy(GRID_DEFAULTS)
    gd["rows_per_page"] = 7

    grid = Grid(
        path,
        fields=[
            db.order.id,
            Column(
                "Order Date",
                represent=lambda row: row.order.order_date.strftime("%m/%d/%Y")
                if row.order.order_date
                else "",
                required_fields=[db.order.order_date],
            ),
            db.order.subtotal,
            db.order.freight,
            db.order.total,
        ],
        orderby=[~db.order.order_date, ~db.order.id],
        query=query,
        left=[db.order.on(db.order_detail.order == db.order.id)],
        show_id=True,
        auto_process=False,
        create=False,
        details=False,
        editable=False,
        deletable=False,
        include_action_button_text=False,
        **gd,
    )

    grid.attributes_plugin = AttributesPluginHtmx("#orders-target")
    grid.process()

    return dict(grid=grid)


@action("orders", method=["POST", "GET"])
@action("orders/<path:path>", method=["POST", "GET"])
@action.uses(
    "orders.html",
    session,
    db,
    auth.user,
)
def orders(path=None):
    search_queries = [
        GridSearchQuery(
            "Filter by Customer",
            lambda value: db.order.customer == value,
            requires=IS_NULL_OR(
                IS_IN_DB(
                    db(
                        db.customer.id.belongs(
                            db(db.order.id > 0)._select(
                                db.order.customer, distinct=True
                            )
                        )
                    ),
                    "customer.id",
                    "%(name)s",
                    zero="..",
                )
            ),
        ),
        GridSearchQuery(
            "Filter by Employee",
            lambda value: db.order.employee == value,
            requires=IS_NULL_OR(
                IS_IN_DB(
                    db(
                        db.employee.id.belongs(
                            db(db.order.id > 0)._select(
                                db.order.employee, distinct=True
                            )
                        )
                    ),
                    "employee.id",
                    "%(last_name)s, %(first_name)s",
                    zero="..",
                )
            ),
        ),
    ]

    queries = [(db.order.id > 0)]
    fields = [
        db.order.id,
        Column(
            "Ordered",
            represent=lambda row: row.order.order_date,
            required_fields=[db.order.order_date],
            orderby=[db.order.order_date],
        ),
        Column(
            "Customer",
            lambda row: XML(
                f"{row.customer.name}<br />{row.customer.address}<br />{row.customer.city}, {row.customer.region} {row.customer.postal_code}"
            ),
            orderby=db.customer.name,
            required_fields=[
                db.customer.name,
                db.customer.address,
                db.customer.city,
                db.customer.region,
                db.customer.postal_code,
            ],
        ),
        Column(
            "Deliver To",
            lambda row: XML(
                f"{row.order.ship_to_name}<br />{row.order.ship_to_address}<br />{row.order.ship_to_city}, {row.order.ship_to_region} {row.order.ship_to_postal_code}"
            ),
            required_fields=[
                db.order.ship_to_name,
                db.order.ship_to_address,
                db.order.ship_to_city,
                db.order.ship_to_region,
                db.order.ship_to_postal_code,
            ],
            orderby=db.order.ship_to_name,
        ),
        Column(
            "Sold By",
            lambda row: XML(
                f"{row.employee.first_name} {row.employee.last_name}<br />{row.employee.address}<br />{row.employee.city}, {row.employee.region} {row.employee.postal_code}"
            ),
            orderby=db.employee.last_name,
            required_fields=[
                db.employee.first_name,
                db.employee.last_name,
                db.employee.address,
                db.employee.city,
                db.employee.region,
                db.employee.postal_code,
            ],
        ),
        Column(
            "Required",
            represent=lambda row: row.order.required_date,
            required_fields=[db.order.required_date],
            orderby=[db.order.required_date],
        ),
        Column(
            "Shipped",
            represent=lambda row: row.order.shipped_date,
            required_fields=[db.order.shipped_date],
            orderby=[db.order.shipped_date],
        ),
    ]
    orderby = [~db.order.order_date]

    search = GridSearch(search_queries, queries)

    left = [
        db.customer.on(db.order.customer == db.customer.id),
        db.employee.on(db.order.employee == db.employee.id),
    ]

    gd = copy.deepcopy(GRID_DEFAULTS)
    gd["rows_per_page"] = 5

    grid = Grid(
        path,
        search.query,
        fields=fields,
        left=left,
        show_id=True,
        orderby=orderby,
        editable=False,
        search_form=search.search_form,
        auto_process=False,
        **gd,
    )

    grid.formatters_by_type["date"] = (
        lambda value: value.strftime("%m/%d/%Y") if value else ""
    )

    grid.param.details_submit_value = "Done"
    grid.process()

    parent_id = None
    order = None
    if grid.action in ["details", "edit"]:
        parent_id = grid.record_id
        order = db.order(parent_id)
    elif grid.action in ["new"]:
        redirect(URL("order_new"))

    return dict(grid=grid, parent_id=parent_id, order=order)


@action(
    "order_new",
    method=["GET", "POST"],
)
@action.uses(
    "order_new.html",
    session,
    db,
)
def order_new():
    db.order.id.readable = False

    form = Form(
        db.order,
        formstyle=FormStyleBulma,
    )

    attrs = {
        "_onclick": "window.history.back(); return false;",
        "_class": "button is-default",
    }
    form.param.sidecar.append(BUTTON("Cancel", **attrs))

    if form.accepted:
        redirect(URL("orders/details/%s" % form.vars["id"]))

    return dict(form=form, DETAIL_FIELDS=ORDER_DETAIL_FIELDS, tablename="order")


@action("order_detail/<order_id>", method=["GET", "POST"])
@action.uses(
    "htmx/form.html",
    session,
    db,
    auth.user,
)
def order_detail(order_id=None):
    order = db.order(order_id)
    if not order:
        ombott.abort(
            code=401,
            text="Could not retrieve order.  Please contact support.",
        )

    for field in db.order.fields:
        if field not in ORDER_DETAIL_FIELDS:
            db.order[field].readable = False

    db.order.id.readable = True

    attrs = {
        "_hx-get": URL("order_detail_edit/%s" % order_id),
        "_hx-target": "#details-target",
    }

    form = Form(
        db.order,
        record=order,
        readonly=True,
        deletable=False,
        formstyle=FormStyleBulma,
        dbio=False,
        submit_value="Edit",
        **attrs,
    )

    edit_button = BUTTON(
        I(_class="fa fa-edit"), _class="submit-edit box-shadow-y", **attrs
    )

    return dict(form=form, form_fields=ORDER_DETAIL_FIELDS, edit_button=edit_button)


@action(
    "order_detail_edit/<order_id>",
    method=["GET", "POST"],
)
@action.uses(
    "htmx/form.html",
    session,
    db,
    auth.user,
)
def order_detail_edit(order_id=None):
    order = db.order(order_id)
    if not order:
        ombott.abort(
            code=401,
            text="Could not retrieve order.  Please contact support.",
        )

    for field in db.order.fields:
        if field not in ORDER_DETAIL_FIELDS:
            db.order[field].readable = False
            db.order[field].writable = False

    db.order.id.readable = True

    attrs = {
        "_hx-post": URL("order_detail_edit/%s" % order_id),
        "_hx-target": "#details-target",
    }

    form = Form(
        db.order,
        record=order,
        formstyle=FormStyleBulma,
        **attrs,
    )

    attrs = {
        "_hx-get": URL("order_detail/%s" % order_id),
        "_hx-target": "#details-target",
        "_class": "button is-default",
    }
    form.param.sidecar.append(BUTTON("Cancel", **attrs))

    if form.accepted:
        redirect(URL("order_detail/%s" % order_id))

    return dict(form=form, form_fields=ORDER_DETAIL_FIELDS)


@action("order_details", method=["POST", "GET"])
@action("order_details/<path:path>", method=["POST", "GET"])
@action.uses(
    "htmx/grid.html",
    session,
    db,
    auth,
)
def order_details(path=None):
    #  set the default
    order_id = get_parent(
        path,
        parent_field=db.order_detail.order,
    )

    db.order_detail.order.default = order_id

    if path and path.split("/")[0] in ["new", "edit"]:
        db.order_detail.order.readable = False
        db.order_detail.order.writable = False

        db.order_detail.unit_price.writable = False

    query = db.order_detail.order == order_id
    left = [
        db.product.on((db.order_detail.product == db.product.id)),
    ]

    formstyle = FormStyleFactory()
    formstyle.classes = FormStyleBulma.classes
    formstyle.class_inner_exceptions = FormStyleBulma.class_inner_exceptions
    formstyle.widgets["product"] = HtmxAutocompleteWidget(
        simple_query=(db.product.id > 0)
    )

    grid = Grid(
        path,
        fields=[
            db.product.name,
            db.order_detail.unit_price,
            Column(
                "quantity",
                lambda row: row.order_detail.quantity,
                td_class_style="grid-cell-type-float",
                required_fields=[db.order_detail.quantity],
                orderby=db.order_detail.quantity,
            ),
            db.order_detail.discount,
        ],
        field_id=db.order_detail.id,
        query=query,
        left=left,
        orderby=[db.product.name, db.order_detail.quantity],
        auto_process=False,
        details=False,
        grid_class_style=GridClassStyleBulma,
        formstyle=formstyle,
        rows_per_page=10,
        include_action_button_text=False,
    )

    grid.attributes_plugin = AttributesPluginHtmx("#lines-target")
    attrs = {
        "_hx-get": URL(
            "order_details",
            vars=dict(parent_id=order_id),
        ),
        "_class": "button is-default",
    }
    grid.param.new_sidecar = BUTTON("Cancel", **attrs)
    grid.param.edit_sidecar = BUTTON("Cancel", **attrs)

    grid.process()

    parent_id = None
    order_detail = None
    if grid.action in ["new", "details", "edit"]:
        parent_id = grid.record_id
        order_detail = db.order_detail(parent_id)

    return dict(
        grid=grid,
        form_fields=ORDER_DETAIL_DETAIL_FIELDS,
        order_detail=order_detail,
        parent_id=parent_id,
    )
