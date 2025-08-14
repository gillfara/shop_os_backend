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


@app.post("/sales/", response_model=SalePub)
async def add_sale_item(
    products: list[ProductSale], session: Session = Depends(create_session)
):
    product_data = []
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
        product_data.append(data)
    sale = SaleTable(products=product_data)

    session.add(sale)
    session.commit()
    session.refresh(sale)
    return sale


@app.get("/sales/", response_model=list[SalePub])
async def get_all_sales(session: Session = Depends(create_session)):
    sales = session.exec(select(SaleTable).order_by(SaleTable.date.desc())).all()
    if not sales:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "there is no sale data found")
    return sales




# loan endpoints 

 