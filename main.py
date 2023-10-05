import os
import hashlib

files = os.listdir(os.getcwd())
print(files)

l = [x for x in files if os.path.isfile(f"{os.getcwd()}/{x}")]
print(l)


lst = [hashlib.md5(f.read()).hexdigest() for f in l]
print(lst)