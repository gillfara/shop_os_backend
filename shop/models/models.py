from sqlmodel import SQLModel, Session, Field, Relationship, create_engine
from datetime import datetime, UTC
from enum import StrEnum
from typing import Optional


class Unit(StrEnum):
    kg = "KG"
    pc = "PC"
    lt = "LT"


# User models


class User(SQLModel):
    name: str
    phone: str | None = Field(default=None)


class Admin(User):
    password: str


class AdminTable(Admin, table=True):
    id: int | None = Field(default=None, primary_key=True)


class CustomerTable(User, table=True):
    id: int | None = Field(default=None, primary_key=True)
    pays: list["PayTable"] = Relationship(back_populates="customer")
    loans: list["LoanTable"] = Relationship(back_populates="customer")


class Product(SQLModel):
    name: str
    buying_price: float
    selling_price: float


class ProductTable(Product, table=True):
    id: int | None = Field(default=None, primary_key=True)
    inventories: Optional["InventoryTable"] = Relationship(
        back_populates="product", sa_relationship_kwargs={"uselist": False}
    )
    purchase_id: int | None = Field(default=None, foreign_key="purchasetable.id")
    purchases: Optional["PurchaseTable"] = Relationship(back_populates="products")
    bill: list["BillTable"] = Relationship(
        back_populates="product",
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ProductSale(SQLModel):
    name: str
    quantity: float


class ProductSalePub(SQLModel):
    name: str
    selling_price: float


class ProductPub(Product):
    id: int


class ProductPurchase(Product):
    """return a product with its inventory"""

    inventories: "Inventory"


class Common(SQLModel):
    date: datetime = Field(default=datetime.now())
    quantity: float


class Sale(SQLModel):
    date: datetime = Field(default=datetime.now())


class SaleTable(Sale, table=True):
    id: int | None = Field(default=None, primary_key=True)
    bills: list["BillTable"] = Relationship(back_populates="sale")
    loan_id: int | None = Field(default=None, foreign_key="loantable.id")
    loan: Optional["LoanTable"] = Relationship(back_populates="sales")


class SalePub(Sale):
    id: int
    bills: list["BillPub"]


class Purchase(SQLModel):
    date: datetime = Field(default=datetime.now())


class PurchaseTable(Purchase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    products: list[ProductTable] = Relationship(back_populates="purchases")


class LoanTable(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    customer_id: int | None = Field(default=None, foreign_key="customertable.id")
    customer: CustomerTable | None = Relationship(back_populates="loans")
    sales: list[SaleTable] = Relationship(back_populates="loan")


class LoanPub(SQLModel):
    customer: User
    sales: list[SalePub]


class Pay(Common):
    pass


class PayTable(Pay, table=True):
    id: int | None = Field(default=None, primary_key=True)
    customer_id: int | None = Field(default=None, foreign_key="customertable.id")
    customer: CustomerTable | None = Relationship(back_populates="pays")


class Inventory(SQLModel):
    quantity: float
    units: Unit = Field(default=Unit.pc)


class InventoryTable(Inventory, table=True):
    id: int | None = Field(default=None, primary_key=True)
    stock: float
    product_id: int | None = Field(default=None, foreign_key="producttable.id")
    product: ProductTable | None = Relationship(back_populates="inventories")


class InventoryPub(Inventory):
    """return id and stock of an inventory"""

    id: int
    stock: int


class BillTable(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    quantity: int
    product_id: int | None = Field(default=None, foreign_key="producttable.id")
    product: ProductTable | None = Relationship(back_populates="bill")
    sale_id: int | None = Field(default=None, foreign_key="saletable.id")
    sale: SaleTable | None = Relationship(back_populates="bills")


class BillPub(SQLModel):
    product: ProductSalePub | None
    quantity: int


# pydantic  model for returning Product with invetory
class ProductInventory(ProductPub):
    inventories: InventoryPub | None


class ProductInventoryIn(Product):
    inventories: Inventory | None


# pydantic model for returning Purchase with products
class PurchaseProduct(SQLModel):
    """return a list of product  in  purchase  object"""

    products: list[ProductPurchase]


class PurchasePub(PurchaseProduct):
    """return a purchase object"""

    id: int
    date: datetime


# fuction for initializing database

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":
    create_db_and_tables()
