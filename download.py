import os
import socket
import paramiko

SERVER_IP = os.environ["SERVER_IP"]
SSH_USER  = os.environ.get("SSH_USER", "ubuntu")
KEY_FILE  = os.environ.get("KEY_FILE", "sonarkey1.pem")


def connect(host, user, key, timeout=15):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(host, username=user, key_filename=key, timeout=timeout)
        return ssh
    except FileNotFoundError:
        problem = f"Key file not found: {key}. Fix: check the path to your .pem file."
    except paramiko.AuthenticationException:
        problem = f"Login refused for user '{user}'. Fix: check the key and the user name."
    except (socket.timeout, paramiko.ssh_exception.NoValidConnectionsError):
        problem = f"Cannot reach {host} on port 22. Fix: check the IP and the security group."

    ssh.close()
    raise ConnectionError("Error" + problem)


def download_log(ip, user, key, source_path="/var/log/nginx/access.log", dest_path="access.log"):
    # connect to the server
    ssh = connect(ip, user, key)

    # copy the access log to the tmp folder
    stdin, stdout, stderr = ssh.exec_command(f"sudo cp {source_path} /tmp/access.log")
    stdout.read()

    # make the file readable so it can be downloaded
    stdin, stdout, stderr = ssh.exec_command("sudo chmod 644 /tmp/access.log")
    stdout.read()

    # download it to the local system
    sftp = ssh.open_sftp()
    sftp.get("/tmp/access.log", dest_path)
    sftp.close()

    # delete the file from the tmp folder
    stdin, stdout, stderr = ssh.exec_command("sudo rm /tmp/access.log")
    stdout.read()
    ssh.close()

    print(f"Completed downloading file from {source_path} to {dest_path}")


if __name__ == "__main__":
    download_log(SERVER_IP, SSH_USER, KEY_FILE)
