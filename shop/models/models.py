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
    purchases: list["PurchaseTable"] = Relationship(back_populates="product")
    sales: list["SaleTable"] = Relationship(back_populates="product")
    loans: list["LoanTable"] = Relationship(back_populates="product")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ProductPub(Product):
    id: int


class Common(SQLModel):
    date: datetime = Field(default=datetime.now())
    quantity: float


class Sale(Common):
    pass


class SaleTable(Sale, table=True):
    id: int | None = Field(default=None, primary_key=True)
    product_id: int | None = Field(default=None, foreign_key="producttable.id")
    product: ProductTable | None = Relationship(back_populates="sales")


class Purchase(Common):
    pass


class PurchaseTable(Purchase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    product_id: int | None = Field(default=None, foreign_key="producttable.id")
    product: ProductTable | None = Relationship(back_populates="purchases")


class Loan(Common):
    pass


class LoanTable(Loan, table=True):
    id: int | None = Field(default=None, primary_key=True)
    customer_id: int | None = Field(default=None, foreign_key="customertable.id")
    customer: CustomerTable | None = Relationship(back_populates="loans")
    product_id: int | None = Field(default=None, foreign_key="producttable.id")
    product: ProductTable | None = Relationship(back_populates="loans")


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
    product_id: int | None = Field(default=None, foreign_key="producttable.id")
    product: ProductTable | None = Relationship(back_populates="inventories")


class InventoryPub(Inventory):
    id: int


# model for returning Product with invetory
class ProductInventory(ProductPub):
    inventories: InventoryPub | None


# fuction for initializing database

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":
    create_db_and_tables()
