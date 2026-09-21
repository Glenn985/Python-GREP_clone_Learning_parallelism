import sys
import re
import os
import time
import psutil
import  readline
import subprocess
import cProfile
import pstats
import mmap
from multiprocessing import Process, Queue





def Search_MMAP(file_path, restrictions, text):
    print("searching using Search_MMAP()")
    try:
        s = time.process_time() 
        Wall_clock_time = time.perf_counter()
        text = text.encode()
        with open(file_path, "rb") as f:
            mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) #now the MM object is mapped into the memory, meaning virtual memoy
            # Gets the file descriptor of the file . This is basicly the ID of the file that we use to map . 
            if "~a" in restrictions: 
                content = mm[:].lower()
                count = content.count(text.lower())
            else:
                position = 0
                while True:
                    position = mm.find(text, position)
                    if position == -1:
                        break
                    count += 1
                    position += len(text)

        mm.close() # Close the memory-mapped object
        print("NO of recurrences", count)
        print("Time taken:", time.process_time() - s)
        print("Wall clock time taken:", time.perf_counter() - Wall_clock_time)

    except FileNotFoundError:
        print(f"File does not exist: {file_path}")
    except PermissionError:
        print(f"Permission denied: {file_path}")
    except UnicodeDecodeError: # i ahd trouble here becasue i was trying to read a non utf 8 file a wuith the text
        print(f"Could not decode file: {file_path}")





def search_from_bytes(file_path, offset, length, restrictions, text, q):

    start_cpu = time.process_time()

    with open(file_path, 'rb') as f:
        with mmap.mmap(
            f.fileno(),
            length=length,
            offset=offset,
            access=mmap.ACCESS_READ
        ) as mm:

            if "~a" in restrictions:
                content_lower = mm[:].lower()
                count = content_lower.count(text.lower().encode())
            else:
                count = mm.count(text.encode())

    end_cpu = time.process_time()

    cpu_time = end_cpu - start_cpu

    q.put((count, cpu_time, os.getpid()))





