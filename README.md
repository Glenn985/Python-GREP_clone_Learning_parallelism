Built a GREP-style text search tool in Python supporting your own flags/options, including recursive/search variations.
Experimented with normal file I/O vs mmap to understand memory-mapped files and their effect on large-file searching.
Implemented and compared single-process, multithreaded, and multiprocessing approaches.
Used multiprocessing queues for communication/work distribution between processes.
Explored why threads don't automatically improve CPU-bound Python workloads, including the role of the GIL, versus processes actually providing CPU parallelism.
Benchmarked different implementations rather than assuming parallelism would be faster.
Tested against large files (~1 GB) and got searches down to roughly the ~2-second range depending on the implementation/run.
Investigated the overhead of creating processes, IPC, splitting work, synchronization, and combining results.
Learned that more workers ≠ automatically faster because overhead and I/O can dominate.
Worked with chunking large files across workers and had to think about boundaries so lines/search matches weren't incorrectly split.
Compared CPU time vs wall-clock time to understand whether work was genuinely happening concurrently/parallel.
Used this project as an introduction to OS-level concepts such as processes, threads, virtual memory/memory mapping, file I/O, IPC, and scheduling.
