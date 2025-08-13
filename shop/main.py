from fastapi import FastAPI, Depends, HTTPException, status
from models import ProductTable, Product, ProductPub
from models import engine, create_db_and_tables
from sqlmodel import Session, select
from models.models import *

app = FastAPI()


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
async def get_product(id: int, session: Session = Depends(create_session)):
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
):
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
