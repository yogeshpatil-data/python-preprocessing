# 📘 Python Object-Oriented Programming (OOP) — Deep Dive (Beginner → Advanced, Data Engineering Focus)

---

# 🔥 1. Overview

This document is designed to give you a **complete, structured, and deeply clear understanding of Object-Oriented Programming (OOP) in Python**.

This is NOT a shortcut guide.
You will learn:

* What each concept actually means
* Why it exists
* How Python implements it internally
* How it is used in real Data Engineering systems

Every concept is explained in **at least 3–4 lines with examples and reasoning**.

---

# 🔥 2. What is OOP (Correct Understanding)

OOP (Object-Oriented Programming) is a way of writing code where we organize logic into **objects that contain both data and behavior**.
Instead of writing everything as separate functions, we group related data and operations together into a single unit called a class.
This helps manage complexity, especially when systems grow large and involve multiple components interacting with each other.
In real-world systems like data pipelines, OOP allows us to build reusable, modular, and maintainable components.

---

# 🔥 3. Python Object Model (VERY IMPORTANT FOUNDATION)

---

## 🔹 Everything in Python is an Object

In Python, everything is treated as an object, including numbers, strings, functions, and even classes.
Each object has:

* a type (what kind of object it is)
* a value (data it holds)
* an identity (unique memory location)

This means Python is **fully object-oriented at its core**, not just syntactically.

---

### Example

```python id="a1"
x = 10
print(type(x))   # <class 'int'>
```

---

## 🔹 Variables are References (Critical Concept)

In Python, variables do NOT store actual values directly.
They store references (pointers) to objects in memory.
This means multiple variables can point to the same object, which can lead to unexpected behavior if the object is mutable.
Understanding this is critical for avoiding bugs.

---

### Example

```python id="a2"
a = [1, 2]
b = a
b.append(3)

print(a)  # [1, 2, 3]
```

👉 Both changed because they reference the same object.

---

# 🔥 4. Class and Object (Step-by-Step Understanding)

---

## 🔹 What is a Class?

A class is a **blueprint or template** used to create objects.
It defines what data (attributes) and behavior (methods) the objects will have.
Classes do not hold actual data until objects are created from them.
They are used to standardize structure and behavior.

---

## 🔹 What is an Object?

An object is an **instance of a class**.
It contains actual data and can use the methods defined in the class.
Each object is independent and has its own state.
Objects are what you actually work with at runtime.

---

### Example

```python id="a3"
class User:
    def __init__(self, id, name):
        self.id = id
        self.name = name

u1 = User(1, "Yogesh")
u2 = User(2, "Amit")
```

---

## 🔹 What happens internally?

When you write:

```python id="a4"
u1 = User(1, "Yogesh")
```

Python does:

1. Creates empty object using `__new__`
2. Initializes it using `__init__`
3. Assigns reference to `u1`

---

# 🔥 5. Encapsulation (Proper Understanding)

---

## 🔹 Definition

Encapsulation means **controlling how data is accessed and modified** rather than directly exposing it.
It helps ensure that data is not accidentally changed in an invalid way.
In Python, encapsulation is achieved using naming conventions, not strict enforcement.
This improves code safety and maintainability.

---

### Example

```python id="a5"
class Account:
    def __init__(self):
        self.__balance = 0

    def deposit(self, amount):
        if amount > 0:
            self.__balance += amount
```

---

## 🔹 Why it is important

* Prevent invalid updates
* Maintain internal consistency
* Provide controlled interface

---

# 🔥 6. Abstraction (Clear Explanation)

---

## 🔹 Definition

Abstraction means **showing only necessary details and hiding internal complexity**.
It allows users to interact with a system without knowing how it works internally.
This makes systems easier to use and modify.
It is especially useful when multiple implementations exist.

---

### Example

```python id="a6"
from abc import ABC, abstractmethod

class DataSource(ABC):
    @abstractmethod
    def read(self):
        pass
```

