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
num_classes = 23

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
    'Acne and Rosacea': {
        'description': 'Acne and rosacea are skin conditions causing redness and bumps. Acne involves pimples and blackheads, while rosacea causes persistent facial flushing.',
        'tips': 'Use gentle cleansers and avoid triggers. Manage stress. Apply sunscreen daily. Avoid spicy foods and hot beverages.',
        'risk': 'Low',
        'advice': 'See a dermatologist for prescription treatments including retinoids, antibiotics, or laser therapy options.'
    },
    'Actinic Keratosis': {
        'description': 'Actinic keratosis is a precancerous lesion caused by sun exposure. It appears as rough, scaly patches and has potential to develop into skin cancer.',
        'tips': 'Use SPF 50+ sunscreen daily. Wear protective clothing and hats. Avoid tanning beds. Seek shade during peak sun hours.',
        'risk': 'High',
        'advice': 'Visit a dermatologist for regular monitoring and treatment options including cryotherapy, topical treatments, or laser therapy.'
    },
    'Atopic Dermatitis': {
        'description': 'Atopic dermatitis is a chronic inflammatory condition causing intense itching and skin barrier dysfunction. Often begins in childhood.',
        'tips': 'Use intensive moisturizers frequently. Take short warm showers. Avoid harsh soaps and irritants. Manage stress and allergens.',
        'risk': 'Medium',
        'advice': 'Consult a dermatologist for treatment options including topical steroids, calcineurin inhibitors, or biologics.'
    },
    'Bullous Disease': {
        'description': 'Bullous diseases are characterized by fluid-filled blisters on skin or mucous membranes. Causes vary and can include autoimmune reactions.',
        'tips': 'Keep lesions clean and dry. Avoid trauma to affected areas. Use sterile bandages. Monitor for signs of infection.',
        'risk': 'Medium',
        'advice': 'Seek dermatological evaluation urgently. Biopsy may be needed. Treatment depends on specific diagnosis.'
    },
    'Cellulitis': {
        'description': 'Cellulitis is an acute bacterial infection causing redness, warmth, and swelling of the skin. It requires prompt medical attention.',
        'tips': 'Keep wound clean and elevated. Do not squeeze or puncture lesions. Monitor temperature. Maintain hygiene.',
        'risk': 'High',
        'advice': 'Seek immediate medical attention. Antibiotics are typically required. Untreated cellulitis can become serious.'
    },
    'Eczema': {
        'description': 'Eczema is a chronic inflammatory skin condition characterized by itching, redness, and dry patches. Multiple types exist.',
        'tips': 'Apply moisturizer within 3 minutes of showering. Use fragrance-free products. Take lukewarm baths. Avoid irritants.',
        'risk': 'Low',
        'advice': 'Consult a dermatologist for personalized treatment plans including topical medications or immunosuppressants.'
    },
    'Exanthems and Drug Eruptions': {
        'description': 'Exanthems are widespread rashes often caused by viral infections or allergic reactions. Drug eruptions result from medication side effects.',
        'tips': 'Identify potential triggers and allergens. Maintain hygiene. Avoid scratching. Stay hydrated.',
        'risk': 'Medium',
        'advice': 'Seek medical evaluation to determine cause. May require medication adjustment or specific treatment for underlying condition.'
    },
    'Hair Loss Alopecia': {
        'description': 'Hair loss (alopecia) can be temporary or permanent, resulting from genetics, stress, hormonal changes, or nutritional deficiencies.',
        'tips': 'Manage stress through exercise. Ensure adequate protein and iron. Avoid harsh hair treatments. Use gentle hair care.',
        'risk': 'Medium',
        'advice': 'Consult a dermatologist for evaluation and treatment options including minoxidil, finasteride, or hair transplant.'
    },
    'Herpes HPV': {
        'description': 'Herpes and HPV are viral infections. Herpes causes painful blisters; HPV can lead to warts or serious complications.',
        'tips': 'Practice safe hygiene and sexual health practices. Avoid contact during active outbreaks. Use antivirals as prescribed.',
        'risk': 'Medium',
        'advice': 'Consult a healthcare provider for antiviral treatment and vaccination options. HPV vaccination prevents certain strains.'
    },
    'Light Diseases': {
        'description': 'Light-related skin diseases include conditions triggered or worsened by sun exposure, such as polymorphous light eruption or solar urticaria.',
        'tips': 'Use SPF 50+ broad-spectrum sunscreen. Wear protective clothing. Seek shade during peak sun hours. Avoid midday sun.',
        'risk': 'Low',
        'advice': 'Dermatologist can recommend preventive measures and desensitization therapy if appropriate.'
    },
    'Lupus': {
        'description': 'Lupus is an autoimmune disease affecting skin, joints, and internal organs. Skin manifestations include photosensitive rashes.',
        'tips': 'Avoid sun exposure. Use SPF 50+ sunscreen. Manage stress. Take prescribed medications. Regular medical check-ups.',
        'risk': 'High',
        'advice': 'Work closely with rheumatologist and dermatologist. May require immunosuppressive medications and systemic treatment.'
    },
    'Melanoma Skin Cancer': {
        'description': 'Melanoma is the most dangerous type of skin cancer. It develops from melanocytes and can spread rapidly if not treated early.',
        'tips': 'Use SPF 30+ sunscreen daily. Avoid tanning beds. Perform monthly skin self-exams. Wear protective clothing.',
        'risk': 'High',
        'advice': 'Seek urgent dermatological evaluation. Early detection is critical. Treatment may include surgery, immunotherapy, or chemotherapy.'
    },
    'Nail Fungus': {
        'description': 'Nail fungus (onychomycosis) causes nails to thicken, discolor, and become brittle. It spreads slowly and is contagious.',
        'tips': 'Keep nails trimmed and dry. Wear breathable shoes. Avoid public pools and showers. Use antifungal powder if prone to moisture.',
        'risk': 'Medium',
        'advice': 'See a dermatologist for prescription antifungal treatment. Topical treatments may not reach deep infections.'
    },
    'Poison Ivy': {
        'description': 'Poison ivy and related plants cause allergic dermatitis with blisters, itching, and redness from urushiol oil contact.',
        'tips': 'Learn to identify plants and avoid contact. Wash skin immediately after exposure. Wash contaminated clothing separately.',
        'risk': 'Low',
        'advice': 'Use hydrocortisone cream and antihistamines for symptom relief. Severe reactions may require prescription treatment.'
    },
    'Psoriasis': {
        'description': 'Psoriasis is a chronic autoimmune condition causing thick, scaly, red patches. It often appears on elbows, knees, and scalp.',
        'tips': 'Keep skin moisturized. Use sunscreen. Manage stress. Avoid trigger foods. Take warm baths with oatmeal.',
        'risk': 'Medium',
        'advice': 'Dermatologist can prescribe topical treatments, phototherapy, or systemic medications depending on severity.'
    },
    'Scabies Lyme Disease': {
        'description': 'Scabies is caused by mites causing intense itching. Lyme disease is transmitted by ticks and can cause skin rash and systemic symptoms.',
        'tips': 'Scabies: treat all household members. Lyme: perform tick checks after outdoor activities. Treat clothing/bedding.',
        'risk': 'Medium',
        'advice': 'Seek medical evaluation for appropriate treatment. Scabies requires prescription cream; Lyme may need antibiotics.'
    },
    'Seborrheic Keratoses': {
        'description': 'Seborrheic keratoses are benign skin growths appearing waxy, scaly, and slightly raised. Common with aging.',
        'tips': 'Protect skin from sun exposure. Use SPF 30+ daily. Avoid picking at lesions. Do not self-remove.',
        'risk': 'Low',
        'advice': 'No treatment needed unless cosmetically bothersome. Dermatologist can safely remove via cryotherapy or laser.'
    },
    'Systemic Disease': {
        'description': 'Systemic diseases can manifest skin symptoms. These conditions require comprehensive evaluation and specialized treatment.',
        'tips': 'Maintain overall health through diet and exercise. Follow prescribed treatment plans. Regular medical monitoring.',
        'risk': 'High',
        'advice': 'Seek comprehensive medical evaluation by multiple specialists. Skin symptoms may indicate underlying systemic condition.'
    },
    'Tinea Ringworm': {
        'description': 'Tinea is a fungal infection causing ring-shaped, itchy, red patches. It is contagious through direct contact or fomites.',
        'tips': 'Keep area clean and dry. Wear loose clothing. Avoid sharing personal items and towels. Use antifungal powder.',
        'risk': 'Low',
        'advice': 'Use topical antifungal creams or take oral antifungals for severe cases. Improves in 2-3 weeks with treatment.'
    },
    'Urticaria Hives': {
        'description': 'Urticaria (hives) are raised, itchy welts caused by allergic reactions to food, medications, insect bites, or other triggers.',
        'tips': 'Identify and avoid triggers. Use antihistamines as needed. Apply cool compresses. Avoid tight clothing.',
        'risk': 'Low',
        'advice': 'Take over-the-counter antihistamines. Seek medical evaluation if hives persist beyond 6 weeks (chronic urticaria).'
    },
    'Vascular Tumors': {
        'description': 'Vascular tumors are benign growths of blood vessels. Hemangiomas are most common and usually appear in childhood.',
        'tips': 'Monitor for changes in appearance or size. Protect from trauma. Avoid scratching or picking.',
        'risk': 'Low',
        'advice': 'Most resolve on their own. Dermatologist can monitor or treat cosmetically significant lesions with laser or other methods.'
    },
    'Vasculitis': {
        'description': 'Vasculitis is inflammation of blood vessels often presenting with palpable purpura. It can be cutaneous or systemic.',
        'tips': 'Protect skin from trauma. Maintain good hygiene. Follow prescribed treatment. Regular medical monitoring.',
        'risk': 'High',
        'advice': 'Seek urgent medical evaluation. Biopsy confirmation may be needed. Treatment depends on type and severity.'
    },
    'Warts Molluscum': {
        'description': 'Warts and molluscum are viral skin infections causing bumps. Both are contagious through direct contact.',
        'tips': 'Avoid touching or picking lesions. Wash hands frequently. Do not share personal items. Cover lesions when possible.',
        'risk': 'Low',
        'advice': 'Many resolve on their own. Dermatologist can treat with cryotherapy, topical treatments, or laser if needed.'
    }
}


