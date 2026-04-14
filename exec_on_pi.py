import paramiko
import sys
import argparse

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def run_command_on_pi(command):
    HOSTNAME = "10.186.162.189"
    USERNAME = "ess"
    PASSWORD = "2026"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOSTNAME, username=USERNAME, password=PASSWORD, timeout=10)
        
        if command.startswith('UPLOAD:'):
            local_path, remote_path = command[7:].split('->')
            sftp = ssh.open_sftp()
            sftp.put(local_path.strip(), remote_path.strip())
            sftp.close()
            print(f"Uploaded {local_path} to {remote_path}")
            sys.exit(0)
            
        stdin, stdout, stderr = ssh.exec_command(command)
        
        exit_status = stdout.channel.recv_exit_status()
        out = stdout.read().decode('utf-8', errors='replace').strip()
        err = stderr.read().decode('utf-8', errors='replace').strip()
        
        if out: print(out)
        if err: print(err, file=sys.stderr)
        
        sys.exit(exit_status)
        
    except Exception as e:
        print(f"SSH Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        ssh.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", help="The command to execute on the Pi")
    args = parser.parse_args()
    
    run_command_on_pi(args.command)
