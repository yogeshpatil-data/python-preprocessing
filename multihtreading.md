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
* It improves performance when tasks are **waiting (I/O-bound)**

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

```python
# All API calls run together
```

👉 Total time ≈ **2 seconds**

---

## 🔥 Why?

Because while one thread is waiting (network/disk), another thread runs.

---

# 🔹 4. Python Threading Basics

---

## ✅ Creating a Thread

```python
import threading

def task():
    print("Running task")

t = threading.Thread(target=task)
t.start()
t.join()
```

---

# 🔹 5. Components of Multithreading (VERY IMPORTANT)

---

## 🔸 1. `Thread`

```python
t = threading.Thread(target=task, args=(arg1,))
```

### Parameters:

* `target` → function to execute
* `args` → arguments for function

---

## 🔸 2. `start()`

```python
t.start()
```

👉 Starts the thread
👉 Executes the function in a separate thread

---

## 🔸 3. `join()` (VERY IMPORTANT)

```python
t.join()
```

### What it does:

> Makes the main thread **wait** until this thread finishes

---

### 🔥 Example Without `join()`

```python
t.start()
print("Done")
```

👉 Output may be:

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

👉 Output:

```
Running task
Done
```

---

## 🔥 Key Insight

> `join()` ensures synchronization

Without it:

* Program may exit early
* Results may be incomplete

---

# 🔹 6. How Threads Work Internally

---

## 🔸 Context Switching

* CPU switches between threads
* Happens when:

  * Thread is waiting (I/O)
  * Time slice ends

---

## 🔸 GIL (Global Interpreter Lock)

👉 Only one thread executes Python bytecode at a time

---

### 🔥 Implication

| Task Type | Threading Benefit |
| --------- | ----------------- |
| I/O-bound | ✅ Yes             |
| CPU-bound | ❌ No              |

---

# 🔹 7. Real World Data Engineering Use Cases

---

# ✅ Use Case 1: API Data Ingestion

---

## Scenario

* 100 APIs
* Each takes 1 second

---

### ❌ Without Threads

```python
for api in apis:
    fetch(api)
```

👉 Time = 100 seconds

---

### ✅ With Threads

```python
import threading

def fetch(api):
    print(f"Fetching {api}")

threads = []

for api in apis:
    t = threading.Thread(target=fetch, args=(api,))
    t.start()
    threads.append(t)

for t in threads:
    t.join()
```

👉 Time ≈ 1–2 seconds

---

# ✅ Use Case 2: Reading Multiple Files

---

## Scenario

* 100 small JSON files

---

### ❌ Sequential

```python
for file in files:
    read(file)
```

---

### ✅ Multithreading

* Read multiple files in parallel
* Improves disk I/O utilization

---

# ✅ Use Case 3: Web Scraping / Data Collection

---

* Scraping 200 URLs
* Each takes 500ms

👉 Threads significantly reduce total time

---

# ✅ Use Case 4: Database Calls

---

* Fetch data from multiple tables / endpoints
* Use threads to parallelize queries

---

# 🔹 8. Example: Multithreading with File Processing

```python
import threading

def process_file(file):
    print(f"Processing {file}")

files = ["f1.json", "f2.json", "f3.json"]

threads = []

for f in files:
    t = threading.Thread(target=process_file, args=(f,))
    t.start()
    threads.append(t)

for t in threads:
    t.join()

print("All files processed")
```

---

# 🔹 9. When NOT to Use Multithreading

---

## ❌ CPU-heavy tasks

```python
for i in range(10**8):
    compute()
```

👉 Threads won’t help (GIL limitation)

---

## ❌ Complex shared state

* Race conditions
* Debugging becomes difficult

---

# 🔹 10. Common Issues

---

## 🔸 Race Condition

Multiple threads modify same data:

```python
counter += 1
```

👉 Can lead to incorrect results

---

## 🔸 Deadlock

Threads waiting on each other → program stuck

---

# 🔹 11. Best Practices

---

✔ Use threads for:

* API calls
* File I/O
* Network operations

✔ Always use:

```python
join()
```

✔ Avoid shared mutable data

✔ Use thread pools for scalability

---

# 🔹 12. Advanced: Thread Pool

```python
from concurrent.futures import ThreadPoolExecutor

def task(x):
    return x * 2

with ThreadPoolExecutor(max_workers=5) as executor:
    results = executor.map(task, [1,2,3,4,5])
```

---

# 🔥 Why ThreadPool?

* Cleaner code
* Manages threads automatically
* Scales better

---

# 🔹 13. Summary (Interview Ready)

---

* A thread is the smallest unit of execution in a process
* Python programs are single-threaded by default
* Multithreading enables concurrent execution
* Due to GIL, it is best suited for **I/O-bound tasks**
* `join()` ensures proper synchronization
* Widely used in data engineering for:

  * API ingestion
  * file processing
  * network calls

---

# 🔥 Final Intuition

| Scenario          | Use Threads?        |
| ----------------- | ------------------- |
| Waiting (I/O)     | ✅ YES               |
| Heavy computation | ❌ NO                |
| Parallel CPU work | Use multiprocessing |

---

**End of Document**