def get_disease_info(disease_name):
    """Fetch disease information from dictionary with fallback message."""
    # Try exact match first
    if disease_name in disease_info:
        return disease_info[disease_name]
    
    # Try fuzzy matching for simplified names
    clean_name = disease_name.split()[0].lower() if disease_name else ''
    for key in disease_info:
        if clean_name in key.lower() or key.lower().split()[0] == clean_name:
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
        0: 'Acne and Rosacea',
        1: 'Actinic Keratosis',
        2: 'Atopic Dermatitis',
        3: 'Bullous Disease',
        4: 'Cellulitis',
        5: 'Eczema',
        6: 'Exanthems and Drug Eruptions',
        7: 'Hair Loss Alopecia',
        8: 'Herpes HPV',
        9: 'Light Diseases',
        10: 'Lupus',
        11: 'Melanoma Skin Cancer',
        12: 'Nail Fungus',
        13: 'Poison Ivy',
        14: 'Psoriasis',
        15: 'Scabies Lyme Disease',
        16: 'Seborrheic Keratoses',
        17: 'Systemic Disease',
        18: 'Tinea Ringworm',
        19: 'Urticaria Hives',
        20: 'Vascular Tumors',
        21: 'Vasculitis',
        22: 'Warts Molluscum'
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
    app.run(debug=True, port=5002)
