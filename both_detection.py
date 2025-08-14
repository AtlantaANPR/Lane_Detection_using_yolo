import os
import json
import shutil
from PIL import Image

# =========================
# Paths
# =========================
old_dataset = "dataset"  # Original dataset path
train_json = "vehicle_train_combined.json"
val_json = "vehicle_val_combined.json"
new_dataset = "dataset_lane_vehicle"

# =========================
# Create new dataset structure
# =========================
for split in ["train", "val"]:
    os.makedirs(f"{new_dataset}/{split}/images", exist_ok=True)
    os.makedirs(f"{new_dataset}/{split}/labels", exist_ok=True)

# =========================
# JSON load function
# =========================
def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

# =========================
# BBox → Polygon convert (normalized)
# =========================
def bbox_to_polygon(x1, y1, x2, y2, img_w, img_h):
    # Normalize values between 0-1
    x1 /= img_w
    y1 /= img_h
    x2 /= img_w
    y2 /= img_h
    # Return polygon as 4 points
    return [x1, y1, x2, y1, x2, y2, x1, y2]

# =========================
# Extract vehicle labels from JSON
# =========================
def extract_vehicle_labels(json_list, img_sizes):
    vehicle_data = {}
    for img_obj in json_list:
        file_name = img_obj["name"]
        img_w, img_h = img_sizes[file_name]

        # Safely get labels
        labels = img_obj.get("labels", [])
        if not labels:
            continue

        for label in labels:
            if label["category"].lower() == "vehicle":
                box = label["box2d"]
                polygon = bbox_to_polygon(box["x1"], box["y1"], box["x2"], box["y2"], img_w, img_h)
                label_line = "1 " + " ".join([f"{p:.6f}" for p in polygon])
                
                if file_name not in vehicle_data:
                    vehicle_data[file_name] = []
                vehicle_data[file_name].append(label_line)
    return vehicle_data

# =========================
# Process dataset (train/val)
# =========================
def process_dataset(split, json_path):
    # Load JSON
    json_list = load_json(json_path)

    # Get image sizes
    img_sizes = {}
    img_dir = os.path.join(old_dataset, split, "images")
    for img_file in os.listdir(img_dir):
        img_path = os.path.join(img_dir, img_file)
        with Image.open(img_path) as img:
            img_sizes[img_file] = img.size  # (width, height)

    # Extract vehicle labels
    vehicle_labels = extract_vehicle_labels(json_list, img_sizes)

    for img_obj in json_list:
        file_name = img_obj["name"]

        # Copy image
        src_img = os.path.join(old_dataset, split, "images", file_name)
        dst_img = os.path.join(new_dataset, split, "images", file_name)
        shutil.copy(src_img, dst_img)

        # Copy lane label
        label_name = file_name.rsplit(".", 1)[0] + ".txt"
        src_label = os.path.join(old_dataset, split, "labels", label_name)
        dst_label = os.path.join(new_dataset, split, "labels", label_name)
        shutil.copy(src_label, dst_label)

        # Add vehicle labels
        if file_name in vehicle_labels:
            with open(dst_label, "a") as f:
                for v_label in vehicle_labels[file_name]:
                    f.write("\n" + v_label)

# =========================
# Run for train & val
# =========================
process_dataset("train", train_json)
process_dataset("val", val_json)

print("✅ New dataset with lanes + vehicles created:", new_dataset)
