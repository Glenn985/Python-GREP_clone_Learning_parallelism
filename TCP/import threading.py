import threading

counter = 0

def bump():
    global counter
    for _ in range(100000):
        counter += 1

threads = [threading.Thread(target=bump) for _ in range(5)]

[t.start() for t in threads]
[t.join() for t in threads]

print(counter)
