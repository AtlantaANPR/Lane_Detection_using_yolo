import json
import os
from PIL import Image

# === CONFIG ===
json_paths = {
    "train": "dataset/labels/drivable_labels/polygons/drivable_train.json",
    "val": "dataset/labels/drivable_labels/polygons/drivable_val.json"
}

image_dirs = {
    "train": "/home/atlanta/Downloads/Lane_Training/dataset/train/images",
    "val": "/home/atlanta/Downloads/Lane_Training/dataset/val/images"
}

output_label_dirs = {
    "train": "/home/atlanta/Downloads/Lane_Training/dataset/train/labels",
    "val": "/home/atlanta/Downloads/Lane_Training/dataset/val/labels"
}

# === Create label folders if not exist ===
for path in output_label_dirs.values():
    os.makedirs(path, exist_ok=True)

# === Conversion function ===
def convert(json_path, image_dir, label_dir):
    with open(json_path, "r") as f:
        data = json.load(f)

    for item in data:
        img_name = item["name"]
        img_path = os.path.join(image_dir, img_name)
        label_path = os.path.join(label_dir, img_name.replace(".jpg", ".txt").replace(".png", ".txt"))

        # Get image size
        if not os.path.exists(img_path):
            print(f"Image not found: {img_path}")
            continue
        img = Image.open(img_path)
        w, h = img.size

        with open(label_path, "w") as lf:
            for label in item.get("labels", []):
                for poly in label.get("poly2d", []):
                    points = poly["vertices"]
                    norm_points = [str(round(x / w, 6)) + " " + str(round(y / h, 6)) for x, y in points]
                    flat_coords = " ".join([" ".join(p.split()) for p in norm_points])
                    lf.write(f"0 {flat_coords}\n")  # Class ID 0 for all
    print(f"✓ Converted: {json_path}")

# === Run conversion ===
for split in ["train", "val"]:
    convert(json_paths[split], image_dirs[split], output_label_dirs[split])
