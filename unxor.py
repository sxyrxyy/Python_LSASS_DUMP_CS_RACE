import os

def unxor_file(input_file, output_file, key=0xFF):
    try:
        with open(input_file, 'rb') as f:
            data = f.read()
        unxor_data = bytearray([b ^ key for b in data])
        with open(output_file, 'wb') as f:
            f.write(unxor_data)
        print(f"File {input_file} un-XORed and saved to {output_file}")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    input_path = input("Enter the path to the XORed file: ")
    directory, filename = os.path.split(input_path)
    output_filename = os.path.splitext(filename)[0] + "_unxor" + os.path.splitext(filename)[1]
    output_path = os.path.join(directory, output_filename)
    unxor_file(input_path, output_path)

if __name__ == "__main__":
    main()
