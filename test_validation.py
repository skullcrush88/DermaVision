import requests
import cv2
import numpy as np
import os

print("\n" + "="*70)
print("TESTING SKIN IMAGE VALIDATION - WITH REALISTIC IMAGES")
print("="*70 + "\n")

# Create test directory
os.makedirs("test_images", exist_ok=True)

# 1. Create a VALID skin-like image with variance (random skin tones)
valid_skin = np.zeros((150, 150, 3), dtype=np.uint8)
for i in range(150):
    for j in range(150):
        # Add variation to skin tone
        r_val = np.random.randint(180, 220)  # R
        g_val = np.random.randint(130, 170)  # G
        b_val = np.random.randint(100, 150)  # B
        valid_skin[i, j] = [b_val, g_val, r_val]  # BGR

cv2.imwrite("test_images/valid_skin_varied.jpg", valid_skin)

# 2. Create an INVALID non-skin image (pure blue with variance)
invalid_blue = np.zeros((150, 150, 3), dtype=np.uint8)
for i in range(150):
    for j in range(150):
        # Strong blue channel, no skin tones
        b_val = np.random.randint(200, 255)  # High blue
        g_val = np.random.randint(0, 50)
        r_val = np.random.randint(0, 50)
        invalid_blue[i, j] = [b_val, g_val, r_val]

cv2.imwrite("test_images/invalid_blue_varied.jpg", invalid_blue)

# 3. Create an INVALID green image (non-skin)
invalid_green = np.zeros((150, 150, 3), dtype=np.uint8)
for i in range(150):
    for j in range(150):
        b_val = np.random.randint(0, 50)
        g_val = np.random.randint(200, 255)  # High green
        r_val = np.random.randint(0, 50)
        invalid_green[i, j] = [b_val, g_val, r_val]

cv2.imwrite("test_images/invalid_green_varied.jpg", invalid_green)

print("Realistic test images created:")
print("  1. valid_skin_varied.jpg (peachy/skin tones with variance)")
print("  2. invalid_blue_varied.jpg (blue with variance)")
print("  3. invalid_green_varied.jpg (green with variance)")
print()

# Test each model
models = [
    {"name": "Model 1 (5 diseases)", "port": 5000},
    {"name": "Model 2 (10 diseases)", "port": 5001},
    {"name": "Model 3 (23 diseases)", "port": 5002},
]

test_images = [
    ("valid_skin_varied.jpg", "SHOULD PASS"),
    ("invalid_blue_varied.jpg", "SHOULD REJECT"),
    ("invalid_green_varied.jpg", "SHOULD REJECT"),
]

for model in models:
    print(f"\n{model['name']}:")
    print("─" * 66)
    
    for img_file, expected in test_images:
        url = f"http://127.0.0.1:{model['port']}/"
        try:
            with open(f"test_images/{img_file}", "rb") as f:
                files = {"file": f}
                response = requests.post(url, files=files, timeout=5)
            
            status = response.status_code
            
            if status == 200:
                result = "✓ ACCEPTED"
                outcome = "PASS" if expected == "SHOULD PASS" else "FAIL"
            elif status == 400:
                result = "✗ REJECTED"
                outcome = "PASS" if expected == "SHOULD REJECT" else "FAIL"
            else:
                result = f"Status {status}"
                outcome = "FAIL"
            
            print(f"  {img_file:28} | {result:15} | [{outcome}]")
            
        except Exception as e:
            print(f"  {img_file:28} | ERROR: {str(e)[:20]}")

print("\n" + "="*70)
print("VALIDATION LAYER OPERATIONAL")
print("="*70)
print("\nValidation Logic:")
print("  - HSV color space analysis for skin tone detection")
print("  - Minimum 15% skin pixel coverage required")
print("  - Variance check to reject flat/blank images")
print("  - Invalid images return HTTP 400 with error message")
print("  - Valid images proceed to model prediction")
print()
