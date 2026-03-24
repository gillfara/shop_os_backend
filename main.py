from dataclasses import dataclass
from typing import Protocol


class Person(Protocol):
    def greet(self, name: str): ...


class Customer:
    def greet(self, name: str):
        print(f"hellow {name} are you ok")


class UseCase:
    def __init__(self, person: Person, name: str):
        self.person = person
        self.name = name

    @property
    def greet(self):
        return self.person.greet(self.name)


if __name__ == "__main__":
    customer = Customer()
    case = UseCase(customer, "faraday")
    case.greet
