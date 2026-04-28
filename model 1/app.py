from flask import Flask, request, render_template, redirect, jsonify
import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
import os
import cv2
import numpy as np

app = Flask(__name__)

# Number of Decease goes here =>
num_classes = 5

# Loading... the trained model =>
model = models.resnet50(pretrained=False)
num_ftrs = model.fc.in_features
model.fc = nn.Linear(num_ftrs, num_classes)
model.load_state_dict(torch.load('models/skin_disease_model.pth', map_location=torch.device('cpu')))
model.eval()

# Defining transform =>
img_width, img_height = 150, 150
transform = transforms.Compose([
    transforms.Resize((img_width, img_height)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])


def is_skin_image(image_path):
    """
    Validates if uploaded image contains human skin using HSV color space analysis.
    
    Returns True if reasonable percentage of pixels fall within skin tone range.
    Returns False if image is invalid, empty, or non-skin.
    """
    try:
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            return False
        
        # Convert BGR to HSV
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Define skin tone ranges in HSV (more inclusive for various skin tones)
        # Lower range: H 0-25, S 10-60%, V 30-100%
        # Upper range: H 155-180, S 10-60%, V 30-100%
        lower_skin1 = np.array([0, 10, 30], dtype=np.uint8)
        upper_skin1 = np.array([25, 200, 255], dtype=np.uint8)
        lower_skin2 = np.array([155, 10, 30], dtype=np.uint8)
        upper_skin2 = np.array([180, 200, 255], dtype=np.uint8)
        
        # Create masks for both ranges
        mask1 = cv2.inRange(hsv, lower_skin1, upper_skin1)
        mask2 = cv2.inRange(hsv, lower_skin2, upper_skin2)
        mask = cv2.bitwise_or(mask1, mask2)
        
        # Calculate percentage of skin pixels
        skin_pixels = cv2.countNonZero(mask)
        total_pixels = img.shape[0] * img.shape[1]
        skin_percentage = (skin_pixels / total_pixels) * 100
        
        # Check for minimum skin coverage (10% threshold)
        if skin_percentage < 10:
            return False
        
        # Check image variance to avoid flat/blank images
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        variance = cv2.Laplacian(gray, cv2.CV_64F).var()
        if variance < 50:
            return False
        
        return True
        
    except Exception as e:
        print(f"Validation error: {e}")
        return False


# Disease Information Dictionary (Post-processing Layer)
disease_info = {
    'Acne': {
        'description': 'Acne is a common skin condition characterized by pimples, blackheads, and whiteheads. It occurs when hair follicles become clogged with dead skin cells and sebum.',
        'tips': 'Keep skin clean and dry. Use non-comedogenic products. Avoid touching your face. Maintain a healthy diet and manage stress.',
        'risk': 'Low',
        'advice': 'See a dermatologist if acne persists or worsens. Over-the-counter treatments with benzoyl peroxide or salicylic acid may help.'
    },
    'Hairloss': {
        'description': 'Hair loss can result from genetics, stress, hormonal changes, or nutritional deficiencies. It may be temporary or permanent.',
        'tips': 'Manage stress through exercise and meditation. Ensure adequate protein and iron intake. Avoid harsh treatments and tight hairstyles.',
        'risk': 'Medium',
        'advice': 'Consult a dermatologist if experiencing rapid or unusual hair loss. Blood tests may be recommended to check for deficiencies.'
    },
    'Nail Fungus': {
        'description': 'Nail fungus (onychomycosis) is an infection that causes nails to thicken, discolor, and become brittle. It spreads slowly and is contagious.',
        'tips': 'Keep nails trimmed and dry. Wear breathable shoes. Avoid public pools and communal areas. Use antifungal powder if prone to moisture.',
        'risk': 'Medium',
        'advice': 'See a dermatologist for prescription antifungal treatment. Topical treatments alone may not be sufficient for deep infections.'
    },
    'Normal': {
        'description': 'Your skin appears healthy with no significant dermatological conditions detected. Maintain good skincare habits.',
        'tips': 'Use a gentle cleanser twice daily. Apply moisturizer suited to your skin type. Use SPF 30+ sunscreen daily. Stay hydrated.',
        'risk': 'Low',
        'advice': 'Continue regular skincare routine. No immediate medical intervention needed. Annual check-ups with a dermatologist are recommended.'
    },
    'Skin Allergy': {
        'description': 'Skin allergies cause itching, redness, and irritation when exposed to allergens. Common triggers include cosmetics, fabrics, and plants.',
        'tips': 'Identify and avoid triggers. Use hypoallergenic products. Wear cotton clothing. Keep skin moisturized and avoid harsh soaps.',
        'risk': 'Low',
        'advice': 'Apply cool compresses and hydrocortisone cream for relief. See a dermatologist if symptoms persist or worsen.'
    }
}


def get_disease_info(disease_name):
    """Fetch disease information from dictionary with fallback message."""
    return disease_info.get(disease_name, {
        'description': 'This condition requires further medical evaluation.',
        'tips': 'Consult with a healthcare professional for personalized advice.',
        'risk': 'Unknown',
        'advice': 'Schedule an appointment with a dermatologist for proper diagnosis and treatment.'
    })


def predict_skin_disease(image_path):
    img = Image.open(image_path).convert('RGB')
    img = transform(img).unsqueeze(0)
    with torch.no_grad():
        outputs = model(img)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)
        confidence, predicted = torch.max(probabilities.data, 1)
    class_labels = {
        0: 'Acne',
        1: 'Hairloss',
        2: 'Nail Fungus',
        3: 'Normal',
        4: 'Skin Allergy'
    }
    confidence_percent = round(confidence.item() * 100, 2)
    return class_labels[predicted.item()], confidence_percent


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file:
            file_path = os.path.join('uploads', file.filename)
            file.save(file_path)
            
            # VALIDATION: Check if image contains skin
            if not is_skin_image(file_path):
                return jsonify({
                    "error": "Invalid input. Please upload a clear skin image."
                }), 400
            
            # PREDICTION: Continue with model prediction
            prediction, confidence = predict_skin_disease(file_path)
            
            # POST-PROCESSING: Fetch disease information
            info = get_disease_info(prediction)
            
            # Confidence interpretation
            if confidence > 80:
                confidence_text = 'High confidence prediction'
            elif confidence > 50:
                confidence_text = 'Moderate confidence'
            else:
                confidence_text = 'Low confidence — result may be uncertain'
            
            return render_template('result.html', 
                prediction=prediction,
                confidence=confidence,
                confidence_text=confidence_text,
                description=info['description'],
                tips=info['tips'],
                risk=info['risk'],
                advice=info['advice'])
    return render_template('upload.html')


if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)
