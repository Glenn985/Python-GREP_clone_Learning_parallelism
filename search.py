import time


def Search(file_path, restrictions, text):
    """Line-by-line text search (case-sensitive unless ~a present)."""
    print("searching using Search()")
    try:
        s = time.process_time()
        Wall_clock_time = time.perf_counter()

        with open(file_path, "r") as f:
            count = 0
            if "~a" in restrictions:
                for line in f:
                    if text.lower() in line.lower():
                        count = count + line.lower().count(text.lower())
            else:
                for line in f:
                    if text in line:
                        count = count + line.count(text)

        print("NO of recurrences", count)
        print("Time taken:", time.process_time() - s)
        print("Wall clock time taken:", time.perf_counter() - Wall_clock_time)

    except FileNotFoundError:
        print(f"File does not exist: {file_path}")

    except PermissionError:
        print(f"Permission denied: {file_path}")

    except UnicodeDecodeError:
        print(f"Could not decode file: {file_path}")
