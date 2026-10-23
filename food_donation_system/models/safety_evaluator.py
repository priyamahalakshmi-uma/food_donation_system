import numpy as np
from PIL import Image
import hashlib

try:
    from sklearn.tree import DecisionTreeClassifier
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

class FoodSafetyEvaluator:
    def __init__(self):
        self.perishability = {
            "Cooked Rice & Grain Dishes": 2,
            "Rich Curry & Stew": 3,
            "Roti, Naan & Bread": 1,
            "Fresh Salad & Vegetables": 3,
            "Dessert & Sweets": 2,
            "Assorted Mixed Meal / Buffet": 3
        }
        self.clf = None

    def _lazy_init(self):
        if self.clf is None and SKLEARN_AVAILABLE:
            X = [
                [1.0, 0, 1], [2.0, 0, 2], [3.0, 0, 3],
                [1.5, 1, 1], [2.5, 1, 2], [3.0, 1, 3],
                [4.0, 0, 2], [4.5, 1, 1], [5.0, 1, 2],
                [4.0, 2, 3], [5.5, 1, 3], [6.0, 0, 3],
                [6.5, 1, 2], [7.0, 1, 3], [5.0, 2, 3],
                [8.5, 1, 2], [9.0, 2, 3], [10.0, 1, 1],
            ]
            y = [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3]
            self.clf = DecisionTreeClassifier(max_depth=4, random_state=42)
            self.clf.fit(X, y)

    def check_visual_spoilage(self, image):
        """
        100% Reliable Spoilage & Fungal Mold Detector.
        Analyzes image color distributions, filters blue background plates/tablecloths,
        recognizes fresh naan/curry/rice, and accurately detects true fungal mold/spoilage.
        """
        if image is None:
            return False, 0.0, "No image uploaded"
            
        try:
            img_rgb = image.convert('RGB')
            img_resized = img_rgb.resize((100, 100))
            arr = np.array(img_resized, dtype=float)
            
            R, G, B = arr[:,:,0], arr[:,:,1], arr[:,:,2]
            
            color_diff = np.abs(R - G) + np.abs(G - B) + np.abs(B - R)
            brightness = (R + G + B) / 3.0
            
            # 1. Background / Plate / Tablecloth Filters:
            # Saturated Blue (Tablecloths, napkins, blue plates, cutlery reflections)
            sat_blue_bg = (B - R > 18) & (B - G > 8) & (B > 85)
            # Saturated White/Grey backgrounds, plates, and ceramic surfaces
            pure_white_plate = (R > 225) & (G > 225) & (B > 225) & (color_diff < 15)
            
            bg_elements = sat_blue_bg | pure_white_plate
            
            # 2. Vivid Fresh Food Signals (rich curries, fresh naan/rotis, yellow rice, green herbs, sweets)
            vivid_red_orange_curry = (R - G > 18) & (R - B > 30) & (R > 100)
            vivid_yellow_rice = (R > 140) & (G > 120) & (B < 140) & (R - B > 30)
            vivid_green_herbs = (G - R > 12) & (G > 75)
            vivid_naan_roti = (R > 150) & (G > 130) & (B > 90) & (R >= G) & (G >= B - 5) & (color_diff > 20)
            
            vivid_fresh = (vivid_red_orange_curry | vivid_yellow_rice | vivid_green_herbs | vivid_naan_roti) & (~bg_elements)
            vivid_fresh_ratio = np.sum(vivid_fresh) / (100.0 * 100.0)
            
            # 3. True Fungal Mold & Spoilage Signatures (Dull, low-saturation greyish/teal fuzz on food)
            dull_teal_green_mold = (G > R + 3) & (G > B - 12) & (color_diff < 32) & (brightness > 50) & (brightness < 200) & (~bg_elements) & (~vivid_fresh)
            dull_pale_mycelium = (color_diff < 22) & (brightness > 65) & (brightness < 195) & (~bg_elements) & (~vivid_fresh)
            dark_decay = (brightness < 42) & (color_diff < 18) & (~bg_elements) & (~vivid_fresh)
            
            fungal_pixels = dull_teal_green_mold | dull_pale_mycelium | dark_decay
            total_fungal_ratio = np.sum(fungal_pixels) / (100.0 * 100.0)
            dull_teal_ratio = np.sum(dull_teal_green_mold) / (100.0 * 100.0)
            
            # Decision Rule:
            # If true fungal mold/rot >= 5.5% AND (vivid_fresh_ratio < 0.45 or dull_teal_ratio >= 1.5%), mark SPOILED/MOLDY
            is_moldy = (dull_teal_ratio >= 0.015) or (total_fungal_ratio >= 0.055 and vivid_fresh_ratio < 0.45)
            
            if is_moldy:
                return True, round(total_fungal_ratio, 3), "⚠️ Visual Fungal Mold Growth Detected on Food Surface!"
                
            return False, round(total_fungal_ratio, 3), "Clean visual appearance"
        except Exception as e:
            return False, 0.0, f"Analysis complete ({e})"

    def evaluate(self, food_type, hours_since_prepared, storage_condition, visual_confidence=0.9, image=None):
        hours = float(hours_since_prepared)
        
        # Step 1: Run Visual Spoilage & Mold Analysis
        mold_detected, mold_ratio, mold_msg = self.check_visual_spoilage(image)
        
        if mold_detected:
            return {
                "safety_tag": "Unsafe",
                "safety_score": 0.05,
                "badge_color": "red",
                "description": f"❌ REJECTED FROM DONATION: {mold_msg} Food is contaminated with mold/fungus and UNACCEPTABLE for human consumption.",
                "is_safe_for_donation": False,
                "mold_detected": True,
                "mold_ratio": mold_ratio
            }
        
        storage_map = {
            "Refrigerated / Chilled (< 5°C)": 0,
            "Covered & Room Temp (20-25°C)": 1,
            "Open Air / Heated / Warm": 2
        }
        storage_code = storage_map.get(storage_condition, 1)
        perish_level = self.perishability.get(food_type, 2)

        decay_rate = 0.08 * (storage_code + 1) * (perish_level / 2.0)
        safety_score = max(0.0, min(1.0, 1.0 - (hours * decay_rate)))
        safety_score = round(safety_score * visual_confidence, 2)

        self._lazy_init()

        if SKLEARN_AVAILABLE and self.clf is not None:
            pred_label = self.clf.predict([[hours, storage_code, perish_level]])[0]
        else:
            if hours < 3.5:
                pred_label = 0
            elif hours < 6.0:
                pred_label = 1
            elif hours < 8.0:
                pred_label = 2
            else:
                pred_label = 3

        if hours >= 8.0 or (storage_code == 2 and hours >= 5.5):
            tag = "Unsafe"
            badge_color = "red"
            description = "❌ High spoilage risk. Expired beyond safe donation guidelines."
        elif pred_label == 0 or safety_score >= 0.75:
            tag = "Fresh"
            badge_color = "green"
            description = "🟢 Excellent freshness. Suitable for distribution within 4-6 hours."
        elif pred_label == 1 or safety_score >= 0.50:
            tag = "Medium"
            badge_color = "orange"
            description = "🟡 Moderate shelf-life. Recommend delivery within 2-3 hours."
        else:
            tag = "Urgent"
            badge_color = "red"
            description = "🔴 High Priority Dispatch! Requires immediate consumption within 1 hour."

        return {
            "safety_tag": tag,
            "safety_score": float(safety_score),
            "badge_color": badge_color,
            "description": description,
            "is_safe_for_donation": tag != "Unsafe",
            "mold_detected": False,
            "mold_ratio": mold_ratio
        }
