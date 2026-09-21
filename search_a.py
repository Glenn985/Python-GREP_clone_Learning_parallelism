import time


def SearchA(file_path, restrictions, text):
    """Read-whole-file search. If '~a' in restrictions then case-insensitive."""
    print("searching in NORMAL SEARCH A")
    try:
        s = time.process_time()
        Wall_clock_time = time.perf_counter()
        with open(file_path, "r") as f:
            count = 0
            content = f.read()
            if "~a" in restrictions:
                if text.lower() in content.lower():
                    count = content.lower().count(text.lower())
            else:
                if text in content:
                    count = content.count(text)

        print("NO of recurrences", count)
        print("Time taken: SearchA", time.process_time() - s)
        print("Wall clock time taken SearchA:", time.perf_counter() - Wall_clock_time)

    except FileNotFoundError:
        print(f"File does not exist: {file_path}")

    except PermissionError:
        print(f"Permission denied: {file_path}")

    except UnicodeDecodeError:
        print(f"Could not decode file: {file_path}")
