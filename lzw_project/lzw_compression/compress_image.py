from PIL import Image
import numpy as np
import os
import math
from lzw import lzw_compress

def calculate_entropy(img):
    unique, counts = np.unique(img, return_counts=True)
    counts = counts.astype(float)
    total_pixels = img.size
    probabilities = counts / total_pixels
    entropy = 0.0
    for p in probabilities:
        if p > 0:
            entropy -= p * np.log2(p)
    return entropy

def calculate_compression_ratio(encoded_img, height, width, max_dict_size):
    block_size = 1
    padded_height = height
    if height % block_size != 0:
        padded_height = height + block_size - (height % block_size)

    padded_width = width
    if width % block_size != 0:
        padded_width = width + block_size - (width % block_size)

    bits_in_original_img = padded_height * padded_width * 8
    bits_per_symbol = math.ceil(math.log2(max_dict_size))
    bits_in_encoded_img = len(encoded_img) * bits_per_symbol

    compression_ratio = bits_in_original_img / bits_in_encoded_img

    return compression_ratio

def compress_image(input_file, output_file):
    img = Image.open(input_file).convert('L')
    width, height = img.size
    img_data = np.array(img)
    
    max_dict_size = 4096
    
    flattened_data = img_data.flatten().astype(np.uint8)
    compressed_data, max_code_used = lzw_compress(flattened_data)
    entropy = calculate_entropy(img_data)
    
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    with open(output_file, 'wb') as f:
        f.write(width.to_bytes(4, byteorder='big'))
        f.write(height.to_bytes(4, byteorder='big'))
        for data in compressed_data:
            f.write(data.to_bytes(2, byteorder='big'))

    compression_ratio = calculate_compression_ratio(compressed_data, height, width, max_dict_size)

    return len(compressed_data) * 2, entropy, max_code_used, compression_ratio 