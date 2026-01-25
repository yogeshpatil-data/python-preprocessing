# Python Exception & Error Handling – From Zero to Production (Tier‑1 Guide)

This document is a **complete, end‑to‑end explanation of error and exception handling in Python**, written for engineers who want **real understanding**, not memorization.

It starts from absolute basics and gradually reaches **production‑grade Data Engineering practices**.

If you understand this document fully, you will:

* Stop being afraid of exceptions
* Know exactly **where to raise** and **where to catch** errors
* Avoid silent failures and bad data
* Design predictable, debuggable Python systems

---

## 1. What Is an Error?

### Simple definition

> **An error is any situation where a program cannot continue its normal execution.**

Examples:

* File does not exist
* Network request fails
* Invalid input data
* Division by zero

Errors are **inevitable** in real systems.
Good engineering is not about avoiding errors, but about **responding to them correctly**.

---

## 2. What Is an Exception?

### Core idea

> **An exception is Python’s way of representing an error as an object.**

When something goes wrong:

1. Python creates an exception object
2. The exception contains:

   * Error type
   * Error message
   * Where it happened (stack trace)
3. Python stops normal execution and looks for someone to handle it

### Example

```python
x = 10 / 0
```

Python raises:

```
ZeroDivisionError: division by zero
```

Here:

* `ZeroDivisionError` is the exception type
* The message explains the problem

---

## 3. Why Exceptions Exist

Without exceptions, Python could only:

* Print an error
* Exit blindly

With exceptions, Python can:

* Categorize failures
* Preserve context
* Allow programs to decide what to do

Exceptions make **controlled failure** possible.

---

## 4. What Does `raise` Mean?

### Simple meaning

> **`raise` means: “I encountered a problem I cannot decide about. I am escalating it.”**

Escalation always happens **to the caller** (the code that called the function).

### Example

```python
def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
```

* `divide()` detects a problem
* It cannot decide what to do
* It raises the problem upward

---

## 5. What Does `try / except` (Catch) Mean?

### Core idea

> **Catching an exception means: “I know this problem might happen, and I know what to do if it does.”**

### Example

```python
try:
    result = divide(10, 0)
except ValueError:
    print("Invalid calculation")
```

If the error occurs:

* Normal execution stops
* The `except` block runs
* The program continues in a controlled way

---

## 6. What Is Handling an Error?

### Critical clarification

> **Handling is NOT printing or logging.**

Handling means **making a decision**.

### Examples of real handling

* Retry an operation
* Stop the system intentionally
* Skip a record
* Roll back a transaction
* Alert a monitoring system

### Examples that are NOT handling

```python
print("Error occurred")
logger.error("Something failed")
```

These only record information. They do not decide system behavior.

---

## 7. Python’s Default Behavior (When You Do Nothing)

If an exception is not caught:

* Python prints the stack trace
* Python exits the program

This is a valid strategy for:

* Bugs
* Unrecoverable errors

But it is **not sufficient** for production systems.

---

## 8. Why Not Catch Everything Everywhere?

### Bad pattern (very common)

```python
try:
    do_work()
except Exception:
    print("Error happened")
```

Problems:

* Error context lost
* Bugs hidden
* System continues in broken state
* Silent data corruption

---

## 9. Correct Error‑Handling Rule (Very Important)

> **Raise errors where they occur. Catch errors where decisions are made.**

This rule governs all good Python systems.

---

## 10. Custom Exceptions (Why and How)

### What is a custom exception?

A custom exception is simply a class that inherits from `Exception`.

```python
class ConfigError(Exception):
    pass
```

Python treats it like any built‑in error.

---

## 11. Why Use Custom Exceptions?

Without custom exceptions:

* All failures look the same
* No categorization
* No intelligent handling

With custom exceptions:

* Errors are meaningful
* Decisions become possible
* Systems become predictable

---

## 12. Exception Inheritance (Very Important)

### Example

```python
class IngestionError(Exception):
    pass

class ConfigError(IngestionError):
    pass

class ExternalAPIError(IngestionError):
    pass
```

Benefits:

* Catch all ingestion failures together
* Still distinguish specific causes

---

## 13. Where to Raise Exceptions

### Rule

> **Raise exceptions at system boundaries.**

Examples:

* File system
* External APIs
* Databases

### Example (API boundary)

```python
try:
    response = requests.get(url)
except requests.exceptions.RequestException as e:
    raise ExternalAPIError("API communication failed") from e
```

This converts low‑level errors into system‑level language.

---

## 14. Where to Catch Exceptions

### Rule

> **Catch exceptions at the orchestration layer.**

In most applications:

* `main()`
* Job runner
* Scheduler

### Example

```python
try:
    run_pipeline()
except IngestionError:
    logger.error("Pipeline failed")
    raise
```

This is controlled, intentional failure.

---

## 15. When You Don’t Know What Can Go Wrong

This is normal.

### Correct approach

1. Let the program fail
2. Observe the exception
3. Decide if handling is meaningful
4. Add handling only when justified

Never guess error names.

---

## 16. Catching by Type (How Python Matches Exceptions)

Python matches exceptions by type:

```python
except FileNotFoundError:
```

Also matches subclasses:

```python
except IngestionError:
```

Order matters. Specific exceptions must come before general ones.

---

## 17. Catching Everything (Last Resort)

```python
except Exception as e:
    logger.error("Unhandled error", exc_info=True)
    raise
```

Allowed **only at the top level**, and only if re‑raised.

---

## 18. Exception Handling in Data Engineering Systems

### Key principles

* Bad data is worse than no data
* Silent failures are unacceptable
* Controlled crashes are often correct

### Typical DE flow

| Layer     | Responsibility               |
| --------- | ---------------------------- |
| Low‑level | Detect problem → raise       |
| Mid‑level | Add context                  |
| Top‑level | Decide: retry / stop / alert |

---

## 19. Common Anti‑Patterns (Avoid These)

* Catching `Exception` everywhere
* Printing instead of deciding
* Swallowing errors
* Continuing after fatal failures
* Using exceptions for normal control flow

---

## 20. Final Mental Model (Lock This In)

> **Errors are inevitable. Exceptions describe them. `raise` escalates. `except` decides.**

If you follow this model, your Python systems will be:

* Predictable
* Debuggable
* Production‑ready

---

## Status

This document is **foundational**.
All future Python work in this project assumes full understanding of this content.
