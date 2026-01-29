# API Control-Plane Mastery (Python for Data Engineers)

This document is a **revision-ready, no-fluff summary** of everything learned in this session.
It is written so that rereading it later restores **full fluency**, not just familiarity.

---

## 1. Core Mental Model (Very Important)

**Python in Data Engineering (control-plane use)** is responsible for:

* Orchestration
* Failure detection
* Failure classification
* Decision-making (retry / stop / escalate)

Python is **NOT** for heavy data processing here.

> Control-plane code must be *predictable under failure*.

---

## 2. Logging: Purpose & Architecture

### 2.1 What Logging Is (and Is NOT)

Logging:

* Records facts for humans and monitoring systems
* Does **NOT** change control flow
* Does **NOT** handle errors

Raising exceptions:

* Changes control flow
* Forces caller to decide
* Does **NOT** persist information unless logged

> **Logging = visibility**
> **Raising = control flow**

Both are required.

---

## 2.2 Logging Architecture Used

### Root Logger Concept

* Python has one **root logger** (always exists)
* All other loggers propagate to it
* Handlers are attached **only to the root logger**

Flow:

```
module logger → root logger → handler → file
```

---

## 2.3 logger.py (Final Design)

Responsibilities:

1. Configure logging once
2. Provide named loggers to modules

```python
# src/logging/logger.py
import logging
from pathlib import Path

_LOGGING_CONFIGURED = False


def setup_logging() -> None:
    global _LOGGING_CONFIGURED

    if _LOGGING_CONFIGURED:
        return

    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    file_handler = logging.FileHandler(log_dir / "app.log")

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    file_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)
    root_logger.setLevel(logging.INFO)

    _LOGGING_CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
```

Key points:

* File logging only (no console)
* Idempotent setup
* Centralized configuration

---

## 2.4 Logging Exceptions Correctly

### WRONG

```python
except Exception as e:
    logger.error(e)
```

❌ Loses stack trace

### CORRECT

```python
except Exception:
    logger.error("Operation failed", exc_info=True)
    raise
```

`exc_info=True` logs:

* Exception type
* Message
* Full traceback

---

## 3. Custom Exceptions (Exception Taxonomy)

### Purpose

Custom exceptions:

* Define **domain-level failures**
* Prevent leaking low-level technical details
* Enable intelligent handling at orchestration layer

> Low-level code detects problems
> High-level code decides outcomes

---

### Exception Hierarchy Used

```python
# src/core/exceptions.py
class IngestionError(Exception):
    pass

class ConfigError(IngestionError):
    pass

class ExternalAPIError(IngestionError):
    pass

class FileOperationError(IngestionError):
    pass
```

Rules:

* Low-level modules raise **specific subclasses**
* `main()` catches `IngestionError`

---

## 4. APIs – First Principles

### 4.1 The Only 4 API Outcomes

1. **Success** (2xx)
2. **Client error** (4xx) → usually NOT retryable
3. **Server error** (5xx) → retryable
4. **No response** → MOST dangerous

> APIs fail more often by *not responding* than by returning errors.

---

## 4.2 Timeouts (Mandatory)

### Two Types

```python
timeout = (connect_timeout, read_timeout)
```

Example:

```python
timeout = (3, 5)
```

* Connection timeout: fail fast
* Read timeout: allow some processing time

> Any API call without a timeout is a production bug.

---

## 4.3 Retry Rules

### Retryable

* Timeouts
* Network errors
* HTTP 5xx
* HTTP 429 (with backoff)

### NOT Retryable

* HTTP 4xx (except 429)
* Bad data

Rule:

> Retry only if repeating the **same request** could reasonably succeed.

---

## 4.4 Backoff

### Why

Immediate retries amplify failures.

### Strategy Used

* Exponential backoff
* With maximum cap

Example:

```
1s → 2s → 4s → 8s → 8s
```

Retries must always be bounded.

---

## 5. API Boundary Translation (Very Important)

### Rule

* `requests` exceptions must **NOT** leak
* API module translates them into `ExternalAPIError`

### Example

```python
except requests.exceptions.RequestException as e:
    logger.error("External API call failed", exc_info=True)
    raise ExternalAPIError(
        "Failed to fetch posts from external API"
    ) from e
```

Why:

* Log = technical context
* Raise = system-level failure reason

---

## 6. Retry + Backoff Implementation (API Module)

Key design rules:

* Retry loop inside API module
* Log WARNING during retries
* Log ERROR only once (final failure)
* Raise ONE `ExternalAPIError` after exhaustion

Retry decision uses:

```python
status = getattr(e.response, "status_code", None)
```

Reason:

* Only HTTP errors have response
* Timeouts / network errors do not

---

## 7. Pagination (Data Engineering Core)

### Why Pagination Exists

APIs never return all data at once.
Data comes in **pages / chunks**.

---

### Pagination Styles

1. Page-number based (fragile)
2. Offset-limit (fragile)
3. Cursor-based (BEST)

Cursor-based pagination is safest because ordering is stable.

---

## 8. Generators (Critical DE Concept)

### What a Generator Is

A generator is:

* A paused function
* With preserved state
* Producing values lazily using `yield`

Calling a generator function:

* Does NOT execute it
* Returns a generator object

Execution happens only on `next()`.

---

### How `for` Loop Uses a Generator

```python
for item in generator:
    process(item)
```

Internally:

```python
while True:
    try:
        item = next(generator)
    except StopIteration:
        break
```

Each `yield` → one loop iteration

---

## 9. Pagination as a Generator

### Core Idea

> Generators do NOT avoid loading pages.
> They avoid **accumulating pages**.

Memory stays flat:

* One page at a time
* One record at a time yielded

---

### Example Logic

```python
data = response.json()

if not data:
    break

for record in data:
    yield record
```

* `data` = one full page
* `if not data` = termination condition
* `yield record` = record-level streaming

---

## 10. Stop Condition Responsibility

* Generator decides **when iteration ends**
* Loop does NOT decide
* Generator ends by finishing execution
* Python raises `StopIteration` automatically

If API returns empty list mid-pagination:

* Generator stops early
* Remaining data is lost

This is why cursor-based pagination is preferred.

---

## 11. Page Size

* Client may REQUEST page size
* API ENFORCES page size
* API may cap, ignore, or reject

Page size is:

* A **performance knob**
* NOT a correctness rule

Make it configurable.

---

## 12. Final Master Rules (Memorize)

* Logging ≠ Handling
* Raise domain exceptions, not library exceptions
* Timeouts are mandatory
* Retries must be bounded
* Backoff prevents failure amplification
* Pagination is streaming, not batching
* Generators avoid accumulation, not loading
* Stop conditions are API contracts

---

## Status

✅ Logging mastered
✅ Exceptions mastered
✅ APIs mastered (timeouts, retries, backoff, pagination)

Next module:
**Files & S3 Control-Plane Logic**
