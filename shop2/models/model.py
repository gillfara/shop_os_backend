from sqlmodel import SQLModel, Relationship, Field, create_engine
from datetime import datetime, timezone
from typing import Optional


# Admin model


class User(SQLModel):
    name: str
    phone: str | None
    password: str | None


class Admin(User, table=True):
    id: int | None = Field(default=None, primary_key=True)
    password: str


class AdminPub(User):
    id: int


# Customer model


class Customer(User, table=True):
    id: int | None = Field(default=None, primary_key=True)
    loan: Optional["Loan"] = Relationship(
        back_populates="customer", sa_relationship_kwargs={"uselist": False}
    )


class CustomerPub(User):
    id: int


# Sale model
class Sale(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    date: datetime = Field(default=datetime.now(timezone.utc))
    saleitems: list["SaleItem"] = Relationship(back_populates="sale")
    revenue: float = Field(default=0)


class SalePub(SQLModel):
    id: int
    date: datetime
    revenue: float


# SaleItem model
class SaleItemIn(SQLModel):
    product_id: int
    quantity: float
    amount: float


class SaleItem(SaleItemIn, table=True):
    id: int | None = Field(default=None, primary_key=True)
    sale_id: int | None = Field(default=None, foreign_key="sale.id")
    product_id: int | None = Field(default=None, foreign_key="product.id")
    loan_id: int | None = Field(default=None, foreign_key="loan.id")
    sale: Sale | None = Relationship(back_populates="saleitems")
    product: Optional["Product"] = Relationship(back_populates="saleitems")
    loan: Optional["Loan"] = Relationship(back_populates="saleitems")


class SaleItemPub(SaleItemIn):
    id: int
    product: "ProductSale"


# Product model
class ProductsIn(SQLModel):
    name: str
    buying_price: float
    selling_price: float
    stock: float
    units: str


class Product(ProductsIn, table=True):
    id: int | None = Field(default=None, primary_key=True)
    saleitems: list[SaleItem] = Relationship(back_populates="product")
    purchases: list["PurchaseItem"] = Relationship(back_populates="product")


class ProductSale(SQLModel):
    name: str


class ProductPub(ProductsIn):
    id: int


# Loan model
class LoanIn(SQLModel):
    total: float = Field(default=0)
    paid_amount: float = Field(default=0)


class Loan(LoanIn, table=True):
    id: int | None = Field(default=None, primary_key=True)
    customer_id: int | None = Field(default=None, foreign_key="customer.id")
    saleitems: list[SaleItem] = Relationship(back_populates="loan")
    payitems: list["PayItem"] = Relationship(back_populates="loan")
    customer: Customer | None = Relationship(back_populates="loan")


class LoanPub(LoanIn):
    id: int


# PayItem model


class PayItemIn(SQLModel):
    amount: float


class PayItem(PayItemIn, table=True):
    id: int | None = Field(default=None, primary_key=True)
    date: datetime = Field(default=datetime.now(timezone.utc))
    loan_id: int | None = Field(default=None, foreign_key="loan.id")
    loan: Optional["Loan"] = Relationship(back_populates="payitems")


class PayItemPub(PayItemIn):
    id: int
    date: datetime


# Purchase model
class ParchaseIn(SQLModel):
    amount: float


class Purchase(ParchaseIn, table=True):
    id: int | None = Field(default=None, primary_key=True)
    date: datetime = Field(default=datetime.now(timezone.utc))
    purchaseitems: list["PurchaseItem"] = Relationship(back_populates="purchase")


class PurchasePub(ParchaseIn):
    id: int
    date: datetime


# PurchaseItem model


class PurchaseItemIn(SQLModel):
    amount: float  # amount is the product price
    product_id: int
    quantity: float


class PurchaseItem(PurchaseItemIn, table=True):
    id: int | None = Field(default=None, primary_key=True)
    purchase_id: int | None = Field(default=None, foreign_key="purchase.id")
    purchase: Optional[Purchase] = Relationship(back_populates="purchaseitems")
    product_id: int | None = Field(default=None, foreign_key="product.id")
    product: Optional[Product] = Relationship(back_populates="purchases")


class PurchaseItemPub(PurchaseItemIn):
    id: int
    product: ProductSale


# Expenses model
class ExpenseIn(SQLModel):
    category: str
    description: str
    amount: float


class Expense(ExpenseIn, table=True):
    id: int | None = Field(default=None, primary_key=True)
    date: datetime = Field(default=datetime.now(timezone.utc))


class ExpensePub(ExpenseIn):
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
