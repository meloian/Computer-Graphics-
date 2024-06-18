import os
import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
from PIL import Image
import compress_image
import decompress_image
import math

def create_folders():
    if not os.path.exists('compressed_images'):
        os.makedirs('compressed_images')
    if not os.path.exists('decompressed_images'):
        os.makedirs('decompressed_images')
    if not os.path.exists('grayscale_images'):
        os.makedirs('grayscale_images')

def select_image():
    root = tk.Tk()
    root.withdraw()
    image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.tif")])
    return image_path

def show_images(original_path, decompressed_path, compressed_size, original_size, entropy, max_code_used, compression_ratio):
    original_img = Image.open(original_path)
    decompressed_img = Image.open(decompressed_path)
    max_achievable_compression = math.log2(256) / entropy if entropy != 0 else 0

    fig, axs = plt.subplots(1, 2, figsize=(12, 6))

    axs[0].imshow(original_img, cmap='gray')
    axs[0].set_title(f'Original Image\nSize: {original_size / 1024:.2f} KB')
    axs[0].axis('off')

    axs[1].imshow(decompressed_img, cmap='gray')
    axs[1].set_title(f'Decompressed Image\nSize: {os.path.getsize(decompressed_path) / 1024:.2f} KB')
    axs[1].axis('off')

    info_text = (
        f'Compression Ratio: {compression_ratio:.2f}, Entropy: {entropy:.2f}\n'
        f'Max Achievable Compression: {max_achievable_compression:.2f}, Maximum Dictionary Code Used: {max_code_used}'
    )
    plt.figtext(0.5, 0.03, info_text, ha='center', fontsize=12)
    plt.subplots_adjust(bottom=0.2)
    plt.show()

def main():
    create_folders()

    original_image_path = select_image()
    if not original_image_path:
        print("No image selected!")
        return

    filename = os.path.basename(original_image_path).rsplit('.', 1)[0]
    grayscale_image_path = os.path.join('grayscale_images', filename + "_grayscale.png")
    compressed_image_path = os.path.join('compressed_images', filename + ".lzw")
    decompressed_image_path = os.path.join('decompressed_images', filename + "_decompressed.png")

    img = Image.open(original_image_path).convert('L')
    img.save(grayscale_image_path)

    original_size = os.path.getsize(grayscale_image_path)
    compressed_size, entropy, max_code_used, compression_ratio = compress_image.compress_image(grayscale_image_path, compressed_image_path)
    decompress_image.decompress_image(compressed_image_path, decompressed_image_path)

    show_images(grayscale_image_path, decompressed_image_path, compressed_size, original_size, entropy, max_code_used, compression_ratio)
    print(f"Image compressed to {compressed_image_path}")
    print(f"Image decompressed to {decompressed_image_path}")

if __name__ == "__main__":
    main() 