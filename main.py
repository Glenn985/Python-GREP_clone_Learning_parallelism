import sys
import re
import os
import psutil
import time

from search_a import SearchA
from search_binary import SearchA_Binary
from recursive_search import RecursiveSearch


def main(argv=None):
    if argv is None:
        argv = sys.argv

    if len(argv) < 3:
        print("There are not enough parameters")
        sys.exit()

    PID = os.getpid()
    p = psutil.Process(PID)
    p.cpu_percent(interval=None)

    command = argv[1]
    logical_cores = psutil.cpu_count(logical=True)
    physical_cores = psutil.cpu_count(logical=False)

    if command == "PGREP":
        print(argv)
        command_pattern = r"~[a-zA-Z]"
        commands = " ".join(argv)

        restrictions = re.findall(command_pattern, commands)
        print(restrictions, "These are the restrictions")
        print(commands, "THESE ARE THE COMMANDS")

        text = argv[-1]
        if "~r" in restrictions:
            path = None
            for argument in argv[2:-1]:
                if not argument.startswith("~") and os.path.isdir(argument):
                    path = argument
                    break
            RecursiveSearch(path, restrictions, text)
            return

        file_name = None
        for argument in argv[2:-1]:
            if re.match(r".+\.\w+$", argument):
                file_name = argument
                break

        if file_name is None:
            print("No file name was provided")
            sys.exit()

        print("FILE FOUND:", file_name)

        # choose binary or text search based on file extension or restriction
        if "~b" in restrictions:
            SearchA_Binary(file_name, restrictions, text)
        else:
            SearchA(file_name, restrictions, text)

        print(f"Physical Cores: {physical_cores}")
        print(f"Logical Cores (Threads): {logical_cores}")
        print(p.cpu_times())
        cpu_used = p.cpu_percent(interval=None)
        print(f"Search used roughly {cpu_used}% CPU")


if __name__ == "__main__":
    main()
