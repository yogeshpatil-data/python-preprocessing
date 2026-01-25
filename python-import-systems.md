# Python Import System – `sys.path` & `PYTHONPATH` (Deep Engineering Guide)

This document is a **foundational, production-grade explanation** of how Python imports work.

It is written for **Data Engineers / Backend Engineers** who want **complete clarity**, not shortcuts.

If you truly understand this document, you will:

* Never be confused by import errors again
* Write portable, production-safe Python code
* Avoid environment-specific hacks
* Understand why imports break in Lambda, Airflow, Spark, Docker

---

## 1. The Core Problem Python Must Solve

Every time Python sees this line:

```python
import something
```

Python must answer **one critical question**:

> Where on this machine should I look for `something`?

Python cannot guess.
It must follow **explicit rules**.

Those rules revolve around a single object:

> **`sys.path`**

Everything else (`PYTHONPATH`, folders, site-packages) exists only to **build or influence `sys.path`**.

---

## 2. What Exactly Is `sys.path`?

### Definition

> **`sys.path` is a list of directory paths where Python searches for modules and packages during import.**

It is a normal Python list.

```python
import sys
print(sys.path)
```

Example output (simplified):

```text
[
  '/home/user/project/src',
  '/usr/lib/python3.11',
  '/usr/lib/python3.11/site-packages'
]
```

Python searches **top to bottom**, in order.

---

## 3. How Python Builds `sys.path` (Exact Order)

Python constructs `sys.path` **at interpreter startup** using strict rules.

### Rule 1 – Script Directory (Highest Priority)

When you run:

```bash
python src/main.py
```

Python automatically inserts:

```text
/home/user/project/src
```

as `sys.path[0]`.

This rule exists so your program can import **its own code**.

> This single rule explains ~90% of Python import behavior.

---

### Rule 2 – `PYTHONPATH` Environment Variable

`PYTHONPATH` is an **optional environment variable**.

Example:

```bash
export PYTHONPATH=/custom/code:/shared/libs
```

Before Python starts, it:

1. Reads `PYTHONPATH`
2. Splits it into folders
3. Inserts them into `sys.path`

Important:

* `PYTHONPATH` itself is **not used during import**
* Only `sys.path` is used

---

### Rule 3 – Standard Library Paths

Python adds directories containing built-in modules:

* `os`
* `sys`
* `json`
* `logging`

These come with Python itself.

---

### Rule 4 – Site-Packages (Installed Libraries)

When you run:

```bash
pip install requests
```

The package is installed into:

```text
.../site-packages/
```

That directory is added to `sys.path`.

---

## 4. What Is `PYTHONPATH` Really?

### Definition

> **`PYTHONPATH` is a user-controlled way to add directories to Python’s import search path before execution begins.**

Key distinction:

| Concept      | Exists When             | Purpose                    |
| ------------ | ----------------------- | -------------------------- |
| `PYTHONPATH` | Before Python starts    | Influence startup behavior |
| `sys.path`   | While Python is running | Actual import resolution   |

`PYTHONPATH` is only a **builder**, never the executor.

---

## 5. How Python Resolves an Import (Exact Algorithm)

Given:

```python
from config.loader import load_config
```

Python performs the following steps:

1. Look for `config` in `sys.path[0]`
2. If not found, look in `sys.path[1]`
3. Continue until the end of `sys.path`
4. If found:

   * If `config.py` → load module
   * If `config/` + `__init__.py` → load package
5. Look for `loader.py` inside `config`
6. Import `load_config`

If any step fails:

```text
ModuleNotFoundError
```

---

## 6. Why `__init__.py` Matters

Python must distinguish between:

* Random folders
* Python packages

`__init__.py` explicitly declares:

> This folder is Python code and is importable.

Production rule:

> **Always include `__init__.py` in packages.**

Even though Python 3 allows implicit namespaces, production systems still rely on explicit packages for stability.

---

## 7. Absolute Imports vs Relative Imports

### Absolute Import (Preferred)

```python
from config.loader import load_config
```

* Clear
* Predictable
* Portable

### Relative Import (Advanced / Limited Use)

```python
from .loader import load_config
```

Problems:

* Breaks when running as script
* Confusing in large projects
* Error-prone in Airflow / Lambda

Production rule:

> **Prefer absolute imports for application code.**

---

## 8. Common Broken Import Scenarios (With Explanation)

### ❌ Importing `src.*`

```python
from src.config.loader import load_config
```

Why it breaks:

* `src` is not in `sys.path`
* Python looks for `src/src/...`

---

### ❌ Works in IDE, fails in terminal

Reason:

* IDE silently modifies `sys.path`
* Terminal does not

Never trust IDE behavior.

---

### ❌ Fixing imports by setting `PYTHONPATH`

This is a **band-aid**, not a solution.

It introduces:

* Hidden dependencies
* Environment-specific behavior
* Deployment failures

---

## 9. Why This Matters in Real Systems

### AWS Lambda

* Code is zipped
* Root folder is injected into `sys.path`
* `PYTHONPATH` may not exist

### Airflow

* DAG folder is injected
* Incorrect imports = broken DAGs

### Spark

* Executors have isolated environments
* Imports must be deterministic

---

## 10. Engineering Golden Rules (Memorize These)

1. Python imports search **folders, not files**
2. Python only uses `sys.path` at runtime
3. `PYTHONPATH` is not reliable for production
4. Never import from `src.*`
5. Always control your entry point
6. Always include `__init__.py`

---

## 11. Mental Model (Simple but Correct)

> Python does not magically find code.
> Python only searches directories listed in `sys.path`.

If you know what `sys.path[0]` is, you understand imports.

---

## 12. Final Takeaway

Understanding `sys.path` and `PYTHONPATH` is not optional for serious Python engineers.

It directly affects:

* Reliability
* Portability
* Deployments
* Debuggability

Once this is clear, Python stops being confusing and starts being predictable.

---

## Status

This document is **foundational** and will not change.
All future Python work in this project assumes this understanding.
