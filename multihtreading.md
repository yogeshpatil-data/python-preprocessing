# Multithreading in Python — Detailed Guide (Data Engineering Focus)

---

# 🔹 1. What is Multithreading?

A **thread** is the smallest unit of execution inside a process.

* A **process** = a running program
* A **thread** = a worker inside that program

👉 By default, Python programs run in **one thread (main thread)**.

```python
print("Hello")
```

✔ Runs sequentially in a single thread.

---

# 🔹 2. Why Multithreading?

Multithreading allows:

> Multiple tasks to run **concurrently** within the same process

---

## 🔥 Important Clarification

* Multithreading ≠ true parallel execution (due to GIL)
* It improves performance when tasks are **I/O-bound (waiting)**

---

# 🔹 3. What Problem Does It Solve?

### ❌ Without Multithreading

```python
call_api_1()  # 2 sec
call_api_2()  # 2 sec
call_api_3()  # 2 sec
```

👉 Total time = **6 seconds**

---

### ✅ With Multithreading

👉 All API calls overlap

👉 Total time ≈ **2 seconds**

---

# 🔹 4. Python Threading Basics

```python
import threading

def task():
    print("Running task")

t = threading.Thread(target=task)
t.start()
t.join()
```

---

# 🔹 5. Components of Multithreading

---

## 🔸 1. `Thread`

```python
t = threading.Thread(target=task, args=(arg1,))
```

* `target` → function to execute
* `args` → arguments

---

## 🔸 2. `start()`

```python
t.start()
```

👉 Starts execution in a separate thread

---

## 🔸 3. `join()` (VERY IMPORTANT)

```python
t.join()
```

> Makes the main thread **wait until this thread completes**

---

### 🔥 Without `join()`

```python
t.start()
print("Done")
```

Possible output:

```
Done
Running task
```

---

### ✅ With `join()`

```python
t.start()
t.join()
print("Done")
```

Output:

```
Running task
Done
```

---

## 🔥 Key Insight

> `join()` ensures **synchronization and completeness**

---

# 🔹 6. How Threads Actually Work (CRITICAL UNDERSTANDING)

---

## 🔥 Core Question

> What happens when a thread is waiting for API or file I/O?

---

## 🔹 Execution Flow (Step-by-step)

---

### Scenario: Two API calls in two threads

```python
def fetch(api):
    response = requests.get(api)
    print(response.status_code)
```

---

### 🔸 Step 1: Thread T1 starts

```
T1 → requests.get(api1)
```

* Sends request
* Goes into **WAITING (blocked state)**

---

### 🔸 Step 2: CPU becomes free

👉 Since T1 is waiting, CPU switches to another thread

---

### 🔸 Step 3: Thread T2 starts

```
T2 → requests.get(api2)
```

* Also goes into waiting

---

### 🔸 Step 4: Both threads waiting

```
T1 → waiting for API1
T2 → waiting for API2
```

---

### 🔸 Step 5: API1 responds

```
T1 → READY → RUNNING
```

* Resumes execution
* Continues from next line

---

### 🔸 Step 6: API2 responds

Same process for T2

---

# 🔥 MOST IMPORTANT INSIGHT

> Threads are **paused, not lost**

✔ Their state is preserved
✔ Variables remain intact
✔ Execution resumes from same point

---

# 🔹 Thread Lifecycle

```
RUNNING → WAITING → READY → RUNNING → DONE
```

---

# 🔹 What happens to data?

---

## API case

```python
response = requests.get(api)
```

* OS handles network call
* Data stored in memory buffer
* Assigned to `response` when ready

---

## File case

```python
data = f.read()
```

* Disk I/O handled by OS
* Thread waits
* Data loaded into memory when ready

---

# 🔥 Key Concept

> Python delegates I/O work to the OS
> OS notifies when operation completes

---

# 🔹 Why This Improves Performance

---

## ❌ Without threads

```
[WAIT API1][WAIT API2][WAIT API3]
```

---

## ✅ With threads

```
[WAIT API1]
    [WAIT API2]
        [WAIT API3]
```

👉 Waiting overlaps → faster execution

---

# 🔹 Blocking I/O

When you do:

```python
requests.get()
```

👉 Thread becomes:

> **Blocked (waiting for external resource)**

---

# 🔹 GIL Behavior

* During I/O wait → GIL is released
* Other threads can run

---

# 🔹 Mental Model

Each thread is like:

* A worker with its own state
* Pauses when waiting
* Resumes from same point

---

# 🔹 7. Real World Data Engineering Use Cases

---

## ✅ API Ingestion

* Fetch data from multiple APIs in parallel

---

## ✅ File Processing

* Read multiple files simultaneously

---

## ✅ Web Scraping

* Collect data from multiple sources

---

## ✅ Database Calls

* Execute parallel queries

---

# 🔹 Example

```python
import threading

def fetch(api):
    print(f"Fetching {api}")

threads = []

for api in ["A", "B", "C"]:
    t = threading.Thread(target=fetch, args=(api,))
    t.start()
    threads.append(t)

for t in threads:
    t.join()
```

---

# 🔹 8. When NOT to Use Multithreading

---

## ❌ CPU-heavy tasks

```python
for i in range(10**8):
    compute()
```

👉 GIL prevents speedup

---

## ❌ Shared mutable state

* Race conditions
* Bugs

---

# 🔹 9. Common Issues

---

## 🔸 Race Condition

Multiple threads modify same variable

---

## 🔸 Deadlock

Threads waiting on each other

---

# 🔹 10. Best Practices

---

✔ Use for I/O-bound tasks
✔ Always use `join()`
✔ Avoid shared state
✔ Prefer thread pools

---

# 🔹 11. Thread Pool (Recommended)

```python
from concurrent.futures import ThreadPoolExecutor

def task(x):
    return x * 2

with ThreadPoolExecutor(max_workers=5) as executor:
    results = executor.map(task, [1,2,3,4,5])
```

---

# 🔹 12. Summary (Interview Ready)

---

* Python programs are single-threaded by default
* Multithreading enables concurrency
* Best for I/O-bound tasks
* Threads pause during I/O but retain state
* `join()` ensures proper synchronization

---

# 🔥 Final Intuition

| Scenario          | Use Threads?        |
| ----------------- | ------------------- |
| Waiting (I/O)     | ✅ YES               |
| Heavy computation | ❌ NO                |
| CPU parallelism   | Use multiprocessing |

---

**End of Document**
