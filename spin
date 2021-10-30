#!/usr/bin/env python3

import os
import subprocess
import time

processes = []
for i in range(8):
    processes.append(subprocess.Popen(["python3", "main.py", str(i)]))
    time.sleep(1)

while True:
    try:
        time.sleep(1)
    except:
        print("bye!")
        for process in processes:
            try:
                process.kill()
            except:
                pass
        exit(0)
