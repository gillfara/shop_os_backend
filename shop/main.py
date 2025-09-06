from typing import Sequence
from fastapi import FastAPI, Depends, HTTPException, status
from models import ProductTable, Product, ProductPub
from models import engine, create_db_and_tables
from sqlmodel import Session, select
from models.models import *
from models.models import SaleTable
from models.models import CustomerTable
from models.models import PurchaseTable
from models.models import LoanTable
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)


async def create_session():
    with Session(engine) as session:
        yield session


create_db_and_tables()


# products endpoints
@app.post("/products/", response_model=ProductPub)
async def save_product(
    product: ProductPurchase, session: Session = Depends(create_session)
):
    inventory = InventoryTable.model_validate(product.inventories)
    product.inventories = inventory
    product_data = ProductTable.model_validate(product)
    session.add(product_data)
    session.commit()
    session.refresh(product_data)
    return product_data


@app.get("/products/", response_model=list[ProductInventory])
async def get_all_products(session: Session = Depends(create_session)):
    seen = set()
    products = session.exec(
        select(ProductTable).order_by(ProductTable.created_at.desc())
    ).all()
    productsout = []

    for product in products:
        if product.name not in seen:
            productsout.append(product)
            seen.add(product.name)

    return productsout


@app.get("/products/{id}", response_model=ProductInventory)
async def get_product(
    id: int, session: Session = Depends(create_session)
) -> ProductTable:
    product = session.get(ProductTable, id)
    if not product:
        raise HTTPException(404, "not found")
    return product


@app.post("/products/{product_id}/inventories/", response_model=InventoryPub)
async def add_product_inventory(
    product_id: int, inventory: Inventory, session: Session = Depends(create_session)
):
    product = session.get(ProductTable, product_id)
    if not product:
        raise HTTPException(404, "no product with such id was found")
    if product.inventories:
        raise HTTPException(
            status.HTTP_406_NOT_ACCEPTABLE,
            "product can not have more than one inventory",
        )
    dbinventory = InventoryTable.model_validate(inventory)
    dbinventory.product = product
    session.add(dbinventory)
    session.commit()
    session.refresh(dbinventory)
    return dbinventory


@app.get("/products/{product_id}/inventories/", response_model=InventoryPub)
async def get_product_inventory(
    product_id: int, session: Session = Depends(create_session)
):
    product = session.get(ProductTable, product_id)
    if not product:
        raise HTTPException(404, "product with such id was not found")
    if not product.inventories:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, "inventory for this product was not found"
        )
    return product.inventories


# purchase endpoints


@app.post("/purchases/", response_model=PurchasePub)
async def add_purchases_item(
    purchase: PurchaseProduct, session: Session = Depends(create_session)
) -> PurchaseTable:
    productm = []
    for product in purchase.products:
        prodresuslt = session.exec(
            select(ProductTable)
            .where(ProductTable.name == product.name)
            .order_by(ProductTable.created_at.desc())
        ).all()
        if prodresuslt:
            prev_stock = prodresuslt[0].inventories.stock
        else:
            prev_stock = 0
        product.inventories = InventoryTable.model_validate(
            {**product.inventories.model_dump(), "stock": product.inventories.quantity}
        )
        product.inventories.stock = product.inventories.stock + prev_stock
        prod = ProductTable.model_validate(product)
        productm.append(prod)

    purchasedb = purchase
    purchasedb.products = productm
    purchasedb = PurchaseTable.model_validate(purchase)
    purchasedb.products = productm

    session.add(purchasedb)
    session.commit()
    session.refresh(purchasedb)
    return purchasedb


@app.get("/purchases/", response_model=list[PurchasePub])
async def get_all_purchases(session: Session = Depends(create_session)):
    purchases = session.exec(
        select(PurchaseTable).order_by(PurchaseTable.date.desc())
    ).all()
    return purchases


@app.get("/purchases/{id}", response_model=PurchasePub)
async def get_purchase(id: int, session: Session = Depends(create_session)):
    purchase = session.get(PurchaseTable, id)
    if not purchase:
        raise HTTPException(404, "purchase with such id was not found")
    return purchase


@app.get("/purchases/{id}/products", response_model=PurchaseProduct)
async def get_purchase_products(id: int, session: Session = Depends(create_session)):
    purchase = session.get(PurchaseTable, id)
    if not purchase:
        raise HTTPException(404, "purchase with such id was not found")
    return purchase


