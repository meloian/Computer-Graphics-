from lzw import lzw_compress, lzw_decompress

def compress(input_string):
    input_bytes = input_string.encode('utf-8')
    compressed_data, _ = lzw_compress(input_bytes)
    return compressed_data

def decompress(compressed_data):
    decompressed_bytes = lzw_decompress(compressed_data)
    decompressed_string = decompressed_bytes.decode('utf-8')
    return decompressed_string

def main():
    input_string = 'ababcbababaaaaaa'
    
    compressed = compress(input_string)
    print("Compressed data:", compressed)
    
    decompressed = decompress(compressed)
    print("Decompressed string:", decompressed)
    
    if input_string == decompressed:
        print("Success: The original and decompressed strings are identical.")
    else:
        print("Error: The original and decompressed strings are different.")

if __name__ == "__main__":
    main() 