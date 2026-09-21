import sys
import re
import os
def Search(file_path, restrictions, text):
    try:
        with open(file_path, "r") as f:

            if "~a" in restrictions:
                content = f.read()
                if text.lower() in content.lower():
                    print(f"\nFound in: {file_path}")
                    print(content)

            else:
                content = f.read()

                if text in content:
                    print(f"\nFound in: {file_path}")
                    print(content)

    except FileNotFoundError:
        print(f"File does not exist: {file_path}")

    except PermissionError:
        print(f"Permission denied: {file_path}")

    except UnicodeDecodeError: # i ahd trouble here becasue i was trying to read a non utf 8 file a wuith the text
        print(f"Could not decode file: {file_path}")

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

    # os.walk automatically recursively goes through directories
    for root, directories, files in os.walk(path):
        for filename in files:
            if re.match(r"\w+\.txt$", filename):
                full_path = os.path.join(root, filename)
                print(f"Searching: {full_path}")
                Search(full_path, restrictions, text)



if len(sys.argv) < 3:
    print("There are not enough parameters")
    sys.exit()


command = sys.argv[1]


if command == "PGREP":
    print(sys.argv)
    command_pattern = r"~[a-zA-Z]"
    commands = " ".join(sys.argv)


    restrictions = re.findall(command_pattern, commands)
    print(restrictions, "These are the restrictions")
    print(commands, "THESE ARE THE COMMANDS")

    # The thing we are searching for is the last argument
    text = sys.argv[-1]
    if "~r" in restrictions:
        # Find a directory argument
        path = None

        for argument in sys.argv[2:-1]:

            # Ignore restrictions like ~r and ~a
            if not argument.startswith("~") and os.path.isdir(argument):
                path = argument
                break

        RecursiveSearch(path, restrictions, text)
    else:
        file_name = None
        for argument in sys.argv[2:-1]:

            if re.match(r".+\.\w+$", argument):
                file_name = argument
                break

        if file_name is None:
            print("No file name was provided")
            sys.exit()

        Search(file_name, restrictions, text)