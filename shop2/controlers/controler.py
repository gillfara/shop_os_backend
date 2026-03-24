import copy
from datetime import date, datetime, timezone

from fastapi import Depends
from models.model import *
from sqlalchemy import func
from sqlmodel import Session, select


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
            session.commit()
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
    def update(cls, id: int, model: User, session: Session):
        customer = session

    @classmethod
    def delete(cls, id: int, session: Session):
        customer = cls.get_one(id, session)
        if customer:
            session.delete(customer)
            session.commit()
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
            select(Sale).where(func.date(Sale.created_at) == today.date())
        ).one_or_none()
        return sale

    @classmethod
    def delete(cls, id: int, session: Session):
        sale = cls.get_one(id, session)
        if sale:
            session.delete(sale)
            session.commit()
            return "successfull"
        return None


class ProductControler:
    @classmethod
    def save(cls, model: ProductsIn, session: Session):
        model = Product.model_validate(model)
        model.avalable_stock = model.stock
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
        today = datetime.now(timezone.utc)
        if not productdb:
            return None

        product_stock = productdb.stock

        for k, v in model.model_dump().items():
            setattr(productdb, k, v)
            setattr(productdb, "updated_at", today)
        productdb.stock += product_stock
        productdb.avalable_stock += product_stock
        session.add(productdb)
        session.commit()
        session.refresh(productdb)
        return productdb

    @classmethod
    def delete(cls, id: int, session: Session):
        product = cls.get_one(id, session)
        if product:
            session.delete(product)
            session.commit()
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
            session.commit()
            return "deleted successful"
        return None


class InvoiceControler:
    @classmethod
    def save(cls, model: InvoiceIn, session: Session):
        invoice = Invoice.model_validate(model)
        session.add(invoice)
        session.commit()
        session.refresh(invoice)
        return invoice

    @classmethod
    def get_all(cls, offset: int, limit: int, session: Session):
        invoiceses = session.exec(select(Invoice).offset(offset).limit(limit)).all()
        return invoiceses

    @classmethod
    def get_one(cls, id: int, session: Session):
        invoice = session.get(Invoice, id)
        return invoice

    @classmethod
    def update_amount(cls, id: int, amount: float, session: Session):
        date = datetime.now(timezone.utc)
        invoice = cls.get_one(id, session)
        if not invoice:
            return None
        if amount < invoice.invoice_amount:
            invoice.status = Status.partial
        elif amount == invoice.invoice_amount:
            invoice.status = Status.paid
        invoice.paid_amount += amount
        invoice.updated_at = date
        session.add(invoice)
        session.commit()
        session.refresh(invoice)
        return invoice

    @classmethod
    def delete(cls, id: int, session: Session):
        invoice = cls.get_one(id, session)
        if invoice:
            session.delete(invoice)
            session.commit()
            return "successful deleted"
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
        today = datetime.now(timezone.utc)
        if not pay:
            return None
        for k, v in model.model_dump(exclude_unset=True).items():
            setattr(pay, k, v)
            setattr(pay, "updated_at", today)
        session.add(pay)
        session.commit()
        session.refresh(pay)
        return pay

    @classmethod
    def delete(cls, id: int, session: Session):
        payitem = cls.get_one(id, session)
        if payitem:
            session.delete(payitem)
            session.commit()
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
    def save_bulk(cls, model: PurchaseIn2, session: Session):
        purchase_items = model.purchaseitems
        validated_items = []
        total = 0
        for item in purchase_items:
            dbitem = PurchaseItem.model_validate(item)
            total += item.amount
            buying_price = item.amount / item.quantity
            print(total)
            if item.product_id is not None:
                product = ProductControler.get_one(item.product_id, session)
                print(product)
                if product:
                    product.stock = product.avalable_stock + item.quantity
                    product.avalable_stock += item.quantity
                    product.buying_price = buying_price
                    dbitem.product = product
                else:
                    raise Exception(f"Product with id {item.product_id} was not found")
            else:
                raise Exception("Product id was not found")

            validated_items.append(dbitem)
        if total != model.amount:
            print(total, model.amount)
            raise Exception(
                f"total amount {total} was not equal to model amount {model.amount}"
            )

        dbmodel = model
        dbmodel.purchaseitems = validated_items
        dbmodel = Purchase.model_validate(dbmodel)
        dbmodel.items_count = len(validated_items)
        session.add(dbmodel)
        session.commit()
        session.refresh(dbmodel)
        return dbmodel

    @classmethod
    def get_all(cls, offset: int, limit: int, session: Session):
        purchases = session.exec(select(Purchase).offset(offset).limit(limit)).all()
        return purchases

    @classmethod
    def get_one(cls, id: int, session: Session):
        purchase = session.get(Purchase, id)
        return purchase

    @classmethod
    def update(cls, id: int, model: ParchaseIn, session: Session):
        purchase = cls.get_one(id, session)
        today = datetime.now(timezone.utc)
        if not purchase:
            return None
        for k, v in model.model_dump(exclude_unset=True).items():
            setattr(purchase, k, v)
            setattr(purchase, "updated_at", today)
        session.add(purchase)
        session.commit()
        session.refresh(purchase)
        return purchase

    @classmethod
    def delete(cls, id: int, session: Session):
        purchase = cls.get_one(id, session)
        if purchase:
            session.delete(purchase)
            session.commit()
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

    @classmethod
    def get_all(cls, offset: int, limit: int, session: Session):
        items = session.exec(select(PurchaseItem).offset(offset).limit(limit)).all()
        return items

    @classmethod
    def delete(cls, id: int, session: Session):
        item = cls.get_one(id, session)
        if item:
            session.delete(item)
            session.commit()
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
        dbitem: list[Expense] = []
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
        today = datetime.now(timezone.utc)
        for k, v in model.model_dump(exclude_unset=True).items():
            setattr(expense, k, v)
            setattr(expense, "updated_at", today)
        session.add(expense)
        session.commit()
        session.refresh(expense)
        return expense

    @classmethod
    def delete(cls, id: int, session: Session):
        expense = cls.get_one(id, session)
        if expense:
            session.delete(expense)
            session.commit()
            return "successful"
        return None


