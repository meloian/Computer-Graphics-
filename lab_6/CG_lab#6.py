import tkinter as tk
from tkinter import filedialog, Label, Button, Entry, messagebox, Frame, LabelFrame
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw, ImageFont
import numpy as np

# create main window
app = tk.Tk()
app.title("Watermark and Text Embedding Tool")
app.geometry("1000x600")

app.grid_columnconfigure(1, weight=1)
app.grid_rowconfigure(0, weight=1)

# frames for input and output
input_frame = LabelFrame(app, text="Input", bd=2, relief="groove", padx=10, pady=10)
input_frame.grid(row=0, column=0, sticky="ns", padx=10, pady=10)

output_frame = LabelFrame(app, text="Output", bd=2, relief="groove", padx=10, pady=10)
output_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
output_frame.grid_columnconfigure(0, weight=1)
output_frame.grid_rowconfigure([0, 1, 2], weight=1)

container_image = None
watermark_image = None
result_image = None
extracted_watermark = None
extracted_container_image = None

def open_file():
    filepath = filedialog.askopenfilename()
    return filepath

def load_image(path):
    return Image.open(path)

def convert_to_binary(image):
    return image.convert("1")

def tile_watermark(container, watermark):
    container_width, container_height = container.size
    watermark_width, watermark_height = watermark.size
    tiled_watermark = Image.new('1', (container_width, container_height))

    if watermark_width > container_width or watermark_height > container_height:
        watermark = watermark.crop((0, 0, container_width, container_height))
        tiled_watermark.paste(watermark, (0, 0))
    else:
        for i in range(0, container_width, watermark_width):
            for j in range(0, container_height, watermark_height):
                tiled_watermark.paste(watermark, (i, j))

    return tiled_watermark

def embed_watermark(container, watermark, bit_plane):
    container = container.convert("RGB")
    container_np = np.array(container)
    watermark_np = np.array(watermark)
    blue_channel = container_np[:,:,2]
    mask = 1 << (bit_plane - 1)  # adjust for 1-based bit plane
    blue_channel = (blue_channel & ~mask) | ((watermark_np & 1) * mask)
    container_np[:,:,2] = blue_channel
    return Image.fromarray(container_np)

def extract_watermark(container, bit_plane):
    container = container.convert("RGB")
    container_np = np.array(container)
    blue_channel = container_np[:,:,2]
    extracted_bits = (blue_channel >> (bit_plane - 1)) & 1
    extracted_watermark = Image.fromarray((extracted_bits * 255).astype(np.uint8))
    return extracted_watermark

def remove_watermark(container, bit_plane):
    container = container.convert("RGB")
    container_np = np.array(container)
    blue_channel = container_np[:,:,2]
    mask = 1 << (bit_plane - 1)  # adjust for 1-based bit plane
    blue_channel = blue_channel & ~mask
    container_np[:,:,2] = blue_channel
    return Image.fromarray(container_np)

def text_to_binary(text):
    return ''.join(format(ord(char), '08b') for char in text)

def embed_text(container, text, bit_plane):
    container = container.convert("RGB")
    container_np = np.array(container)
    text_binary = text_to_binary(text)
    index = 0
    for i in range(container_np.shape[0]):
        for j in range(container_np.shape[1]):
            if index < len(text_binary):
                container_np[i, j, 2] = (container_np[i, j, 2] & ~(1 << (bit_plane - 1))) | (int(text_binary[index]) << (bit_plane - 1))
                index += 1
            if index >= len(text_binary):
                break

    return Image.fromarray(container_np)

def add_text_to_image(image, text, position, font_size, color):
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("arial.ttf", font_size)
    draw.text(position, text, font=font, fill=color)
    return image

def update_image(display_area, image):
    image.thumbnail((300, 300), Image.Resampling.LANCZOS)
    photo = ImageTk.PhotoImage(image)
    display_area.config(image=photo)
    display_area.image = photo

def process_watermark():
    global container_image, watermark_image, bit_plane_entry, result_image, result_display_label
    if not container_image or not watermark_image:
        messagebox.showerror("Error", "Please load both container and watermark images.")
        return
    bit_plane = int(bit_plane_entry.get())
    if bit_plane < 1 or bit_plane > 8:
        messagebox.showerror("Error", "Bit plane must be between 1 and 8.")
        return
    binary_watermark = convert_to_binary(watermark_image)
    tiled_watermark = tile_watermark(container_image, binary_watermark)
    result_image = embed_watermark(container_image, tiled_watermark, bit_plane)
    update_image(result_display_label, result_image)

def process_embedding():
    global container_image, text_entry, bit_plane_entry, result_image, result_display_label
    if not container_image:
        messagebox.showerror("Error", "Please load the container image.")
        return
    text = text_entry.get()
    bit_plane = int(bit_plane_entry.get())
    if bit_plane < 1 or bit_plane > 8:
        messagebox.showerror("Error", "Bit plane must be between 1 and 8.")
        return
    # embed text invisibly
    result_image = embed_text(container_image, text, bit_plane)
    # add visible text
    result_image = add_text_to_image(result_image, text, (10, 10), 20, (255, 255, 255))
    update_image(result_display_label, result_image)

