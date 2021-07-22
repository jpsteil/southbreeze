"""
This file defines the database models
"""
import datetime
from decimal import Decimal, ROUND_HALF_UP

from dateutil.parser import parse

from .common import db, Field
from pydal.validators import *


db.define_table(
    "sales_region",
    Field("nw", readable=False, writable=False),
    Field("name", length=50, required=True, requires=IS_NOT_EMPTY()),
)

db.define_table(
    "territory",
    Field("nw", readable=False, writable=False),
    Field("name", required=True, requires=IS_NOT_EMPTY()),
    Field(
        "sales_region",
        "reference sales_region",
        requires=IS_IN_DB(db, "sales_region.id", "%(name)s", zero=".."),
    ),
)

db.define_table(
    "customer",
    Field("nw", readable=False, writable=False),
    Field("name", length=40, required=True, requires=IS_NOT_EMPTY()),
    Field("contact", length=30),
    Field("title", length=30),
    Field("address", length=60),
    Field("city", length=15),
    Field("region", length=15),
    Field("postal_code", length=10),
    Field("country", length=15),
    Field("phone", length=24),
    Field("email", length=256, requires=IS_NULL_OR(IS_EMAIL())),
)

db.define_table(
    "customer_note",
    Field(
        "customer",
        "reference customer",
        requires=IS_IN_DB(db, "customer.id", "%(name)s", zero=".."),
    ),
    Field(
        "timestamp",
        "datetime",
        requires=IS_DATETIME(),
        default=lambda: datetime.datetime.now(),
    ),
    Field("note", "text", requires=IS_NOT_EMPTY()),
)

db.define_table(
    "shipper",
    Field("nw", readable=False, writable=False),
    Field("name", length=40, required=True, requires=IS_NOT_EMPTY()),
    Field("phone", length=24),
    format=lambda row: row.name if row else "",
)

db.define_table(
    "supplier",
    Field("nw", readable=False, writable=False),
    Field("name", length=40, required=True, requires=IS_NOT_EMPTY()),
    Field("contact", length=30),
    Field("title", length=30),
    Field("address", length=60),
    Field("city", length=15),
    Field("region", length=15),
    Field("postal_code", length=10),
    Field("country", length=15),
    Field("phone", length=24),
    Field("email", length=256, requires=IS_NULL_OR(IS_EMAIL())),
    Field("homepage", "text"),
    Field(
        "sales_region",
        "reference sales_region",
        requires=IS_IN_DB(db, "sales_region.id", "%(name)s", zero=".."),
    ),
    format=lambda row: row.name if row else "",
)

db.define_table(
    "category",
    Field("nw", readable=False, writable=False),
    Field("name", length=15, required=True, requires=IS_NOT_EMPTY()),
    Field("description", "text"),
    Field("picture"),
    format=lambda row: row.name if row else "",
)

db.define_table(
    "product",
    Field("nw", readable=False, writable=False),
    Field("name", length=40, required=True, requires=IS_NOT_EMPTY()),
    Field(
        "supplier",
        "reference supplier",
        requires=IS_IN_DB(db, "supplier.id", "%(name)s", zero=".."),
        comment="The organization where we purchase this product",
    ),
    Field(
        "category",
        "reference category",
        requires=IS_IN_DB(db, "category.id", "%(name)s", zero=".."),
    ),
    Field("quantity_per_unit", length=20),
    Field("unit_price", "decimal(11,2)"),
    Field("in_stock", "integer"),
    Field("on_order", "integer"),
    Field("reorder_level", "integer"),
    Field("discontinued", "boolean", default=False),
)

db.define_table(
    "employee",
    Field("nw", readable=False, writable=False),
    Field("last_name", length=20, required=True, requires=IS_NOT_EMPTY()),
    Field("first_name", length=10, required=True, requires=IS_NOT_EMPTY()),
    Field("title", length=30),
    Field("title_of_courtesy", length=25),
    Field("birth_date", "date", requires=IS_DATE()),
    Field("hire_date", "date", requires=IS_DATE()),
    Field("address", length=60),
    Field("city", length=15),
    Field("region", length=15),
    Field("postal_code", length=10),
    Field("country", length=15),
    Field("phone", length=24),
    Field("extension", length=4),
    Field("photo"),
    Field("notes", "text"),
    Field(
        "supervisor",
        "reference employee",
        requires=IS_NULL_OR(
            IS_IN_DB(db, "employee.id", "%(last_name)s, %(first_name)s", zero="..")
        ),
        represent=lambda r: f"{r.first_name} {r.last_name}" if r else "",
    ),
    Field(
        "sales_region",
        "reference sales_region",
        requires=IS_IN_DB(db, "sales_region.id", "%(name)s", zero=".."),
        represent=lambda r: f"{r.name}" if r else "",
    ),
)