class ProductStatisticsControler:
    name = ProductStatistics

    @classmethod
    def save(cls, model: ProductStatistics, session: Session):
        modeldb = ProductStatistics.model_validate(ProductStatistics)
        session.add(modeldb)
        session.commit()
        session.refresh(modeldb)
        return modeldb

    @classmethod
    def add_product_statistics_from_product(
        cls, product_id: int, quantity: float, session: Session
    ):
        date = datetime.now(timezone.utc)
        product_stat = ProductStatistics(quantity_sold=quantity, product_id=product_id)
        product_stat.created_at = date
        product_stat.updated_at = date
        session.add(product_stat)
        session.commit()
        session.refresh(product_stat)
        return product_stat

    @classmethod
    def get_all(cls, limit: int, offset: int, session: Session):
        stats = session.exec(
            select(ProductStatistics).offset(offset).limit(limit)
        ).all()
        return stats

    @classmethod
    def get_product_stat(cls, id: int, limit: int, offset: int, session: Session):
        stat = session.exec(
            select(ProductStatistics)
            .where(ProductStatistics.product_id == id)
            .limit(limit)
            .offset(offset)
        ).all()
        if not stat:
            return None
        return stat

    @classmethod
    def get_product_stat_by_date(cls, id: int, date: date, session: Session):
        stat = session.exec(
            select(cls.name)
            .where(cls.name.product_id == id)
            .where(func.date(cls.name.created_at) == date)
        ).one_or_none()
        return stat

    @classmethod
    def get_one(cls, id: int, session: Session):
        stat = session.get(ProductStatistics, id)
        return stat

    @classmethod
    def delete(cls, id: int, session: Session):
        prod_stat = cls.get_one(id, session)
        if not prod_stat:
            return None
        session.delete(prod_stat)
        session.commit()
        return "deleted successful"

    @classmethod
    def update(cls, id: int, prod_stat: ProductStatistics, session: Session):
        date = datetime.now(timezone.utc)
        prodStat = cls.get_one(id, session)
        if not prodStat:
            return None
        for k, v in prod_stat.model_dump():
            setattr(prodStat, k, v)
        prodStat.updated_at = date
        session.add(prodStat)
        session.commit()
        session.refresh(prodStat)
        return prodStat
