# Python GREP Clone — Systems & Concurrency Learning Project

A GREP-style text search tool built in Python as a hands-on project to explore **file I/O, memory management, concurrency, multiprocessing, inter-process communication, and performance benchmarking**.

Rather than simply recreating `grep`, I used the project to experiment with different approaches to processing and searching large files and to understand where each approach performs well or poorly.

## Key Features & Experiments

* Built a **GREP-style text search tool** in Python with custom search flags and recursive file-search functionality.

* Experimented with different **file I/O strategies**, including:

  * Standard line-by-line file reading
  * Loading entire files into memory
  * Binary file processing
  * Memory-mapped files using `mmap`

* Benchmarked retrieval/search times across the different approaches to understand their performance characteristics.

* Tested the limitations of loading very large files directly into memory, including intentionally pushing the program to the point of **RAM exhaustion**, demonstrating why streaming and memory-mapped approaches can be preferable for large datasets.

## Concurrency & Parallelism

Implemented and compared several execution models:

* **Single-process execution**
* **Multithreading**
* **Multiprocessing**

This provided a practical way to understand the difference between **CPU-bound and I/O-bound workloads**.

In particular, I explored how Python's **Global Interpreter Lock (GIL)** limits CPU-bound parallelism with threads, while multiprocessing allows work to execute across multiple CPU cores.

For sufficiently large workloads, multiprocessing improved performance significantly. However, for smaller workloads, the normal single-process implementation could be faster because multiprocessing introduces additional overhead from:

* Process creation
* Inter-process communication (IPC)
* Work distribution
* Synchronization
* Combining results from workers

This demonstrated an important performance principle: **adding more workers does not automatically make a program faster**.

## Inter-Process Communication

Used Python's **multiprocessing queues** to distribute work and communicate results between processes.

This helped me explore:

* Producer/consumer-style communication
* Passing data between isolated processes
* IPC overhead
* Coordinating multiple workers
* Collecting and combining results

## Large-File Processing

Tested the search implementations against large files in the range of approximately **1 GB to 5 GB**.

For some ~1 GB tests, search times reached roughly the **2-second range**, depending on the implementation and test conditions.

Large files were divided into chunks and distributed across workers, which introduced additional problems such as ensuring that **chunk boundaries did not incorrectly split lines or search matches**.

## Performance Benchmarking

Rather than assuming that a particular implementation would be faster, I benchmarked the different approaches and compared their behavior under different workloads.

Experiments included:

* Single process vs multithreading vs multiprocessing
* Standard file I/O vs `mmap`
* Whole-file loading vs incremental/line-by-line processing
* Different file sizes and worker counts
* Multiprocessing overhead on small vs large workloads
* **CPU time vs wall-clock time** to better understand concurrency and actual parallel execution

## What I Learned

This project became an introduction to several systems and operating-system concepts, including:

* Processes and threads
* CPU-bound vs I/O-bound workloads
* Python's Global Interpreter Lock (GIL)
* Multiprocessing and multicore execution
* Inter-process communication (IPC)
* Queues and worker coordination
* Memory-mapped files
* File I/O and buffering
* Virtual memory and RAM usage
* Work partitioning and chunk boundaries
* Process creation and synchronization overhead
* CPU time vs wall-clock time
* Performance benchmarking and bottleneck analysis

The main takeaway from the project was that **performance optimization depends heavily on the workload**. Techniques such as multiprocessing can provide substantial improvements for the right workload while actually reducing performance when their overhead exceeds the amount of useful work being parallelized.
