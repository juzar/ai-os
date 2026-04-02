import subprocess

def run(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout

def check_azure_vms():
    return run("az vm list -o table")

def check_ec2():
    return run("aws ec2 describe-instances")