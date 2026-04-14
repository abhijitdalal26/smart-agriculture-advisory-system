import paramiko
import time
import sys

HOSTNAME = "ess.local"
USERNAME = "ess"
PASSWORD = "2026"
WORKSPACE_DIR = "/home/ess/.openclaw/workspace"
REPO_URL = "https://github.com/abhijitdalal26/smart-agriculture-advisory-system.git"

print("Init connecting to Pi...")
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(HOSTNAME, username=USERNAME, password=PASSWORD, timeout=10)
    print("Connected successfully!")
    
    commands = [
        f"mkdir -p {WORKSPACE_DIR}",
        f"cd {WORKSPACE_DIR} && if [ ! -d 'smart-agriculture-advisory-system' ]; then git clone {REPO_URL}; else echo 'Repository already exists. Pulling latest.'; cd smart-agriculture-advisory-system && git pull; fi",
        f"ls -l {WORKSPACE_DIR}/smart-agriculture-advisory-system"
    ]
    
    for cmd in commands:
        print(f"Executing: {cmd}")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        
        exit_status = stdout.channel.recv_exit_status()
        out = stdout.read().decode().strip()
        err = stderr.read().decode().strip()
        
        if out: print(f"Output: {out}")
        if err: print(f"Error: {err}")
        print(f"Exit status: {exit_status}\n")
        
except Exception as e:
    print(f"Failed to connect or execute: {e}")
    sys.exit(1)
finally:
    ssh.close()
