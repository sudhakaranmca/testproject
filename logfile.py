# python main.py -e one two three -x py tar.gz txt log -r 3 -d 10
import os
from datetime import date,timedelta
import subprocess
import time
import psutil
import pandas as pd
from copy import deepcopy
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('-e', '--env', action='store', dest='envlist',type=str, nargs='*',default=["one","two","three"])
parser.add_argument('-x', '--ext', action='store', dest='logext', type=str, nargs='*',default=["log","html","py","tar.gz"])
parser.add_argument('-r', '--lret', type=int, default=3)
parser.add_argument('-d', '--ddiff', type=int, default=10)

environment = parser.parse_args()

environments = environment.envlist
file_extensions = environment.logext
log_retension = environment.lret
date_difference = environment.ddiff

proc_filter =["nix-editor"]

files = []
file = open("log_file.html", "w")

pwd = os.getcwd()
to_date = str(date.today() - timedelta(days=log_retension))
from_date = str(date.today() - timedelta(days=date_difference))

def process_list(proc_filter):
    process_list = []
    for process in psutil.process_iter():
        try:
            if (len(proc_filter)==0):
              process_list.append([process.name(), process.pid, process.username(),process.cmdline()])
            if process.name() in proc_filter:
              if str(process.cmdline()).find("output"):
                process_list.append([process.name(), process.pid, process.username(),process.cmdline()])
              
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return process_list

def space_calc(bytes):

  for unit in ['','K','M','G','T','P']:
    if bytes < 1024:
      return f"{bytes:.2f}{unit}B"
    bytes /= 1024

def listfiles(rootpath):
    for env_name in os.listdir(rootpath):
        fullpath = os.path.join(rootpath,env_name)

        if os.path.isdir(fullpath):
            if env_name in environments:
              pwd = fullpath
              delete_log_file(from_date, to_date, file_extensions, pwd, env_name)
              listfiles(fullpath)
            else:
              listfiles(fullpath)


def delete_log_file(start_date, end_date, fext, pwd, env_name):
  from_date = start_date
  to_date = end_date
  file_details = {}

  for ext in fext:
    find = subprocess.Popen('find ' + pwd + ' -name *.' + ext + ' -newermt ' + from_date + ' ! -newermt ' + to_date , shell=True, stdout=subprocess.PIPE)
    #find = subprocess.Popen('find ' + pwd + ' -name *.' + ext + ' -type f -mtime ' + str(date_difference) , shell=True, stdout=subprocess.PIPE)
    for line in find.stdout:
       filename = line.decode('UTF-8').strip()
       filedetail = os.stat(filename)

       file_details["env_name"] = env_name
       file_details["filename"] = filename
       file_details["last_accessed"] = time.ctime(filedetail.st_atime)
       file_details["diskspace"] = space_calc(filedetail.st_size)
       files.append(deepcopy(file_details))
       #os.remove(line.decode('UTF-8').strip()) 
    find.communicate()  
    
def print_delete_log_file():
  df = pd.DataFrame.from_dict(files)
  html = df.to_html()
  file = open("log_file.html", "w")
  file.write(html)
  file.close()

if __name__ == "__main__":
  
  listfiles(pwd)
  print(files)
  print_delete_log_file()

  #for process in process_list(proc_filter):
  #  print(process)
