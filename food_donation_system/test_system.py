import os
import sys
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))

from database.db_manager import init_db, get_all_ngos
from models.classifier import FoodClassifier
from models.quantity_estimator import FoodQuantityEstimator
from models.safety_evaluator import FoodSafetyEvaluator
from matching.smart_matcher import SmartMatcher

def test_pipeline():
    print("--- 1. Testing Database Initialization ---", flush=True)
    init_db()
    ngos = get_all_ngos()
    print(f"✅ Initialized DB with {len(ngos)} seeded NGOs.", flush=True)

    print("\n--- 2. Testing Stage 1: Food Classifier ---", flush=True)
    classifier = FoodClassifier()
    dummy_img = Image.new('RGB', (224, 224), color=(200, 100, 50))
    cls_result = classifier.predict(dummy_img)
    print(f"✅ Classification Result: {cls_result['category']} (Confidence: {cls_result['confidence']})", flush=True)

    print("\n--- 3. Testing Stage 2: Quantity Estimator (ML) ---", flush=True)
    qty_estimator = FoodQuantityEstimator()
    qty_result = qty_estimator.estimate(
        container_type="Medium Catering Vessel (~8-10 kg)",
        container_count=2,
        food_type=cls_result['category']
    )
    print(f"✅ Quantity Estimation: {qty_result['estimated_weight_kg']} kg -> {qty_result['estimated_servings']} People Served", flush=True)

    print("\n--- 4. Testing Stage 3: Food Safety Evaluator (Rule-based + ML) ---", flush=True)
    safety_evaluator = FoodSafetyEvaluator()
    safety_result = safety_evaluator.evaluate(
        food_type=cls_result['category'],
        hours_since_prepared=2.5,
        storage_condition="Covered & Room Temp (20-25°C)",
        visual_confidence=cls_result['confidence']
    )
    print(f"✅ Clean Food Safety Tag: {safety_result['safety_tag']} (Score: {safety_result['safety_score']})", flush=True)

    # Test visual mold detection on moldy bread image
    bread_crop_path = os.path.join(os.path.dirname(__file__), "..", "bread_crop.png")
    if os.path.exists(bread_crop_path):
        moldy_img = Image.open(bread_crop_path)
        mold_result = safety_evaluator.evaluate(
            food_type="Roti, Naan & Bread",
            hours_since_prepared=1.0,
            storage_condition="Refrigerated / Chilled (< 5°C)",
            visual_confidence=0.9,
            image=moldy_img
        )
        assert mold_result['is_safe_for_donation'] == False, "Failed to reject moldy bread!"
        print(f"✅ Moldy Food Visual Detection: {mold_result['description']}", flush=True)

    # Test fresh meal image (fresh naan, curry, rice with blue tablecloth)
    fresh_meal_path = os.path.join(os.path.dirname(__file__), "..", "fresh_meal_crop.png")
    if os.path.exists(fresh_meal_path):
        fresh_meal_img = Image.open(fresh_meal_path)
        fresh_meal_res = safety_evaluator.evaluate(
            food_type="Rich Curry & Stew",
            hours_since_prepared=1.5,
            storage_condition="Covered & Room Temp (20-25°C)",
            visual_confidence=0.95,
            image=fresh_meal_img
        )
        assert fresh_meal_res['is_safe_for_donation'] == True, "Incorrectly rejected fresh restaurant meal!"
        print(f"✅ Fresh Restaurant Meal Visual Verification: {fresh_meal_res['description']} (Tag: {fresh_meal_res['safety_tag']})", flush=True)

    print("\n--- 5. Testing Stage 4: Smart Matching Engine ---", flush=True)
    matcher = SmartMatcher(ngos)
    matches = matcher.match(
        donor_lat=12.9716,
        donor_lon=77.5946,
        estimated_servings=qty_result['estimated_servings'],
        safety_tag=safety_result['safety_tag']
    )
    print(f"✅ Top Matched NGO: {matches[0]['name']} ({matches[0]['match_score']}% Match, {matches[0]['distance_km']} km away)", flush=True)

    print("\n--- 6. Testing Stage 5: NGO & Volunteer Need Requests ---", flush=True)
    from database.db_manager import add_food_request, get_all_food_requests
    req_id = add_food_request("Volunteer", "Test Volunteer", "+91 99999 11111", 11.10, 77.34, "Test Railway Gate", "Cooked Rice & Grain Dishes", 40, "Urgent", "Testing request flow")
    all_reqs = get_all_food_requests()
    assert any(r['id'] == req_id for r in all_reqs), "Failed to save food request!"
    print(f"✅ Successfully created and fetched Volunteer Food Need Request #{req_id}.", flush=True)

    print("\n🎉 ALL PIPELINE TESTS PASSED SUCCESSFULLY!", flush=True)

if __name__ == "__main__":
    test_pipeline()
