from PIL import Image, ExifTags
import os
import concurrent.futures

input_path = './images'
output_path = './edited-images'
target_filesize_kb = 500

if not os.path.exists(output_path):
    os.makedirs(output_path)

def fix_orientation(img):
    try:
        exif = img._getexif()
        orientation = exif.get(0x0112, 1)

        if orientation == 1:
            return img
        elif orientation == 3:
            return img.rotate(180, expand=True)
        elif orientation == 6:
            return img.rotate(270, expand=True)
        elif orientation == 8:
            return img.rotate(90, expand=True)
    except (AttributeError, KeyError, IndexError):
        pass
    return img

def process_image(input_image_path, output_image_path):
    with Image.open(input_image_path) as img:
        img = fix_orientation(img)
        img.thumbnail((1200, 1200), Image.LANCZOS)
        img.save(output_image_path, optimize=True, quality=95)
        
        original_size = os.path.getsize(input_image_path) / (1024*1024)
        output_size = os.path.getsize(output_image_path) / 1024
        print(f"{os.path.basename(input_image_path)} size reduced from {original_size:.2f}MB to {output_size:.2f}KB")

def process_images(input_image_paths, output_image_paths):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for input_image_path, output_image_path in zip(input_image_paths, output_image_paths):
            futures.append(executor.submit(process_image, input_image_path, output_image_path))
        for future in concurrent.futures.as_completed(futures):
            future.result()

image_files = [filename for filename in os.listdir(input_path) if filename.lower().endswith(('.jpg', '.jpeg', '.png'))]
input_image_paths = [os.path.join(input_path, filename) for filename in image_files]
output_image_paths = [os.path.join(output_path, filename) for filename in image_files]

process_images(input_image_paths, output_image_paths)
