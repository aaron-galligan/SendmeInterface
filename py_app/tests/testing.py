
import os
print("Current working directory:", os.getcwd())


f = open("C:/Users/aaron/OneDrive/Documents/Programming/Rust/SendmeInterface/py_app/flag.png", "rb")
bytes = bytearray(f.read())
print(bytes)
f.close()