def verify_embedding():
    global result_image, text_entry, bit_plane_entry
    if not result_image:
        messagebox.showerror("Error", "Please embed text first.")
        return
    text = text_entry.get()
    bit_plane = int(bit_plane_entry.get())
    if bit_plane < 1 or bit_plane > 8:
        messagebox.showerror("Error", "Bit plane must be between 1 and 8.")
        return

    # convert the text to binary
    text_binary = text_to_binary(text)
    
    # get the blue channel of the image
    container_np = np.array(result_image)
    blue_channel = container_np[:,:,2]

    # extract the embedded bits
    extracted_bits = []
    index = 0
    for i in range(container_np.shape[0]):
        for j in range(container_np.shape[1]):
            if index < len(text_binary):
                extracted_bit = (blue_channel[i, j] >> (bit_plane - 1)) & 1
                extracted_bits.append(str(extracted_bit))
                index += 1
            if index >= len(text_binary):
                break

    extracted_text_binary = ''.join(extracted_bits)
    
    # convert the binary string back to text
    extracted_text = ''.join(chr(int(extracted_text_binary[i:i+8], 2)) for i in range(0, len(extracted_text_binary), 8))

    if extracted_text == text:
        messagebox.showinfo("Success", "Text embedding verification successful.")
    else:
        messagebox.showerror("Error", f"Text embedding verification failed. Extracted text: {extracted_text}")

def extract_watermark_and_show():
    global result_image, bit_plane_entry, extracted_watermark, extracted_container_image, result_display_label, watermark_display_label, removed_watermark_display_label
    if not result_image:
        messagebox.showerror("Error", "Please embed a watermark first.")
        return
    bit_plane = int(bit_plane_entry.get())
    if bit_plane < 1 or bit_plane > 8:
        messagebox.showerror("Error", "Bit plane must be between 1 and 8.")
        return

    extracted_watermark = extract_watermark(result_image, bit_plane)
    extracted_container_image = remove_watermark(result_image, bit_plane)
    update_image(watermark_display_label, extracted_watermark)
    update_image(removed_watermark_display_label, extracted_container_image)
    messagebox.showinfo("Success", "Watermark extraction successful.")

def clear_output():
    global result_display_label, watermark_display_label, removed_watermark_display_label
    result_display_label.config(image='')
    result_display_label.image = None
    watermark_display_label.config(image='')
    watermark_display_label.image = None
    removed_watermark_display_label.config(image='')
    removed_watermark_display_label.image = None

def set_container_image():
    global container_image
    path = open_file()
    if path:
        container_image = load_image(path)
        update_image(container_label, container_image)

def set_watermark_image():
    global watermark_image
    path = open_file()
    if path:
        watermark_image = load_image(path)
        update_image(watermark_label, watermark_image)

# controls in the input frame
container_label = Label(input_frame)
container_label.pack(pady=5)

container_button = ttk.Button(input_frame, text="Load Container Image", command=set_container_image)
container_button.pack(fill='x', pady=5)

watermark_label = Label(input_frame)
watermark_label.pack(pady=5)

watermark_button = ttk.Button(input_frame, text="Load Watermark Image", command=set_watermark_image)
watermark_button.pack(fill='x', pady=5)

text_label = Label(input_frame, text="Enter Text:")
text_label.pack(pady=5)

text_entry = ttk.Entry(input_frame)
text_entry.pack(fill='x', pady=5)

bit_plane_label = Label(input_frame, text="Enter Bit Plane (1-8):")
bit_plane_label.pack(pady=5)

bit_plane_entry = ttk.Entry(input_frame)
bit_plane_entry.pack(fill='x', pady=5)

embed_watermark_button = ttk.Button(input_frame, text="Embed Watermark", command=process_watermark)
embed_watermark_button.pack(pady=5)

embed_text_button = ttk.Button(input_frame, text="Embed Text", command=process_embedding)
embed_text_button.pack(pady=5)

verify_button = ttk.Button(input_frame, text="Verify Embedding", command=verify_embedding)
verify_button.pack(pady=5)

extract_button = ttk.Button(input_frame, text="Extract Watermark", command=extract_watermark_and_show)
extract_button.pack(pady=5)

clear_button = ttk.Button(input_frame, text="Clear Output", command=clear_output)
clear_button.pack(pady=5)

result_display_label = Label(output_frame)
result_display_label.grid(row=0, column=0, sticky="nsew", pady=5)

watermark_display_label = Label(output_frame)
watermark_display_label.grid(row=1, column=0, sticky="nsew", pady=5)

removed_watermark_display_label = Label(output_frame)
removed_watermark_display_label.grid(row=2, column=0, sticky="nsew", pady=5)

app.mainloop() 