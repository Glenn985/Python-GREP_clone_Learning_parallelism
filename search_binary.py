import time


def SearchA_Binary(file_path, restrictions, text):
    """Binary-mode whole-file search. Encodes the search text to bytes."""
    print("Searching in binary mode")
    try:
        s = time.process_time()
        Wall_clock_time = time.perf_counter()

        with open(file_path, "rb") as f:
            count = 0
            content = f.read()
            if "~a" in restrictions:
                if text.lower().encode() in content.lower():
                    count = content.lower().count(text.lower().encode())
            else:
                if text.encode() in content:
                    count = content.count(text.encode())

        print("NO of recurrences", count)
        print("Time taken: SearchA", time.process_time() - s)
        print("Wall clock time taken SearchA_Binary:", time.perf_counter() - Wall_clock_time)

    except FileNotFoundError:
        print(f"File does not exist: {file_path}")

    except PermissionError:
        print(f"Permission denied: {file_path}")

    except UnicodeDecodeError:
        print(f"Could not decode file: {file_path}")