@app.get("/purchases/{id}/products/{product_id}", response_model=ProductPurchase)
async def get_purchase_product(
    id: int, product_id: int, session: Session = Depends(create_session)
):
    purchase = session.get(PurchaseTable, id)
    if not purchase:
        raise HTTPException(404, "purchase with such id was not found")
    product = next((p for p in purchase.products if p.id == product_id), None)
    if not product:
        raise HTTPException(404, "product with such id was not found in this purchase")
    return product


@app.delete("/purchases/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_purchase(id: int, session: Session = Depends(create_session)):
    purchase = session.get(PurchaseTable, id)
    if not purchase:
        raise HTTPException(404, "purchase with such id was not found")
    session.delete(purchase)
    session.commit()
    return {"message": "Purchase deleted successfully"}


# endpionts for sales


def prepare_sale(products, session) -> SaleTable:
    """This is a helper fuction for preparing SaleTable before it  can be saved"""
    bills = []
    for product in products:
        data = session.exec(
            select(ProductTable)
            .where(ProductTable.name == product.name)
            .order_by(ProductTable.created_at.desc())
        ).all()
        print(data)
        if data:
            data = data[0]
            if data.inventories.stock > product.quantity:
                data.inventories.stock = data.inventories.stock - product.quantity
            else:
                raise HTTPException(
                    status.HTTP_406_NOT_ACCEPTABLE,
                    "there is no enough stock to perform this operation",
                )
        else:
            raise HTTPException(
                status.HTTP_406_NOT_ACCEPTABLE,
                f"you can not sell product {product.name} as it was not found",
            )
        bills.append(BillTable(quantity=product.quantity, product=data))
    sale = SaleTable(bills=bills)
    return sale


@app.post("/sales/", response_model=SalePub)
async def add_sale_item(
    products: list[ProductSale], session: Session = Depends(create_session)
) -> SaleTable:
    sale = prepare_sale(products, session)
    session.add(sale)
    session.commit()
    session.refresh(sale)
    return sale


@app.get("/sales/", response_model=list[SalePub])
async def get_all_sales(
    session: Session = Depends(create_session),
) -> Sequence[SaleTable]:
    sales = session.exec(select(SaleTable).order_by(SaleTable.date.desc())).all()
    if not sales:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "there is no sale data found")
    return sales


# Customer endpoints
@app.post("/customers", response_model=User)
async def add_customer(
    user: User, session: Session = Depends(create_session)
) -> CustomerTable:
    customer = CustomerTable.model_validate(user)
    session.add(customer)
    session.commit()
    session.refresh(customer)
    return customer


@app.get("/customers/", response_model=list[User])
async def get_all_customers(
    session: Session = Depends(create_session),
) -> Sequence[CustomerTable]:
    customers = session.exec(select(CustomerTable)).all()
    if not customers:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "there are no customers found")
    return customers


# loan endpoints
@app.post("/loans", response_model=LoanPub)
async def add_loan(
    products: list[ProductSale],
    user_id: int,
    session: Session = Depends(create_session),
):
    customer = session.get(CustomerTable, user_id)
    if not customer:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "customer was not found")
    # check if there is loan with that customer if there is do not create loan raise error
    loan = session.exec(
        select(LoanTable).where(LoanTable.customer_id == user_id)
    ).one_or_none()
    if loan:
        loan.sales.append(prepare_sale(products, session))
    else:
        sale: SaleTable = prepare_sale(products, session)
        loan = LoanTable(customer=customer, sales=[sale])
    session.add(loan)
    session.commit()
    session.refresh(loan)
    return loan


@app.get("/loans", response_model=LoanPub)
def get_all_loan(
    user_id: int, session: Session = Depends(create_session)
) -> Sequence[LoanTable]:
    print(user_id)
    customer = session.get(CustomerTable, user_id)
    print(customer)
    if not customer:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, "there is no such customer found"
        )
    loan = session.exec(
        select(LoanTable).where(LoanTable.customer == customer)
    ).one_or_none()
    if not loan:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "this customer has no loan")
    # print(loan.sales)
    return loan


if __name__ == "__main__":
    config = uvicorn.Config("main:app", host="127.0.0.1", port=8000, log_level="info")
    server = uvicorn.Server(config)
    server.run()
