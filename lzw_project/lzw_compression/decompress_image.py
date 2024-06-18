from PIL import Image
import numpy as np
from lzw import lzw_decompress
import os

def decompress_image(input_file, output_file):
    with open(input_file, 'rb') as f:
        width = int.from_bytes(f.read(4), byteorder='big')
        height = int.from_bytes(f.read(4), byteorder='big')
        
        compressed_data = []
        while True:
            byte = f.read(2)
            if not byte:
                break
            compressed_data.append(int.from_bytes(byte, byteorder='big'))

    decompressed_data = lzw_decompress(compressed_data)
    img_flat = np.array(list(decompressed_data), dtype=np.uint8)
    img_data = img_flat.reshape((height, width))
    img = Image.fromarray(img_data)
    
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    img.save(output_file) 