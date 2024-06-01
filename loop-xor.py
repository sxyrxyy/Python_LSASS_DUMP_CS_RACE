import os
import time

def xor_file(input_file, output_file, key=0xFF):
    try:
        with open(input_file, 'rb') as f:
            data = f.read()
        xor_data = bytearray([b ^ key for b in data])
        with open(output_file, 'wb') as f:
            f.write(xor_data)
    except Exception as e:
        print(f"An error occurred: {e}")

input_filename = "Please_XOR.txt"
output_filename = "xored_dump.txt"

while True:
    if os.path.exists(input_filename):
        xor_file(input_filename, output_filename)
        print(f"File {input_filename} XORed and saved to {output_filename}")
    else:
        print('File not found.')
    time.sleep(0.1)
