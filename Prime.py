import os
import time
import psutil
import multiprocessing


def calculate_sum(n, m, result_queue):
    count = 0
    for i in range(n, m):
        count = count + i
    result_queue.put(count)

def calculate_sum_NoProcess(n, m):
    count = 0
    for i in range(n, m):
        count = count + i
    return count


if __name__ == "__main__":
    start = 10
    end = 2000000
    num_chunks = 3

    chunk_size = (end - start) // num_chunks
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


    result_queue = multiprocessing.Queue() #ibrary to automaticaly share the value, we cant use a normla queu, 
    #as data can get lost, deu to it beign sepearte

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
    wall_start = time.perf_counter()
    p1.start()
    p2.start()
    p3.start()
    p1.join()
    p2.join()
    p3.join()
    # Get results from child processes
    result1 = result_queue.get()
    result2 = result_queue.get()
    result3 = result_queue.get()

    Count = result1 + result2 + result3
    wall_end = time.perf_counter()
    print()
    print("MULTIPROCESS")
    print("Result:", Count)
    print("Wall time:", wall_end - wall_start)

    wall_start1 = time.perf_counter()
    Count_NoProcess = calculate_sum_NoProcess(start, end)
    wall_end1 = time.perf_counter()


    print()
    print("SINGLE PROCESS")
    print("Result:", Count_NoProcess)
    print("Wall time:", wall_end1 - wall_start1)