
import os
print("Current working directory:", os.getcwd())

file_path = "C:/Users/aaron/OneDrive/Documents/Programming/Rust/SendmeInterface/py_app/flag.png"
file_name = os.path.basename(file_path)
print("File name:", file_name)

f = open(file_path, "rb")
bytes = bytearray(f.read())
#print(bytes)
f.close()