---

## 🔹 Why abstraction matters

* Reduces complexity
* Makes components interchangeable
* Enables scalability

---

## DE Example

You can switch:

* S3 source
* Database source

without changing pipeline logic.

---

# 🔥 7. Inheritance (Step-by-Step)

---

## 🔹 Definition

Inheritance allows one class to **reuse and extend another class**.
The child class inherits properties and methods of the parent class.
This reduces code duplication and improves reuse.
However, it should be used carefully to avoid tight coupling.

---

### Example

```python id="a7"
class BasePipeline:
    def run(self):
        print("Running pipeline")

class ETLPipeline(BasePipeline):
    def run(self):
        print("Custom ETL logic")
```

---

## 🔹 Key Insight

Inheritance is NOT just reuse—it creates dependency between classes.

---

# 🔥 8. Polymorphism (Simple but Powerful)

---

## 🔹 Definition

Polymorphism means **same interface, different behavior**.
Different objects can respond differently to the same method call.
Python achieves this through duck typing.
This makes code flexible and extensible.

---

### Example

```python id="a8"
def read_data(source):
    return source.read()
```

---

👉 Works with any object that has `read()`

---

# 🔥 9. Composition (VERY IMPORTANT)

---

## 🔹 Definition

Composition means building a class using other classes instead of inheriting.
It promotes flexibility because components can be changed easily.
It reduces tight coupling between classes.
It is preferred over inheritance in most production systems.

---

### Example

```python id="a9"
class Logger:
    def log(self, msg):
        print(msg)

class Pipeline:
    def __init__(self):
        self.logger = Logger()
```

---

# 🔥 10. Class vs Instance Variables

---

## 🔹 Definition

Class variables are shared across all objects.
Instance variables are unique for each object.
Understanding this prevents bugs related to shared state.
It is important for designing scalable systems.

---

### Example

```python id="a10"
class A:
    x = 10

    def __init__(self):
        self.y = 20
```

---

# 🔥 11. Method Types (Clear Explanation)

---

## 🔸 Instance Method

Works with object data.

---

## 🔸 Class Method

Works with class-level data.

---

## 🔸 Static Method

Utility function grouped inside class.

---

---

# 🔥 12. Magic Methods (Dunder Methods)

---

## 🔹 Definition

Magic methods allow you to define how objects behave with built-in operations.
They integrate your objects with Python’s syntax and operators.
They make objects behave like built-in types.
They are essential for advanced design.

---

### Example

```python id="a11"
class A:
    def __str__(self):
        return "Hello"
```

---

# 🔥 13. Real Data Engineering Example

---

```python id="a12"
class DataSource:
    def read(self):
        raise NotImplementedError

class S3Source(DataSource):
    def read(self):
        return "data from s3"

class Transformer:
    def transform(self, data):
        return data.upper()

class Loader:
    def load(self, data):
        print("Loaded:", data)

class Pipeline:
    def __init__(self, source, transformer, loader):
        self.source = source
        self.transformer = transformer
        self.loader = loader

    def run(self):
        data = self.source.read()
        data = self.transformer.transform(data)
        self.loader.load(data)
```

---

# 🔥 14. Common Misconceptions

---

❌ OOP = classes only
✔ OOP = design principles

---

❌ Inheritance always best
✔ Composition often better

---

❌ Private variables are secure
✔ Only naming convention

---

# 🔥 15. Real-World Enhancements

---

## 🔹 Logging

## 🔹 Config Injection

## 🔹 Retry Logic

## 🔹 Testing

---

# 🔥 16. Final Mental Model

```text id="a13"
Understand → Design → Compose → Reuse → Scale
```

---

# 🔥 17. Interview Summary

> OOP in Python helps build modular, reusable, and scalable systems by organizing code into objects. It uses principles like encapsulation, abstraction, inheritance, and polymorphism, with composition being the preferred design strategy in real-world applications.

---

**End of Document**
