import os
import re
from search import Search


def RecursiveSearch(path, restrictions, text):
    if path is None:
        path = os.getcwd()
        print(
            "Didn't enter a path, hence using the current "
            "working directory as a path"
        )
    if not os.path.exists(path):
        print("Path does not exist")
        return

    for root, directories, files in os.walk(path):
        for filename in files:
            if re.match(r"\w+\.txt$", filename):
                full_path = os.path.join(root, filename)
                print(f"Searching: {full_path}")
                Search(full_path, restrictions, text)
