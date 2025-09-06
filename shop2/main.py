from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import Session, select
from sqlalchemy import func


from models.model import *
from controlers.controler import *


def get_session():
    with Session(engine) as session:
        yield session


create_db_and_tables()

app = FastAPI()


@app.post("/admin/", response_model=AdminPub)
async def add_admin(user: User, session: Session = Depends(get_session)):
    user = AdminControler.save(user, session)
    return user


@app.get("/admin/{id}/", response_model=AdminPub)
async def get_admin(id: int, session: Session = Depends(get_session)):
    user = AdminControler.get_one(id, session)
    if user:
        return user
    raise HTTPException(status.HTTP_404_NOT_FOUND, "user with such id was not found")


@app.get("/admin/", response_model=list[AdminPub])
async def get_admins(
    offset: int = 0, limit: int = 2, session: Session = Depends(get_session)
):
    admins = AdminControler.get_all(offset=offset, limit=limit, session=session)
    if admins:
        return admins
    raise HTTPException(status.HTTP_404_NOT_FOUND, "there is no admin found")


@app.delete("/admin/{id}/")
async def delete_admin(id: int, session: Session = Depends(get_session)):
    message = AdminControler.delete(id, session)
    if message:
        return message
    return "admin was not deleted"


@app.post("/customer/")
async def add_customer(user: User, session: Session = Depends(get_session)):
    user = CustomerControler.save(user, session)
    return user


@app.get("/customer/{id}/")
async def get_customer(id: int, session: Session = Depends(get_session)):
    customer = CustomerControler.get_one(id, session)
    if customer:
        return customer
    raise HTTPException(
        status.HTTP_404_NOT_FOUND, f"customer with id {id} was not found"
    )


@app.get("/customer/", response_model=list[CustomerPub])
async def get_customers(
    offset: int = 0, limit: int = 30, session: Session = Depends(get_session)
):
    customers = CustomerControler.get_all(offset, limit, session)
    if customers:
        return customers
    raise HTTPException(status.HTTP_404_NOT_FOUND, "customers were not found")


@app.delete("/customer/{id}/")
async def delete_customer(id: int, session: Session = Depends(get_session)):
    message = CustomerControler.delete(id, session)
    if message:
        return message
    return "customer was not deleted"


@app.post("/customer/{id}/loan/", response_model=LoanPub)
async def add_loan(id: int, session: Session = Depends(get_session)):
    customer = CustomerControler.get_one(id, session)
    if not customer:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, "customer with that id was not found"
        )
    if customer.loan:
        raise HTTPException(status.HTTP_302_FOUND, "this customer already has loan")
    loan = LoanIn()
    loan2 = Loan.model_validate(loan)
    loan2.customer_id = id
    session.add(loan2)
    session.commit()
    session.refresh(loan2)
    return loan2


@app.get("/customer/{id}/loan", response_model=LoanPub)
async def get_customer_loan(id: int, session: Session = Depends(get_session)):
    customer = CustomerControler.get_one(id, session)
    if customer:
        return customer.loan
    raise HTTPException(
        status.HTTP_404_NOT_FOUND, f"no customer with id {id} was found"
    )


def create_sale(session: Session):
    sale = Sale()
    session.add(sale)
    session.commit()
    session.refresh(sale)
    return sale


@app.post("/sales/")
async def add_sale(session: Session = Depends(get_session)):
    date = datetime.now(timezone.utc).date()

    sale = session.exec(select(Sale).where(func.date(Sale.date) == date)).one_or_none()
    if sale:
        return sale

    sale = create_sale(session)
    return sale


@app.get("/sales", response_model=list[SalePub])
async def get_all_sales(
    offset: int = 0, limit: int = 40, session: Session = Depends(get_session)
):
    sales = SaleControler.get_all(offset, limit, session)
    if sales:
        return sales
    raise HTTPException(status.HTTP_404_NOT_FOUND, "no sales was found")


@app.get("/sales/{id}/", response_model=SalePub)
async def get_sale(id: int, session: Session = Depends(get_session)):
    sale = SaleControler.get_one(id, session)
    if sale:
        return sale
    raise HTTPException(status.HTTP_404_NOT_FOUND, f"sale with id {id} was not found")


@app.post("/sales/{id}/saleitems", response_model=list[SaleItemPub])
async def add_sale_items(
    sale_items: list[SaleItemIn], id: int, session: Session = Depends(get_session)
):
    sale = SaleControler.get_one(id, session)
    if sale:
        items = []
        for item in sale_items:
            product = ProductControler.get_one(item.product_id, session)
            if product is None:
                raise HTTPException(
                    status.HTTP_404_NOT_FOUND, f"product with id {id} was not found"
                )
            if product.stock > item.quantity:
                product.stock = product.stock - item.quantity
            else:
                raise HTTPException(
                    status.HTTP_406_NOT_ACCEPTABLE,
                    "you can not perform this opperation cause you have low stock",
                )
            item = SaleItem.model_validate(item)
            item.sale_id = sale.id
            sale.revenue += item.quantity * item.amount
            items.append(item)
        sitems = sale.saleitems
        items.extend(sitems)
        sale.saleitems = items
        session.add(sale)
        session.commit()
        session.refresh(sale)
        return sale.saleitems
    raise HTTPException(status.HTTP_404_NOT_FOUND, f"sale with id {id} was not found ")


