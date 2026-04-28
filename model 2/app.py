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
num_classes = 10

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
    'Eczema': {
        'description': 'Eczema is a chronic inflammatory skin condition causing itching, redness, and dry patches. It often develops in childhood but can occur at any age.',
        'tips': 'Moisturize skin regularly with fragrance-free products. Take lukewarm baths/showers. Avoid harsh soaps and irritants. Manage stress.',
        'risk': 'Medium',
        'advice': 'See a dermatologist for proper diagnosis and treatment options including topical corticosteroids or immunosuppressants if needed.'
    },
    'Melanoma': {
        'description': 'Melanoma is a serious type of skin cancer that develops from melanocytes. It can spread to other parts of the body if not treated early.',
        'tips': 'Use SPF 30+ sunscreen daily. Avoid prolonged sun exposure. Perform monthly self-skin examinations. Wear protective clothing.',
        'risk': 'High',
        'advice': 'Seek immediate dermatological evaluation. Early detection is critical. Treatment options may include surgery, immunotherapy, or targeted therapy.'
    },
    'Atopic Dermatitis': {
        'description': 'Atopic dermatitis is a chronic inflammatory skin disease characterized by intense itching and skin barrier dysfunction.',
        'tips': 'Use hypoallergenic moisturizers frequently. Avoid irritating fabrics like wool. Take short warm showers. Reduce allergen exposure.',
        'risk': 'Medium',
        'advice': 'Consult a dermatologist for prescription treatments. Topical steroids, calcineurin inhibitors, or biologics may be recommended.'
    },
    'Basal Cell Carcinoma': {
        'description': 'Basal cell carcinoma is the most common type of skin cancer. It typically appears as a small, shiny bump or scar-like lesion.',
        'tips': 'Protect skin from UV rays. Use SPF 30+ daily. Avoid tanning beds. Check skin regularly for changes.',
        'risk': 'High',
        'advice': 'Visit a dermatologist immediately for biopsy and treatment. Most basal cell carcinomas are highly treatable when caught early.'
    },
    'Melanocytic Nevi': {
        'description': 'Melanocytic nevi are common moles that can be flat or raised. Most are benign, but some may have potential for malignancy.',
        'tips': 'Monitor moles for changes (ABCDE rule). Use sunscreen daily. Avoid excessive sun exposure. Document mole appearance with photos.',
        'risk': 'Low',
        'advice': 'Have suspicious moles evaluated by a dermatologist. Regular screening is recommended if you have multiple atypical nevi.'
    },
    'Benign Keratosis': {
        'description': 'Benign keratosis are common, non-cancerous growths that appear as waxy, scaly bumps on the skin. They are harmless but cosmetically bothersome.',
        'tips': 'Avoid picking or scratching lesions. Protect from sun exposure. Maintain good skin hygiene.',
        'risk': 'Low',
        'advice': 'No treatment needed unless for cosmetic reasons. Dermatologist can remove via cryotherapy, laser, or chemical peel if desired.'
    },
    'Psoriasis': {
        'description': 'Psoriasis is a chronic autoimmune condition causing thick, scaly, red or silvery patches on the skin.',
        'tips': 'Keep skin moisturized. Avoid triggers (stress, cold weather). Use sunscreen. Take warm baths with oatmeal.',
        'risk': 'Medium',
        'advice': 'Consult a dermatologist for treatment plans including topical treatments, phototherapy, or systemic medications.'
    },
    'Seborrheic Keratoses': {
        'description': 'Seborrheic keratoses are benign skin growths that appear waxy, scaly, and slightly raised. Common with aging.',
        'tips': 'Avoid sun exposure. Use sunscreen daily. Do not pick at lesions. Protect skin with clothing.',
        'risk': 'Low',
        'advice': 'No treatment required unless for cosmetic concerns. Dermatologist can safely remove via cryotherapy or laser treatment.'
    },
    'Tinea Ringworm': {
        'description': 'Tinea is a fungal infection causing ring-shaped, itchy, red patches. It is contagious and common in warm, moist areas.',
        'tips': 'Keep affected area clean and dry. Wear loose clothing. Avoid sharing personal items. Use antifungal powder.',
        'risk': 'Low',
        'advice': 'Use over-the-counter or prescription antifungal creams. See a doctor if infection spreads or doesn\'t improve in 2-3 weeks.'
    },
    'Warts Molluscum': {
        'description': 'Warts and molluscum are viral skin infections causing small bumps. They are contagious through direct contact.',
        'tips': 'Avoid touching or picking lesions. Wash hands frequently. Do not share personal items. Cover lesions when possible.',
        'risk': 'Low',
        'advice': 'Many resolve on their own. Dermatologist can treat with cryotherapy, laser, or topical treatments if needed.'
    }
}


def get_disease_info(disease_name):
    """Fetch disease information from dictionary with fallback message."""
    # Normalize disease names for matching
    clean_name = disease_name.split()[0] if ' ' in disease_name else disease_name
    
    for key in disease_info:
        if clean_name.lower() in key.lower() or key.lower() in disease_name.lower():
            return disease_info[key]
    
    return {
        'description': 'This condition requires further medical evaluation.',
        'tips': 'Consult with a healthcare professional for personalized advice.',
        'risk': 'Unknown',
        'advice': 'Schedule an appointment with a dermatologist for proper diagnosis and treatment.'
    }


def predict_skin_disease(image_path):
    img = Image.open(image_path).convert('RGB')
    img = transform(img).unsqueeze(0)
    with torch.no_grad():
        outputs = model(img)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)
        confidence, predicted = torch.max(probabilities.data, 1)
    class_labels = {
        0: 'Eczema',
        1: 'Melanoma',
        2: 'Atopic Dermatitis',
        3: 'Basal Cell Carcinoma',
        4: 'Melanocytic Nevi',
        5: 'Benign Keratosis',
        6: 'Psoriasis',
        7: 'Seborrheic Keratoses',
        8: 'Tinea Ringworm',
        9: 'Warts Molluscum',
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
    app.run(debug=True, port=5001)
