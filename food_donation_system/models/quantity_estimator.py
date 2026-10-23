import numpy as np

try:
    from sklearn.ensemble import RandomForestRegressor
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

class FoodQuantityEstimator:
    def __init__(self):
        self.container_capacities = {
            "Single Portion / Small Item (~0.2-0.5 kg)": 0.35,
            "Small Packaging Tray (~2-3 kg)": 2.5,
            "Medium Catering Vessel (~8-10 kg)": 9.0,
            "Large Commercial Pot (~20-25 kg)": 22.5,
            "Industrial Bulk Container (~50+ kg)": 50.0,
            "Custom Weight (Manual Input)": 1.0
        }

        self.portion_standards = {
            "Cooked Rice & Grain Dishes": 0.35,  # 350 grams
            "Rich Curry & Stew": 0.30,           # 300 grams
            "Roti, Naan & Bread": 0.25,          # 250 grams
            "Fresh Salad & Vegetables": 0.20,    # 200 grams
            "Dessert & Sweets": 0.15,            # 150 grams
            "Assorted Mixed Meal / Buffet": 0.40  # 400 grams
        }

        self.calories_per_kg = {
            "Cooked Rice & Grain Dishes": 1300,
            "Rich Curry & Stew": 1100,
            "Roti, Naan & Bread": 2600,
            "Fresh Salad & Vegetables": 450,
            "Dessert & Sweets": 2800,
            "Assorted Mixed Meal / Buffet": 1400
        }

        self.ml_model = None

    def _lazy_train(self):
        if self.ml_model is None and SKLEARN_AVAILABLE:
            X_train = []
            y_train = []
            for weight in np.linspace(0.2, 150.0, 60):
                for density_factor in [0.85, 1.0, 1.15]:
                    X_train.append([weight, density_factor])
                    y_train.append(weight / (0.32 * density_factor))

            self.ml_model = RandomForestRegressor(n_estimators=10, random_state=42)
            self.ml_model.fit(X_train, y_train)

    def estimate(self, container_type, container_count, food_type, user_weight_kg=None):
        if user_weight_kg and user_weight_kg > 0:
            total_weight_kg = float(user_weight_kg)
        else:
            unit_weight = self.container_capacities.get(container_type, 2.5)
            total_weight_kg = round(unit_weight * container_count, 2)

        portion_per_person = self.portion_standards.get(food_type, 0.35)
        cal_per_kg = self.calories_per_kg.get(food_type, 1200)

        self._lazy_train()

        if SKLEARN_AVAILABLE and self.ml_model is not None:
            density_factor = portion_per_person / 0.35
            ml_servings_pred = self.ml_model.predict([[total_weight_kg, density_factor]])[0]
            servings = int(max(1, round(ml_servings_pred)))
        else:
            servings = int(max(1, round(total_weight_kg / portion_per_person)))

        total_calories = int(round(total_weight_kg * cal_per_kg))

        return {
            "estimated_weight_kg": round(total_weight_kg, 2),
            "estimated_servings": servings,
            "portion_grams": int(portion_per_person * 1000),
            "total_calories_kcal": total_calories,
            "summary_text": f"Feeds approximately {servings} people ({total_weight_kg} kg total)"
        }
