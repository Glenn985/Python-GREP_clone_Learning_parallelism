import os
import time
import psutil
import multiprocessing

def calculate_sum(n, m, result_queue):
    count = 0
    for i in range(n, m):
        count = count + i
    result_queue.put(count) # this queue is used so taht like , we can add up the count properly 

if __name__ == "__main__":
    PID = os.getpid()
    process = psutil.Process(PID)
    start = 10
    end = 200000000
    num_chunks = 3

    # Integer division
    chunk_size = (end - start) // num_chunks

    # -----------------------------
    # Divide the work into 3 chunks
    # -----------------------------

    chunk1 = (
        start,
        start + chunk_size
    )

    chunk2 = (
        start + chunk_size,
        start + 2 * chunk_size
    )

    chunk3 = (
        start + 2 * chunk_size,
        end
    )

    print("Chunks:")
    print("Process 1:", chunk1)
    print("Process 2:", chunk2)
    print("Process 3:", chunk3)
    result_queue = multiprocessing.Queue()
    # -----------------------------
    # Create the 3 processes
    # -----------------------------

    p1 = multiprocessing.Process(
        target=calculate_sum,
        args=(chunk1[0], chunk1[1], result_queue)
    )

    p2 = multiprocessing.Process(
        target=calculate_sum,
        args=(chunk2[0], chunk2[1], result_queue)
    )

    p3 = multiprocessing.Process(
        target=calculate_sum,
        args=(chunk3[0], chunk3[1], result_queue)
    )

    # -----------------------------
    # Take start snapshots
    # -----------------------------

    wall_start = time.perf_counter()
    cpu_start = process.cpu_times()

    p1.start()
    p2.start()
    p3.start()
    p1.join()
    p2.join()
    p3.join()

 
    result1 = result_queue.get()
    result2 = result_queue.get()
    result3 = result_queue.get()

    Count = result1 + result2 + result3
    wall_end = time.perf_counter()
    cpu_end = process.cpu_times() 
    print(wall_end-wall_start)
    