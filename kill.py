import os
import sys

# Code to kill the server at port 2301

output = os.popen("netstat -aon | findstr :2301").read().split(" ")[-1][:-1]
if output:
    os.system(f"taskkill /PID {output} /F")
else:
    print("No server running")




