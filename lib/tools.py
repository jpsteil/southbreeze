import os
import sqlite3

from dateutil.parser import parse

from ..common import db

source_db = os.path.join(
    "/home", "jim", "dev", "northwind-SQLite3", "Northwind_large.sqlite"
)
conn = sqlite3.connect(source_db)
c = conn.cursor()


def region():
    db(db.sales_region.id > 0).delete()

    sql = "SELECT id, regionDescription FROM region"
    c.execute(sql)
    for region_nw, region_name in c.fetchall():
        db.sales_region.insert(nw=region_nw, name=region_name)


def territory():
    db(db.territory.id > 0).delete()

    sql = "SELECT id, territoryDescription, regionId FROM territory"
    c.execute(sql)
    for territory_nw, territory_name, sales_region_nw in c.fetchall():
        sales_region = db(db.sales_region.nw == sales_region_nw).select().first()

        if sales_region:
            db.territory.insert(
                nw=territory_nw, name=territory_name, sales_region=sales_region.id
            )


def category():
    db(db.category.id > 0).delete()

    sql = "SELECT id, categoryName, description FROM category"
    c.execute(sql)
    for category_nw, category_name, description in c.fetchall():
        db.category.insert(nw=category_nw, name=category_name, description=description)


def shipper():
    db(db.shipper.id > 0).delete()

    sql = "SELECT id, companyName, phone FROM shipper"
    c.execute(sql)
    for shipper_nw, shipper_name, phone in c.fetchall():
        db.shipper.insert(nw=shipper_nw, name=shipper_name, phone=phone)


def customer():
    db(db.customer.id > 0).delete()

    sql = "SELECT id, companyName, contactName, contactTitle, address, city, region, postalCode, country, phone from customer"
    c.execute(sql)

    for (
        customerId,
        companyName,
        contactName,
        contactTitle,
        address,
        city,
        region,
        postalCode,
        country,
        phone,
    ) in c.fetchall():
        db.customer.insert(
            nw=customerId,
            name=companyName,
            contact=contactName,
            title=contactTitle,
            address=address,
            city=city,
            region=region,
            postal_code=postalCode,
            country=country,
            phone=phone,
        )


def employee():
    db(db.employee.id > 0).delete()

    sql = (
        "SELECT id, lastName, firstName, title, titleOfCourtesy, birthDate, hireDate, address, city, "
        "region, postalCode, country, homePhone, extension, notes, reportsTo from employee"
    )
    c.execute(sql)

    xref = dict()
    supervisors = dict()
    for (
        nw,
        last_name,
        first_name,
        title,
        title_of_courtesy,
        birth_date,
        hire_date,
        address,
        city,
        region,
        postal_code,
        country,
        home_phone,
        extension,
        notes,
        reports_to,
    ) in c.fetchall():
        employee_id = db.employee.insert(
            nw=nw,
            last_name=last_name,
            first_name=first_name,
            title=title,
            title_of_courtesy=title_of_courtesy,
            birth_date=birth_date,
            hire_date=hire_date,
            address=address,
            city=city,
            region=region,
            postal_code=postal_code,
            country=country,
            phone=home_phone,
            extension=extension,
            notes=notes,
        )

        xref[nw] = employee_id
        supervisors[employee_id] = reports_to

    for employee_id in supervisors:
        emp = db.employee(employee_id)
        emp.update_record(supervisor=xref[int(emp.nw)])


def supplier():
    db(db.supplier.id > 0).delete()

    sql = (
        "SELECT id, companyName, contactName, contactTitle, address, city, region, "
        "postalCode, country, phone, fax, homePage FROM supplier"
    )
    c.execute(sql)

    for (
        nw,
        name,
        contact,
        title,
        address,
        city,
        region,
        postal_code,
        country,
        phone,
        fax,
        homepage,
    ) in c.fetchall():
        db.supplier.insert(
            nw=nw,
            name=name,
            contact=contact,
            title=title,
            address=address,
            city=city,
            region=region,
            postal_code=postal_code,
            country=country,
            phone=phone,
            homepage=homepage,
        )


def product():
    db(db.product.id > 0).delete()

    sql = (
        "SELECT id, productName, supplierId, categoryId, quantityPerUnit, unitPrice, unitsInStock, "
        "UnitsOnOrder, ReorderLevel, discontinued FROM product"
    )
    c.execute(sql)

    for (
        nw,
        name,
        supplier_nw,
        category_nw,
        quantity_per_unit,
        unit_price,
        in_stock,
        on_order,
        reorder_level,
        discontinued,
    ) in c.fetchall():
        supplier = db(db.supplier.nw == supplier_nw).select().first()
        category = db(db.category.nw == category_nw).select().first()

        db.product.insert(
            nw=nw,
            name=name,
            supplier=supplier.id if supplier else None,
            category=category.id if category else None,
            quantity_per_unit=quantity_per_unit,
            unit_price=unit_price,
            in_stock=in_stock,
            on_order=on_order,
            reorder_level=reorder_level,
            discontinued=discontinued,
        )


def order():
    db(db.order.id > 0).delete()

    sql = (
        "SELECT id, customerId, employeeId, orderDate, requiredDate, shippedDate, shipVia, freight, "
        "shipName, shipAddress, shipCity, ShipRegion, shipPostalCode, shipCountry FROM `order`"
    )
    c.execute(sql)

    for (
        nw,
        customer_nw,
        employee_nw,
        order_date,
        required_date,
        shipped_date,
        shipper_nw,
        freight,
        ship_to_name,
        ship_to_address,
        ship_to_city,
        ship_to_region,
        ship_to_postal_code,
        ship_to_country,
    ) in c.fetchall():
        customer = db(db.customer.nw == customer_nw).select().first()
        employee = db(db.employee.nw == employee_nw).select().first()
        shipper = db(db.shipper.nw == shipper_nw).select().first()

        order_date = parse(order_date).date() if order_date else None
        required_date = parse(required_date).date() if required_date else None
        shipped_date = parse(shipped_date).date() if shipped_date else None
        db.order.insert(
            nw=nw,
            customer=customer.id if customer else None,
            employee=employee.id if employee else None,
            order_date=order_date,
            required_date=required_date,
            shipped_date=shipped_date,
            shipper=shipper.id if shipper else None,
            freight=freight,
            ship_to_name=ship_to_name,
            ship_to_address=ship_to_address,
            ship_to_city=ship_to_city,
            ship_to_region=ship_to_region,
            ship_to_postal_code=ship_to_postal_code,
            ship_to_country=ship_to_country,
        )


def order_detail():
    db(db.order_detail.id > 0).delete()

    sql = (
        "SELECT id, orderId, productId, unitPrice, quantity, discount FROM orderDetail"
    )
    c.execute(sql)

    for nw, order_nw, product_nw, unit_price, quantity, discount in c.fetchall():
        order = db(db.order.nw == order_nw).select().first()
        product = db(db.product.nw == product_nw).select().first()

        db.order_detail.insert(
            nw=nw,
            order=order.id if order else None,
            product=product.id if product else None,
            unit_price=unit_price,
            quantity=quantity,
            discount=discount,
        )


def run():
    region()
    territory()
    category()
    shipper()
    customer()
    employee()
    supplier()
    product()
    order()
    order_detail()

    db.commit()
