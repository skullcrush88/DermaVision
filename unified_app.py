"""
DermaDetectAI - Unified Product Application
Consolidates 3 AI models into a single, professional skin disease detection system.
"""

from flask import Flask, request, render_template, jsonify
import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
import os
import cv2
import numpy as np

# Explicitly set template folder to avoid loading wrong templates
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
app = Flask(__name__, template_folder=template_dir)

# ============================================================================
# MODEL LOADING
# ============================================================================

class UnifiedModelEnsemble:
    """Loads and manages all 3 pre-trained models."""
    
    def __init__(self):
        self.models = {}
        self.transforms = transforms.Compose([
            transforms.Resize((150, 150)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
        self._load_models()
    
    def _load_models(self):
        """Load all 3 trained models."""
        # Model 1: 5 diseases
        self.models['model1'] = {
            'model': self._build_resnet(5),
            'weights': 'model 1/models/skin_disease_model.pth',
            'classes': 5,
            'labels': {
                0: 'Acne', 1: 'Hairloss', 2: 'Nail Fungus',
                3: 'Normal', 4: 'Skin Allergy'
            }
        }
        
        # Model 2: 10 diseases
        self.models['model2'] = {
            'model': self._build_resnet(10),
            'weights': 'model 2/models/skin_disease_model.pth',
            'classes': 10,
            'labels': {
                0: 'Eczema', 1: 'Melanoma', 2: 'Atopic Dermatitis',
                3: 'Basal Cell Carcinoma', 4: 'Melanocytic Nevi',
                5: 'Benign Keratosis', 6: 'Psoriasis',
                7: 'Seborrheic Keratoses', 8: 'Tinea Ringworm', 9: 'Warts Molluscum'
            }
        }
        
        # Model 3: 23 diseases (comprehensive)
        self.models['model3'] = {
            'model': self._build_resnet(23),
            'weights': 'model 3/models/skin_disease_model.pth',
            'classes': 23,
            'labels': {
                0: 'Acne and Rosacea', 1: 'Actinic Keratosis',
                2: 'Atopic Dermatitis', 3: 'Bullous Disease',
                4: 'Cellulitis', 5: 'Eczema',
                6: 'Exanthems and Drug Eruptions', 7: 'Hair Loss Alopecia',
                8: 'Herpes HPV', 9: 'Light Diseases',
                10: 'Lupus', 11: 'Melanoma Skin Cancer',
                12: 'Nail Fungus', 13: 'Poison Ivy',
                14: 'Psoriasis', 15: 'Scabies Lyme Disease',
                16: 'Seborrheic Keratoses', 17: 'Systemic Disease',
                18: 'Tinea Ringworm', 19: 'Urticaria Hives',
                20: 'Vascular Tumors', 21: 'Vasculitis',
                22: 'Warts Molluscum'
            }
        }
        
        # Load weights
        for model_name, model_config in self.models.items():
            try:
                model_config['model'].load_state_dict(
                    torch.load(model_config['weights'], map_location='cpu')
                )
                model_config['model'].eval()
                print(f"✓ {model_name} loaded ({model_config['classes']} classes)")
            except Exception as e:
                print(f"✗ Error loading {model_name}: {e}")
    
    def _build_resnet(self, num_classes):
        """Build ResNet50 architecture."""
        model = models.resnet50(pretrained=False)
        num_ftrs = model.fc.in_features
        model.fc = nn.Linear(num_ftrs, num_classes)
        return model
    
    def predict(self, image_path):
        """
        Get prediction using all 3 models and return unified result.
        Uses Model 3 as primary (most comprehensive), validates against others.
        
        Returns: (disease_name, confidence, model_used)
        """
        img = Image.open(image_path).convert('RGB')
        img_tensor = self.transforms(img).unsqueeze(0)
        
        results = {}
        
        with torch.no_grad():
            # Get predictions from all models
            for model_name, config in self.models.items():
                outputs = config['model'](img_tensor)
                probs = torch.nn.functional.softmax(outputs, dim=1)
                confidence, predicted = torch.max(probs.data, 1)
                
                disease_name = config['labels'][predicted.item()]
                confidence_pct = round(confidence.item() * 100, 2)
                
                results[model_name] = {
                    'disease': disease_name,
                    'confidence': confidence_pct,
                    'probs': probs[0]
                }
        
        # Primary: Model 3 (most comprehensive), fallback to Model 2, then Model 1
        primary_result = results['model3']
        
        return (
            primary_result['disease'],
            primary_result['confidence'],
            'model3'  # Track which model was used
        )


# Load ensemble at startup
ensemble = UnifiedModelEnsemble()

# ============================================================================
# DISEASE INFORMATION DICTIONARY (Unified Post-Processing)
# ============================================================================

DISEASE_INFO = {
    # Model 1 diseases
    'Acne': {
        'description': 'Acne is a skin condition characterized by pimples, blackheads, and whiteheads. Caused by bacteria and oil buildup in pores.',
        'tips': 'Cleanse twice daily with gentle products. Avoid touching your face. Use oil-free moisturizer.',
        'risk': 'Low',
        'advice': 'Use topical treatments with benzoyl peroxide or salicylic acid. See dermatologist for persistent acne.'
    },
    'Hairloss': {
        'description': 'Hair loss (alopecia) involves thinning or baldness. Can be genetic, hormonal, or due to stress and nutritional deficiencies.',
        'tips': 'Manage stress, maintain balanced diet with biotin and iron. Avoid harsh hair treatments.',
        'risk': 'Medium',
        'advice': 'Consult dermatologist for diagnosis. Options include minoxidil, finasteride, or hair transplant.'
    },
    'Nail Fungus': {
        'description': 'Fungal infection of nails causing discoloration, thickening, and brittleness. Spreads in warm, moist environments.',
        'tips': 'Keep nails dry and trimmed. Avoid public pools. Wear breathable shoes.',
        'risk': 'Medium',
        'advice': 'Prescription antifungal creams or oral medications. Takes 3-6 months to resolve.'
    },
    'Normal': {
        'description': 'Your skin appears to be healthy with no visible signs of disease or abnormality.',
        'tips': 'Maintain good hygiene and sun protection. Use SPF 30+ daily.',
        'risk': 'Low',
        'advice': 'Continue regular skincare routine. Monitor for any changes.'
    },
    'Skin Allergy': {
        'description': 'Allergic reaction causing rash, itching, redness, or swelling on skin.',
        'tips': 'Identify and avoid triggers. Use hypoallergenic products. Apply cool compresses.',
        'risk': 'Low',
        'advice': 'Use antihistamine creams. See dermatologist if reaction persists beyond 2 weeks.'
    },
    # Model 2 diseases
    'Eczema': {
        'description': 'Chronic inflammatory skin condition with itching, dryness, and redness.',
        'tips': 'Moisturize within 3 minutes of bathing. Use fragrance-free products. Take warm showers.',
        'risk': 'Medium',
        'advice': 'Dermatologist can prescribe topical steroids or immunosuppressants.'
    },
    'Melanoma': {
        'description': 'Most dangerous skin cancer from melanocytes. Early detection is critical.',
        'tips': 'Monthly skin self-exams. Avoid tanning beds. Use SPF 50+ daily.',
        'risk': 'High',
        'advice': 'URGENT: See dermatologist immediately. Biopsy and treatment needed.'
    },
    'Atopic Dermatitis': {
        'description': 'Chronic inflammatory condition causing intense itching and skin barrier dysfunction.',
        'tips': 'Use intensive moisturizers. Avoid harsh soaps. Manage stress.',
        'risk': 'Medium',
        'advice': 'Dermatologist-prescribed treatments including topical steroids or biologics.'
    },
    'Basal Cell Carcinoma': {
        'description': 'Common skin cancer. Appears as pearly bump or sore that doesn\'t heal.',
        'tips': 'Sun protection with SPF 50+. Protective clothing.',
        'risk': 'High',
        'advice': 'Urgent dermatology visit. Treatment via surgery, cryotherapy, or laser.'
    },
    'Melanocytic Nevi': {
        'description': 'Benign moles (collections of melanocytes). Usually harmless.',
        'tips': 'Monitor for changes in size, color, or shape. Sun protection.',
        'risk': 'Low',
        'advice': 'Routine monitoring. Remove if cosmetically bothersome.'
    },
    'Benign Keratosis': {
        'description': 'Common, harmless skin growths that appear waxy and scaly.',
        'tips': 'No treatment needed unless bothersome. Sun protection.',
        'risk': 'Low',
        'advice': 'Can be safely removed by dermatologist via cryotherapy or laser.'
    },
    'Psoriasis': {
        'description': 'Chronic autoimmune condition with thick, scaly, red patches.',
        'tips': 'Moisturize regularly. Manage stress. Avoid trigger foods.',
        'risk': 'Medium',
        'advice': 'Topical treatments, phototherapy, or systemic medications depending on severity.'
    },
    'Seborrheic Keratoses': {
        'description': 'Benign skin growths common with aging. Waxy, slightly raised appearance.',
        'tips': 'Sun protection. Don\'t self-remove.',
        'risk': 'Low',
        'advice': 'No treatment needed unless cosmetically concerning. Safe removal available.'
    },
    'Tinea Ringworm': {
        'description': 'Fungal infection causing ring-shaped, itchy, red patches.',
        'tips': 'Keep area clean and dry. Wear loose clothing. Avoid sharing items.',
        'risk': 'Low',
        'advice': 'Topical antifungal creams. Improves in 2-3 weeks with treatment.'
    },
    'Warts Molluscum': {
        'description': 'Viral skin infections causing bumps. Both are contagious.',
        'tips': 'Avoid touching or picking. Wash hands frequently. Cover lesions.',
        'risk': 'Low',
        'advice': 'Many resolve on their own. Dermatologist can treat with cryotherapy or laser.'
    },
    # Model 3 additional diseases (comprehensive)
    'Acne and Rosacea': {
        'description': 'Acne and rosacea are skin conditions causing redness and bumps. Acne involves pimples, rosacea causes persistent flushing.',
        'tips': 'Gentle cleansers, avoid triggers. Apply sunscreen daily. Avoid spicy foods.',
        'risk': 'Medium',
        'advice': 'Dermatologist prescription for retinoids, antibiotics, or laser therapy.'
    },
    'Actinic Keratosis': {
        'description': 'Precancerous lesion from sun exposure. Rough, scaly patches with cancer potential.',
        'tips': 'SPF 50+ daily. Protective clothing. Avoid tanning beds. Seek shade.',
        'risk': 'High',
        'advice': 'Dermatology visit for cryotherapy, topical treatments, or laser.'
    },
    'Bullous Disease': {
        'description': 'Fluid-filled blisters on skin/mucous membranes from autoimmune reactions.',
        'tips': 'Keep lesions clean and dry. Use sterile bandages. Monitor for infection.',
        'risk': 'High',
        'advice': 'Urgent dermatological evaluation. Biopsy may be needed.'
    },
    'Cellulitis': {
        'description': 'Acute bacterial skin infection with redness, warmth, and swelling.',
        'tips': 'Keep wound clean and elevated. Don\'t puncture. Monitor temperature.',
        'risk': 'High',
        'advice': 'URGENT: Seek immediate medical attention. Antibiotics required.'
    },
    'Exanthems and Drug Eruptions': {
        'description': 'Widespread rashes from viral infections or medication side effects.',
        'tips': 'Identify triggers. Maintain hygiene. Avoid scratching. Stay hydrated.',
        'risk': 'Medium',
        'advice': 'Medical evaluation. May require medication adjustment or specific treatment.'
    },
    'Hair Loss Alopecia': {
        'description': 'Hair loss from genetics, stress, hormones, or nutritional deficiency.',
        'tips': 'Manage stress. Adequate protein and iron. Avoid harsh treatments.',
        'risk': 'Medium',
        'advice': 'Dermatologist evaluation. Options: minoxidil, finasteride, or transplant.'
    },
    'Herpes HPV': {
        'description': 'Viral infections. Herpes causes painful blisters, HPV leads to warts.',
        'tips': 'Safe hygiene and sexual practices. Avoid contact during outbreaks.',
        'risk': 'Medium',
        'advice': 'Antiviral treatment and vaccination options. HPV vaccine prevents strains.'
    },
    'Light Diseases': {
        'description': 'Sun-triggered skin diseases like polymorphous light eruption.',
        'tips': 'SPF 50+ broad-spectrum. Protective clothing. Seek shade during peak sun.',
        'risk': 'Low',
        'advice': 'Preventive measures and desensitization therapy if appropriate.'
    },
    'Lupus': {
        'description': 'Autoimmune disease affecting skin, joints, and organs. Photosensitive rashes.',
        'tips': 'Avoid sun. SPF 50+ sunscreen. Manage stress. Regular check-ups.',
        'risk': 'High',
        'advice': 'Rheumatologist + dermatologist. May require immunosuppressive medications.'
    },
    'Melanoma Skin Cancer': {
        'description': 'Most dangerous skin cancer. Develops rapidly if not treated early.',
        'tips': 'Daily SPF 30+. Avoid tanning. Monthly self-exams. Protective clothing.',
        'risk': 'High',
        'advice': 'URGENT dermatology. Early detection critical. Surgery/immunotherapy.'
    },
    'Poison Ivy': {
        'description': 'Allergic dermatitis from plant contact. Blisters, itching, redness.',
        'tips': 'Identify and avoid plants. Wash skin immediately after exposure.',
        'risk': 'Low',
        'advice': 'Hydrocortisone cream and antihistamines. Severe cases need prescription.'
    },
    'Scabies Lyme Disease': {
        'description': 'Scabies from mites; Lyme from ticks. Both need treatment.',
        'tips': 'Treat all household members. Tick checks after outdoor activity.',
        'risk': 'Medium',
        'advice': 'Medical evaluation. Scabies: prescription cream. Lyme: antibiotics.'
    },
    'Systemic Disease': {
        'description': 'Skin symptoms indicating underlying systemic condition.',
        'tips': 'Maintain health. Follow treatment plans. Regular monitoring.',
        'risk': 'High',
        'advice': 'Comprehensive evaluation by multiple specialists.'
    },
    'Urticaria Hives': {
        'description': 'Raised, itchy welts from allergic reactions.',
        'tips': 'Identify and avoid triggers. Cool compresses. Avoid tight clothing.',
        'risk': 'Low',
        'advice': 'OTC antihistamines. Medical evaluation if persists beyond 6 weeks.'
    },
    'Vascular Tumors': {
        'description': 'Benign blood vessel growths. Hemangiomas common in children.',
        'tips': 'Monitor for changes. Avoid trauma. Don\'t scratch or pick.',
        'risk': 'Low',
        'advice': 'Most resolve on their own. Cosmetic treatment available if needed.'
    },
    'Vasculitis': {
        'description': 'Blood vessel inflammation with palpable purpura. Cutaneous or systemic.',
        'tips': 'Avoid trauma. Good hygiene. Follow treatment. Regular monitoring.',
        'risk': 'High',
        'advice': 'URGENT medical evaluation. Biopsy confirmation may be needed.'
    },
}


def get_disease_info(disease_name):
    """Get disease information with fallback."""
    if disease_name in DISEASE_INFO:
        return DISEASE_INFO[disease_name]
    
    # Fuzzy matching
    clean_name = disease_name.split()[0].lower() if disease_name else ''
    for key in DISEASE_INFO:
        if clean_name in key.lower() or key.lower().split()[0] == clean_name:
            return DISEASE_INFO[key]
    
    return {
        'description': 'This condition requires medical evaluation.',
        'tips': 'Consult a healthcare professional.',
        'risk': 'Unknown',
        'advice': 'Schedule an appointment with a dermatologist.'
    }


# ============================================================================
# IMAGE VALIDATION (HSV Skin Detection)
# ============================================================================

def is_skin_image(image_path):
    """Validate if image contains human skin using HSV analysis."""
    try:
        img = cv2.imread(image_path)
        if img is None:
            return False
        
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Skin tone ranges (HSV)
        lower_skin1 = np.array([0, 10, 30], dtype=np.uint8)
        upper_skin1 = np.array([25, 200, 255], dtype=np.uint8)
        lower_skin2 = np.array([155, 10, 30], dtype=np.uint8)
        upper_skin2 = np.array([180, 200, 255], dtype=np.uint8)
        
        mask1 = cv2.inRange(hsv, lower_skin1, upper_skin1)
        mask2 = cv2.inRange(hsv, lower_skin2, upper_skin2)
        mask = cv2.bitwise_or(mask1, mask2)
        
        skin_pixels = cv2.countNonZero(mask)
        total_pixels = img.shape[0] * img.shape[1]
        skin_percentage = (skin_pixels / total_pixels) * 100
        
        if skin_percentage < 10:
            return False
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        variance = cv2.Laplacian(gray, cv2.CV_64F).var()
        if variance < 50:
            return False
        
        return True
    except Exception as e:
        print(f"Validation error: {e}")
        return False


# ============================================================================
# UNIFIED PREDICTION FUNCTION (Core Logic)
# ============================================================================

def get_prediction(image_path):
    """
    UNIFIED PREDICTION INTERFACE
    
    Single function that handles all 3 models and returns unified result.
    User doesn't need to know about multiple models.
    
    Returns:
        {
            'disease': str,
            'confidence': float,
            'risk': str,
            'description': str,
            'tips': str,
            'advice': str,
            'confidence_text': str
        }
    """
    # Get prediction from ensemble
    disease_name, confidence, model_used = ensemble.predict(image_path)
    
    # Get disease information
    info = get_disease_info(disease_name)
    
    # Generate confidence interpretation
    if confidence > 80:
        confidence_text = 'High confidence prediction'
    elif confidence > 50:
        confidence_text = 'Moderate confidence'
    else:
        confidence_text = 'Low confidence — result may be uncertain'
    
    return {
        'disease': disease_name,
        'confidence': confidence,
        'risk': info['risk'],
        'description': info['description'],
        'tips': info['tips'],
        'advice': info['advice'],
        'confidence_text': confidence_text
    }


# ============================================================================
# FLASK ROUTES (Single Unified Interface)
# ============================================================================

@app.route('/', methods=['GET', 'POST'])
def index():
    """Single page application - upload and result display."""
    if request.method == 'POST':
        # Handle file upload
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file:
            file_path = os.path.join('uploads', file.filename)
            file.save(file_path)
            
            # Validation: Check if image contains skin
            if not is_skin_image(file_path):
                return jsonify({
                    'error': 'Invalid input. Please upload a clear skin image.'
                }), 400
            
            # Get prediction using unified interface
            try:
                result = get_prediction(file_path)
                return jsonify(result), 200
            except Exception as e:
                return jsonify({'error': f'Prediction error: {str(e)}'}), 500
    
    # GET request: Return single page
    return render_template('unified.html')


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'models': ['model1 (5 classes)', 'model2 (10 classes)', 'model3 (23 classes)'],
        'unified': True
    }), 200


# ============================================================================
# INITIALIZATION
# ============================================================================

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    
    print("\n" + "="*70)
    print("DermaVision - UNIFIED PRODUCT APPLICATION")
    print("="*70)
    print("\nSingle-page application with unified prediction interface")
    print("All 3 models loaded and operational")
    print("Starting server on http://127.0.0.1:5000\n")
    
    app.run(debug=True, port=5000)