@app.get("/sales/{id}/saleitems/", response_model=list[SaleItemPub])
async def get_all_sale_saleitem(id: int, session: Session = Depends(get_session)):
    sale = SaleControler.get_one(id, session)
    if sale:
        if sale.saleitems:
            return sale.saleitems
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, f"sale with id {id} has no sale items"
        )
    raise HTTPException(status.HTTP_404_NOT_FOUND, f"sale with id {id} was not found")


@app.post("/products/", response_model=ProductPub)
async def add_product(products: ProductsIn, session: Session = Depends(get_session)):
    product = session.exec(select(Product).where(Product.name == products.name)).all()
    if product:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail=f"can not create product {products.name} cause it already exists",
        )
    product = ProductControler.save(products, session)
    if product:
        return product
    raise HTTPException(status.HTTP_304_NOT_MODIFIED, "product was not created")


@app.get("/products/", response_model=list[ProductPub])
async def get_all_products(
    offset: int = 0, limit: int = 30, session: Session = Depends(get_session)
):
    products = ProductControler.get_all(offset, limit, session)
    if products:
        return products
    raise HTTPException(status.HTTP_404_NOT_FOUND, detail="no products were found")


@app.get("/products/{id}/", response_model=ProductPub)
async def get_product(id: int, session: Session = Depends(get_session)):
    product = ProductControler.get_one(id, session)
    if product:
        return product
    raise HTTPException(
        status.HTTP_404_NOT_FOUND, f"product with id {id} was not found"
    )


@app.put("/products/{id}/", response_model=ProductPub)
async def update_product(
    id: int, product: ProductsIn, session: Session = Depends(get_session)
):
    productdb = ProductControler.update(product, id, session)
    if productdb:
        return productdb
    raise HTTPException(
        status.HTTP_404_NOT_FOUND, f"product with id {id} was not found"
    )


@app.delete("/products/{id}/")
async def delete_product(id: int, session: Session = Depends(get_session)):
    product = ProductControler.get_one(id, session)
    if product:
        session.delete(product)
        return f"product {product.name} was deleted succesfull"
    raise HTTPException(
        status.HTTP_404_NOT_FOUND, f"product with id {id} was not found"
    )


@app.get("/loan/{id}/saleitems", response_model=list[SaleItemPub])
async def get_sell_items(id: int, session: Session = Depends(get_session)):
    loan = LoanControler.get_one(id, session)
    if loan:
        return loan.saleitems
    raise HTTPException(status.HTTP_404_NOT_FOUND, f"loan with id {id} was not found")


@app.post("/loan/{id}/saleitems/", response_model=list[SaleItemPub])
async def add_loan_sales(
    id: int, items: list[SaleItemIn], session: Session = Depends(get_session)
):
    loan = LoanControler.get_one(id, session)
    if not loan:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, f"loan with id {id} was not found"
        )
    sale = SaleControler.get_today_sale(session)
    if not sale:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "there is no sale")
    prev_loan_amount = loan.total
    total_revenue = 0
    itemdb = []
    for item in items:
        product = ProductControler.get_one(item.product_id, session)
        if not product:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                f"product with id {item.product_id} was not found",
            )
        if product.stock <= item.quantity:
            raise HTTPException(
                status.HTTP_406_NOT_ACCEPTABLE,
                f"you can not sell {item.quantity} {product.name} while there are {product.stock} in the stock",
            )
        product.stock -= item.quantity
        s_item = SaleItem.model_validate(item)
        s_item.product = product
        total_revenue += s_item.amount * s_item.quantity
        prev_loan_amount += s_item.amount * s_item.quantity
        itemdb.append(s_item)
    loan.saleitems.extend(itemdb)
    loan.total = total_revenue
    sale.saleitems.extend(itemdb)
    sale.revenue += total_revenue
    session.add(loan)
    session.commit()
    session.refresh(loan)
    return loan.saleitems


@app.post("/loan/{id}/pay/", response_model=list[PayItemPub])
async def add_payitem(
    id: int, payitems: list[PayItemIn], session: Session = Depends(get_session)
):
    loan = LoanControler.get_one(id, session)
    if not loan:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, f"loan with id {id} was not found"
        )
    items = []

    total_pay = 0
    for item in payitems:
        item = PayItem.model_validate(item)
        total_pay += item.amount
        items.append(item)

    loan.paid_amount += total_pay
    if loan.paid_amount > loan.total:
        raise HTTPException(
            status.HTTP_406_NOT_ACCEPTABLE,
            "you can not pay more that what you are supose to pay",
        )
    loan.payitems.extend(items)
    session.add(loan)
    session.commit()
    session.refresh(loan)
    return loan.payitems


