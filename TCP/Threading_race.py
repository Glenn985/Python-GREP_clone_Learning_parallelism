import threading
import time

counter = 0

def bump():
    global counter

    for i in range(10000):
        temp = counter      # READ
        time.sleep(0)        #  we ARE MAKING ANOTHER THREAD RUN, entirely
        counter = temp + 1  # WRITE

threads = [threading.Thread(target=bump) for _ in range(3)]

for t in threads:
    t.start()

for t in threads:
    t.join()

print("Expected:", 30000)
print("Actual:  ", counter)