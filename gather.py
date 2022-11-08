#!/usr/bin/env python3

import os
import subprocess
import json

def get_file_list():
    subprocess.run("ssh root@localhost -p 43000 python3 make_gmap.py", shell = True)
    remote_ls = subprocess.run("ssh root@localhost -p43000 ls /root/walkmaps | grep html", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, universal_newlines = True)
    if remote_ls.returncode == 0:
        obs = []
        split_lines = remote_ls.stdout.split("\n")
        for x in split_lines:
            for o in x.split(" "):
                if o:
                    obs.append(o)
                print(o)

        return obs
    else:
        print("Got bad return from command!")
        print(remote_ls.stdout)
        return []

def gather_missing():
    os.chdir("/var/www/html")
    for file in get_file_list():
        if not file in os.listdir("/var/www/html"):
            print(f"Gathering missing file {file}")
            subprocess.run("scp -P43000 root@localhost:/root/walkmaps/" + file + " /var/www/html", shell = True)
            os.chdir("/var/www/html")
    subprocess.run("python3 makeindex.py", shell = True)


if __name__ == "__main__":
    gather_missing()
