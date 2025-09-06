from models.model import *
from sqlmodel import Session, select
from sqlalchemy import func
from fastapi import Depends
from datetime import datetime, timezone
import copy


class NotFound(Exception):
    pass


class AdminControler:
    @classmethod
    def save(cls, admin: User, session: Session):
        model = Admin.model_validate(admin)
        session.add(model)
        session.commit()
        session.refresh(model)
        return model

    @classmethod
    def get_all(cls, offset: int, limit: int, session: Session):
        query = select(Admin).offset(offset).limit(limit)
        admins = session.exec(query).all()
        return admins

    @classmethod
    def get_one(cls, id: int, session: Session):
        admin = session.get(Admin, id)
        return admin

    @classmethod
    def delete(cls, id: int, session: Session):
        admin = session.get(Admin, id)
        if admin:
            session.delete(admin)
            return "sucessful"
        return None


class CustomerControler:
    @classmethod
    def save(cls, model: User, session: Session):
        model = Customer.model_validate(model)
        session.add(model)
        session.commit()
        session.refresh(model)
        return model

    @classmethod
    def get_all(cls, offset: int, limit: int, session: Session):
        query = select(Customer).offset(offset).limit(limit)
        customers = session.exec(query)
        return customers.all()

    @classmethod
    def get_one(cls, id: int, session: Session):
        customer = session.get(Customer, id)
        return customer

    @classmethod
    def delete(cls, id: int, session: Session):
        customer = cls.get_one(id, session)
        if customer:
            session.delete(customer)
            return "successfull"
        return None


class SaleControler:
    @classmethod
    def save(cls, model: Sale, session: Session):
        model = Sale.model_validate(model)
        session.add(model)
        session.commit()
        session.refresh(model)
        return model

    @classmethod
    def get_all(cls, offset: int, limit: int, session: Session):
        query = select(Sale).offset(offset).limit(limit)
        sales = session.exec(query).all()
        return sales

    @classmethod
    def get_one(cls, id: int, session: Session):
        sale = session.get(Sale, id)
        return sale

    @classmethod
    def get_today_sale(cls, session: Session):
        today = datetime.now(timezone.utc)
        sale = session.exec(
            select(Sale).where(func.date(Sale.date) == today.date())
        ).one_or_none()
        return sale

    @classmethod
    def delete(cls, id: int, session: Session):
        sale = cls.get_one(id, session)
        if sale:
            return "successfull"
        return None


class ProductControler:
    @classmethod
    def save(cls, model: ProductsIn, session: Session):
        model = Product.model_validate(model)
        session.add(model)
        session.commit()
        session.refresh(model)
        return model

    @classmethod
    def get_all(cls, offset: int, limit: int, session: Session):
        products = session.exec(select(Product).offset(offset).limit(limit)).all()
        return products

    @classmethod
    def get_one(cls, id: int, session: Session):
        product = session.get(Product, id)
        return product

    @classmethod
    def get_by_name(cls, name: str, session: Session):
        product = session.exec(select(Product).where(Product.name == name)).all()
        if product:
            return True
        return False

    @classmethod
    def update(cls, model: ProductsIn, id: int, session: Session):
        productdb = cls.get_one(id, session)
        if not productdb:
            return None

        product_stock = productdb.stock

        for k, v in model.model_dump().items():
            setattr(productdb, k, v)
        productdb.stock += product_stock
        session.add(productdb)
        session.commit()
        session.refresh(productdb)
        return productdb

    @classmethod
    def delete(cls, id: int, session: Session):
        product = cls.get_one(id, session)
        if product:
            session.delete(product)
            return "success"
        return None


class LoanControler:
    @classmethod
    def save(cls, model: LoanIn, session: Session):
        loan = Loan.model_validate(model)
        session.add(loan)
        session.commit()
        session.refresh(loan)
        return loan

    @classmethod
    def get_all(cls, offset: int, limit: int, session: Session):
        loans = session.exec(select(Loan).offset(offset).limit(limit)).all()
        return loans

    @classmethod
    def get_one(cls, id: int, session: Session):
        loan = session.get(Loan, id)
        return loan

    @classmethod
    def delete(cls, id: int, session: Session):
        loan = cls.get_one(id, session)
        if loan:
            session.delete(loan)
            return "deleted successful"
        return None