def Search_MultiProcess(file_path, restrictions, text):

    file_size = os.path.getsize(file_path)
    quarter = file_size // 4
    granularity = mmap.ALLOCATIONGRANULARITY

    offset1 = 0
    len1 = (quarter // granularity) * granularity

    offset2 = len1
    len2 = ((quarter * 2) // granularity) * granularity - offset2

    offset3 = offset2 + len2
    len3 = ((quarter * 3) // granularity) * granularity - offset3

    offset4 = offset3 + len3
    len4 = file_size - offset4

    q = Queue()

    p1 = Process(target=search_from_bytes, args=(file_path, offset1, len1, restrictions, text, q))
    p2 = Process(target=search_from_bytes, args=(file_path, offset2, len2, restrictions, text, q))
    p3 = Process(target=search_from_bytes, args=(file_path, offset3, len3, restrictions, text, q))
    p4 = Process(target=search_from_bytes, args=(file_path, offset4, len4, restrictions, text, q))

    start = time.perf_counter()

    p1.start()
    p2.start()
    p3.start()
    p4.start()

    p1.join()
    p2.join()
    p3.join()
    p4.join()

    wall = time.perf_counter() - start

    results = [q.get() for _ in range(4)]

    total_count = sum(r[0] for r in results)
    total_cpu = sum(r[1] for r in results)

    print("Count:", total_count)
    print("CPU time:", total_cpu)
    print("Wall time:", wall)




def Search(file_path, restrictions, text):  
    print("Normal search")

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



def SearchA(file_path, restrictions, text):
    print("SearchA entire thing into RAM not using Byte ")
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


    print("searching in NORMLA SERACH A")
    try:
        s = time.process_time() 
        Wall_clock_time = time.perf_counter()
        with open(file_path, "r") as f: 
            count = 0 
            if "~a" in restrictions: 
                content = f.read()
                if text.lower() in content.lower(): #this is bad coz Whole thing.lower()
                    count = content.lower().count(text.lower())
            else:
                content = f.read()
                if text in content:
                    count = content.count(text)
                    
        print("NO of recurrences", count)
        print("Time taken: SearchA", time.process_time() - s)
        print("Wall clock time taken SearchA:", time.perf_counter() - Wall_clock_time)


    except FileNotFoundError:
        print(f"File does not exist: {file_path}")

    except PermissionError:
        print(f"Permission denied: {file_path}")

    except UnicodeDecodeError: # i ahd trouble here becasue i was trying to read a non utf 8 file a wuith the text
        print(f"Could not decode file: {file_path}")



def SearchA_Process(file_path, restrictions, text): 
    print("Searching in binary mode")
    try:
        s = time.process_time() 
        Wall_clock_time = time.perf_counter()

        with open(file_path, "rb") as f: 
            count = 0 
            if "~a" in restrictions: 
                content = f.read()
                if text.lower().encode() in content.lower(): #this is bad coz Whole thing.lower()
                    count = content.lower().count(text.lower().encode())
            else:
                content = f.read()
                if text.encode() in content:
                    count = content.count(text.encode())
                    
        print("NO of recurrences", count)
        print("Time taken: SearchA", time.process_time() - s)
        print("Wall clock time taken SearchA_Binary:", time.perf_counter() - Wall_clock_time)



    except FileNotFoundError:
        print(f"File does not exist: {file_path}")

    except PermissionError:
        print(f"Permission denied: {file_path}")

    except UnicodeDecodeError: # i ahd trouble here becasue i was trying to read a non utf 8 file a wuith the text
        print(f"Could not decode file: {file_path}")




def SearchA_Binary(file_path, restrictions, text): 
    print("Searching in binary mode")
    try:
        s = time.process_time() 
        Wall_clock_time = time.perf_counter()

        with open(file_path, "rb") as f: 
            count = 0 
            if "~a" in restrictions: 
                content = f.read()
                if text.lower().encode() in content.lower(): #this is bad coz Whole thing.lower()
                    count = content.lower().count(text.lower().encode())
            else:
                content = f.read()
                if text.encode() in content:
                    count = content.count(text.encode())
                    
        print("NO of recurrences", count)
        print("Time taken: SearchA", time.process_time() - s)
        print("Wall clock time taken SearchA_Binary:", time.perf_counter() - Wall_clock_time)



    except FileNotFoundError:
        print(f"File does not exist: {file_path}")

    except PermissionError:
        print(f"Permission denied: {file_path}")

    except UnicodeDecodeError: # i ahd trouble here becasue i was trying to read a non utf 8 file a wuith the text
        print(f"Could not decode file: {file_path}")




if __name__ == "__main__":
 if len(sys.argv) < 3:
    print("There are not enough parameters")
    sys.exit()

 PID = os.getpid()

 p = psutil.Process(PID)

#p1 = psutil.Process(PID)
#time.sleep(2.8)  i tired using the time.sleep meothd but this is wrong because, it will sleep the entire process not just this becoz right now its a single thread 
#operation, meaning the whoel hting happens at once, so the sleep will sleep the entire process, and hence the CPU usage will be 0 for this process.


 p = psutil.Process()
 p.cpu_percent(interval=None)



 command = sys.argv[1]

 logical_cores = psutil.cpu_count(logical=True)
 physical_cores = psutil.cpu_count(logical=False)



 if command == "PGREP":
    print(sys.argv)
    command_pattern = r"~[a-zA-Z]"
    commands = " ".join(sys.argv) 

    restrictions = re.findall(command_pattern, commands)
    print(restrictions, "These are the restrictions")
    print(commands, "THESE ARE THE COMMANDS")
    print("WE ARE NOT PRINTING")

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

    print("FILE FOUND:", file_name)

    #Search(file_name, restrictions, text)
    #SearchA_Binary(file_name, restrictions, text)
    #SearchA(file_name, restrictions, text)
    #print("SAIS SO HOT")
    #Search_MMAP(file_name, restrictions, text)
    Search_MultiProcess(file_name, restrictions, text)


    #core_usage =psutil.Process(PID).cpu_percent(interval=.5, percpu=True) ##logic here is even tho the code is wrong
    # i want to get the CPU CORE USAGE FOR THIS PROCESS ALONE. ITS A MONITORING. 


    #print(f"Physical Cores: {physical_cores}")
    #print(f"Logical Cores (Threads): {logical_cores}")
    #print(f"Usage per Core: {core_usage}")

    print(p.cpu_times()) 
    cpu_used = p.cpu_percent(interval=None) 

    print(f"SearchA_Binary used roughly {cpu_used}% CPU")
    ## tbh the CPU usage here 
    ##During the wall-clock interval of that search, how much CPU execution
    #  time did this process accumulate relative to one logical CPU? 

    ## form the monitoring we got the thign that , SearchAbinary used roughly 91.5 percent of CPU< 
    ## BTW THIS DATA IS BASICLY SAYIGN ONLY ONE lgoical core was used NOT ALL 10 , all 10 wld mean 1000 perceut of the CPU
    # searching binary is more CPU bound than normal fiel search
    


# 
#     with cProfile.Profile() as pr: ## wahts this doign is it seeing waht functions in ur code gets called and how many times and how much time it took to execute, this is a profiling tool
#         # SearchA_Binary(file_name, restrictions, text)
#         SearchA(file_name, restrictions, text)
#         # Search(file_name, restrictions, text)
#         stats = pstats.Stats(pr)
#         stats.sort_stats(pstats.SortKey.TIME)  # Sort by CPU time
#         stats.print_stats()
# # 

