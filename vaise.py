import json

# Load your JSON file
with open("vehicle_train_combined.json", "r") as f:
    data = json.load(f)

# Since your JSON is a list with dictionaries
categories = set()

for item in data:
    for label in item.get("labels", []):
        categories.add(label.get("category", None))

# Print the unique categories
print("Unique categories:", categories)
print("Total unique categories:", len(categories))