# this should be modifyied to only return a single pay item
@app.get("/loan/{id}/pay/", response_model=list[PayItemPub])
async def get_payitems(id: int, session: Session = Depends(get_session)):
    loan = LoanControler.get_one(id, session)
    if loan:
        return loan.payitems
    raise HTTPException(status.HTTP_404_NOT_FOUND, f"loan with id {id} was not found")


@app.delete("/pay/{id}/")
async def delete_pay_item(id: int, session: Session = Depends(get_session)):
    pay = PayItemControler.get_one(id, session)
    if pay:
        session.delete(pay)
        return "pay item was deleted successfull"
    raise HTTPException(
        status.HTTP_404_NOT_FOUND, f"no pay item with id {id} was found"
    )


@app.put("/pay/{id}/", response_model=PayItemPub)
async def update_pay_item(
    id: int, model: PayItemIn, session: Session = Depends(get_session)
):
    pay = PayItemControler.update(id, model, session)
    return pay


@app.post("/purchase/", response_model=PurchasePub)
async def add_purchase(model: ParchaseIn, session: Session = Depends(get_session)):
    purchase = PurchaseControler.save(model, session)
    return purchase


@app.get("/purchase/", response_model=list[PurchasePub])
async def get_all_purchase(
    offset: int = 0, limit: int = 30, session: Session = Depends(get_session)
):
    purchases = PurchaseControler.get_all(offset, limit, session)
    return purchases


@app.get("/purchase/{id}/", response_model=PurchasePub)
async def get_purchase(id: int, session: Session = Depends(get_session)):
    purchase = PurchaseControler.get_one(id, session)
    return purchase


@app.put("/purchase/{id}/", response_model=PurchasePub)
async def update_purchase(
    id: int, model: ParchaseIn, session: Session = Depends(get_session)
):
    purchase = PurchaseControler.update(id, model, session)
    if purchase:
        return purchase
    raise HTTPException(status.HTTP_404_NOT_FOUND, "there is no purchase found")


@app.delete("/purchase/{id}/")
async def delete_purchase(id: int, session: Session = Depends(get_session)):
    purchase = PurchaseControler.get_one(id, session)
    if purchase:
        session.delete(purchase)
        return "successful"
    raise HTTPException(
        status.HTTP_404_NOT_FOUND, f"no purchase with id {id} was found"
    )


@app.post("/purchase/{id}/purchaseitem/", response_model=PurchaseItemPub)
async def add_purchase_items(
    id: int, items: list[PurchaseItemIn], session: Session = Depends(get_session)
):
    try:
        purchase_items = PurchaseItemControler.save_list(id, items, session)
        if not purchase_items:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, f"purchase with id {id} was not found"
            )
    except NotFound as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "some products were not found")


@app.get("/purchase/{id}/purchaseitem/")
async def get_purchase_items(id: int, session: Session = Depends(get_session)):
    items = PurchaseControler.get_one(id, session)
    if items:
        return items.purchaseitems
    raise HTTPException(
        status.HTTP_404_NOT_FOUND, f"purchase with id {id} was not found"
    )


@app.get("/purchaseitem/{id}", response_model=PurchaseItemPub)
async def get_purchase_item(id: int, session: Session = Depends(get_session)):
    item = PurchaseItemControler.get_one(id, session)
    if item:
        return item
    raise HTTPException(status.HTTP_404_NOT_FOUND, "purchase item not found")


# endpoints for expenses


@app.post("/expenses/", response_model=list[ExpensePub])
async def add_expenses(
    expenses: list[ExpenseIn], session: Session = Depends(get_session)
):
    items = ExpenseControler.save_list(expenses, session)
    return items


@app.get("/expenses/", response_model=list[ExpensePub])
async def get_expenses(
    offset: int = 0, limit: int = 30, session: Session = Depends(get_session)
):
    expenses = ExpenseControler.get_all(offset, limit, session)
    return expenses


@app.get("/expenses/{id}/", response_model=ExpensePub)
async def get_expense(id: int, session: Session = Depends(get_session)):
    expense = ExpenseControler.get_one(id, session)
    if expense:
        return expense
    raise HTTPException(status.HTTP_404_NOT_FOUND, "expense with that id was not found")


@app.put("/expenses/{id}/")
async def update_expense(id: int, expense: ExpenseIn, session):
    expensedb = ExpenseControler.get_one(id, session)
    if not expensedb:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "expense was not found")
    for k, v in expense.model_dump(exclude_unset=True).items():
        setattr(expensedb, k, v)
    session.add(expensedb)
    session.commit()
    session.refresh(expensedb)
    return expensedb


@app.delete("/expenses/{id}/")
async def delete_expense(id: int, session: Session = Depends(get_session)):
    expense = ExpenseControler.delete(id, session)
    if expense:
        return expense
    raise HTTPException(status.HTTP_404_NOT_FOUND, "expense with such id was not found")
