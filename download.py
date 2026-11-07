import paramiko
from pathlib import Path
import os

SERVER_IP= os.environ["SERVER_IP"]
SSH_USER=os.environ.get["SSH_USER","ubuntu"]
KEY_FILE=os.environ.get["KEY_FILE","sonarkey1.pem"]



def connect(host,user,key,timeout=15):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(host, username=user, key_filename=key, timeout=15)
        return ssh
        
    # except FileNOtFoundError:
    #     problem = (f"key file not found: {key}\n   Fix: check the path to your .pem file.")
    except socket.timeout:
        problem = (f"Connection to {host} timed out.")


def download_log(ip, user, key, source_path="/var/log/nginx/access.log", dest_path="access.log"):
                 # connect to the server
                 ssh = connect(ip, user, key)

                 # copy the access log to the tmp folder
                 stdin, stdout, stderr = ssh.exec_command(f"sudo cp {source_path} /tmp/access.log")
                 stdout.read()

                 # make the file downloadable
                 stdin, stdout, stderr = ssh.exec_command("sudo chmod 777 /tmp/access.log")
                 stdout.read()

                 # Download it to the local system.
                 sftp = ssh.open_sftp()
                 sftp.get("/tmp/access.log", dest_path)
                 sftp.close()


                  # Delete the file from tmp folder
                 stdin, stdout, stderr = ssh.exec_command("sudo rm /tmp/access.log")
                 stdout.read()
                 ssh.close()

                 print(f" Completed downloading file from {source_path} to {dest_path}")


download_log(SERVER_IP,SSH_USER,KEY_FILE)