class PayItemControler:
    @classmethod
    def save(cls, model: PayItem, session: Session):
        pay = PayItem.model_validate(model)
        session.add(pay)
        session.commit()
        session.refresh(pay)
        return pay

    @classmethod
    def get_all(cls, offset: int, limit: int, session: Session):
        payitems = session.exec(select(PayItem).offset(offset).limit(limit)).all()
        return payitems

    @classmethod
    def get_one(cls, id: int, session: Session):
        payitem = session.get(PayItem, id)
        return payitem

    @classmethod
    def update(cls, id: int, model: PayItemIn, session: Session):
        pay = cls.get_one(id, session)
        if not pay:
            return None
        for k, v in model.model_dump(exclude_unset=True).items():
            setattr(pay, k, v)
        session.add(pay)
        session.commit()
        session.refresh(pay)
        return pay

    @classmethod
    def delete(cls, id: int, session: Session):
        payitem = cls.get_one(id, session)
        if payitem:
            session.delete(payitem)
            return "successful deleted"
        return None


class PurchaseControler:
    @classmethod
    def save(cls, model: ParchaseIn, session: Session):
        purchase = Purchase.model_validate(model)
        session.add(purchase)
        session.commit()
        session.refresh(purchase)
        return purchase

    @classmethod
    def get_all(cls, offset: int, limit: int, session: Session):
        purchases = session.exec(select(Purchase).offset(offset).limit(limit)).all()
        return purchases

    @classmethod
    def get_one(cls, id: int, session: Session):
        purchase = session.get(Purchase, id)
        return purchase

    @classmethod
    def update(cls, id: int, model: ParchaseIn, session):
        purchase = cls.get_one(id, session)
        if not purchase:
            return None
        for k, v in model.model_dump(exclude_unset=True).items():
            setattr(purchase, k, v)
        session.add(purchase)
        session.commit()
        session.refresh(purchase)
        return purchase

    @classmethod
    def delete(cls, id: int, session: Session):
        purchase = cls.get_one(id, session)
        if purchase:
            session.delete(purchase)
            return "successful"
        return None


class PurchaseItemControler:
    @classmethod
    def save(cls, model: PurchaseItemIn, session: Session):
        item = PurchaseItem.model_validate(model)
        session.add(item)
        session.commit()
        session.refresh(item)
        return item

    @classmethod
    def save_list(cls, purchase_id: int, items: list[PurchaseItemIn], session: Session):
        purchase = PurchaseControler.get_one(purchase_id, session)
        if not purchase:
            return None
        for item in items:
            product = ProductControler.get_one(item.product_id, session)
            if not product:
                raise NotFound(f"product with id {id} not found")
            item = PurchaseItem.model_validate(item)
            product.stock += item.quantity
            item.purchase_id = purchase_id
            session.add(item)
        session.commit()

        return purchase.purchaseitems

    @classmethod
    def get_one(cls, id: int, session: Session):
        item = session.get(PurchaseItem, id)
        return item

    def get_all(cls, offset: int, limit: int, session: Session):
        items = session.exec(select(PurchaseItem).offset(offset).limit(limit)).all()
        return items

    def delete(cls, id: int, session: Session):
        item = cls.get_one(id, session)
        if item:
            session.delete(item)
            return "successful"
        return None


class ExpenseControler:
    @classmethod
    def save(cls, model: Expense, session: Session):
        expense = Expense.model_validate(model)
        session.add(expense)
        session.commit()
        session.refresh(expense)
        return expense

    @classmethod
    def save_list(cls, items: list[ExpenseIn], session: Session):
        dbitem = []
        for item in items:
            item = Expense.model_validate(item)
            dbitem.append(item)
            session.add(item)
        session.commit()
        for item in dbitem:
            session.refresh(item)
        return dbitem

    @classmethod
    def get_all(cls, offset: int, limit: int, session: Session):
        expense = session.exec(select(Expense).offset(offset).limit(limit)).all()
        return expense

    @classmethod
    def get_one(cls, id: int, session: Session):
        expense = session.get(Expense, id)
        return expense

    @classmethod
    def update(cls, id: int, model: ExpenseIn, session: Session):
        expense = cls.get_one(id, session)
        for k, v in model.model_dump(exclude_unset=True).items():
            setattr(expense, k, v)
        session.add(expense)
        session.commit()
        session.refresh(expense)
        return expense

    @classmethod
    def delete(cls, id: int, session: Session):
        expense = cls.get_one(id, session)
        if expense:
            session.delete(expense)
            return "successful"
        return None