db.define_table(
    "customer_type",
    Field("nw", readable=False, writable=False),
    Field("name", required=True, requires=IS_NOT_EMPTY()),
)

db.define_table(
    "customer_customer_type",
    Field("nw", readable=False, writable=False),
    Field(
        "customer",
        "reference customer",
        requires=IS_IN_DB(db, "customer.id", "%(name)s", zero=".."),
    ),
    Field(
        "customer_type",
        "reference customer_type",
        requires=IS_IN_DB(db, "customer_type.id", "%(name)s", zero=".."),
    ),
)

db.define_table(
    "employee_territory",
    Field("nw", readable=False, writable=False),
    Field(
        "employee",
        "reference employee",
        requires=IS_IN_DB(
            db, "employee.id", "%(last_name)s, %(first_name)s", zero=".."
        ),
    ),
    Field(
        "territory",
        "reference territory",
        requires=IS_IN_DB(db, "territory.id", "%(name)s", zero=".."),
    ),
)

db.define_table(
    "order",
    Field("nw", readable=False, writable=False),
    Field(
        "customer",
        "reference customer",
        requires=IS_IN_DB(db, "customer.id", "%(name)s", zero=".."),
        represent=lambda row: row.name if row else "",
    ),
    Field(
        "employee",
        "reference employee",
        requires=IS_IN_DB(
            db, "employee.id", "%(last_name)s, %(first_name)s", zero=".."
        ),
        represent=lambda row: f"{row.first_name} {row.last_name}" if row else "",
    ),
    Field(
        "order_date",
        "date",
        requires=IS_DATE(),
        represent=lambda x: parse(x).strftime("%m/%d/%Y")
        if x and isinstance(x, str)
        else "",
    ),
    Field(
        "required_date",
        "date",
        requires=IS_DATE(),
        represent=lambda x: parse(x).strftime("%m/%d/%Y")
        if x and isinstance(x, str)
        else "",
    ),
    Field(
        "shipped_date",
        "date",
        requires=IS_NULL_OR(IS_DATE()),
        represent=lambda x: parse(x).strftime("%m/%d/%Y")
        if x and isinstance(x, str)
        else "",
    ),
    Field(
        "shipper",
        "reference shipper",
        requires=IS_NULL_OR(IS_IN_DB(db, "shipper.id", "%(name)s", zero="..")),
        represent=lambda row: f"{row.name}" if row else "",
    ),
    Field("freight", "decimal(11,2)"),
    Field("ship_to_name", length=40),
    Field("ship_to_address", length=60),
    Field("ship_to_city", length=15),
    Field("ship_to_state", length=2),
    Field("ship_to_region", length=15),
    Field("ship_to_postal_code", length=10),
    Field("ship_to_country", length=15),
    Field.Virtual(
        "subtotal",
        lambda o: order_subtotal(o) if "id" in o else 0,
    ),
    Field.Virtual(
        "total",
        lambda o: order_total(o) if "id" in o else 0,
    ),
)

db.define_table(
    "order_detail",
    Field("nw", readable=False, writable=False),
    Field("order", "reference order", requires=IS_IN_DB(db, "order.id")),
    Field(
        "product",
        "reference product",
        requires=IS_IN_DB(db, "product.id", "%(name)s", zero=".."),
    ),
    Field("unit_price", "decimal(11,2)"),
    Field("quantity", "integer"),
    Field("discount", "decimal(11,2)", default=0),
)


#  add callback functions
def order_detail_before_update(fields):
    if "product" in fields:
        product_id = fields["product"]
        product = db.product(product_id)
        if product:
            fields["unit_price"] = product.unit_price


db.order_detail._before_insert.append(lambda f: order_detail_before_update(f))
db.order_detail._before_update.append(lambda s, f: order_detail_before_update(f))


def order_subtotal(row):
    price = 0

    row_id = row["id"] if "id" in row else row.order["id"] if "order" in row else None

    price = 0

    if row_id:
        for od in db(db.order_detail.order == row_id).select():
            price += Decimal(od.unit_price).quantize(
                Decimal("0.00"), rounding=ROUND_HALF_UP
            ) * Decimal(od.quantity).quantize(Decimal("0.00"), rounding=ROUND_HALF_UP)

    return Decimal(price).quantize(Decimal("0.00"), rounding=ROUND_HALF_UP)


def order_total(row):
    total = 0

    subtotal = order_subtotal(row)
    freight = (
        row["freight"]
        if "freight" in row
        else db.order(row["id"])["freight"]
        if "id" in row
        else 0
    )
    total = Decimal(subtotal).quantize(
        Decimal("0.00"), rounding=ROUND_HALF_UP
    ) + Decimal(freight).quantize(Decimal("0.00"), rounding=ROUND_HALF_UP)

    return Decimal(total).quantize(Decimal("0.00"), rounding=ROUND_HALF_UP)


db.commit()
