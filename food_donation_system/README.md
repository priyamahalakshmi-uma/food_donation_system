# 🍲 AI Food Rescue & Tiruppur City Live Tracking System

An end-to-end AI-powered web platform built to minimize food waste, ensure food safety through visual quality evaluation, smartly match food donations with local NGOs in Tiruppur District, simulate live GPS delivery tracking, and display executive impact analytics.

---

## 🚀 Key Features

1. **🤖 AI Food Safety & Mold/Fungus Evaluation**
   - Image analysis for visual spoilage, mold, and bacterial risk evaluation.
   - Evaluates storage condition, hours elapsed, and food type to determine safety.

2. **⚖️ Portion & Quantity Estimator**
   - Estimates portion size and serving counts (including single-portion handling).

3. **🏢 Smart NGO Matcher**
   - Matches donors with optimal recipient NGOs in Tiruppur based on capacity, distance, and food type requirements.

4. **📋 Interactive NGO Intake Portal**
   - Sleek dashboard for NGOs to review, accept, or decline incoming food donations.

5. **🚚 Live GPS Delivery Tracking Simulator**
   - Real-time simulated delivery route from **Palladam to Kovilvazhi (Tiruppur District)**.
   - Dynamic map updates, realistic transit speeds, arrival notifications, and interactive 3D metallic balloon celebrations.

6. **📊 Executive Analytics & Impact Dashboard**
   - Glowing KPI cards, interactive Plotly visualizations tracking food saved, CO₂ reduction, meals distributed, and active delivery stats.

---

## 🛠️ Project Structure

```text
food_donation_system/
├── app.py                      # Main Streamlit Dashboard application
├── requirements.txt            # Python dependencies
├── database/
│   └── db_manager.py           # SQLite Database Manager with Tiruppur NGO registry
├── models/
│   ├── classifier.py           # Food classification model
│   ├── quantity_estimator.py   # Portion & quantity estimation engine
│   └── safety_evaluator.py     # AI Safety & Fungus detector
└── matching/
    └── smart_matcher.py        # Multi-criteria NGO matching engine
```

---

## ⚙️ Installation & Setup Guide

### 1. Prerequisites
- Python 3.9 or higher installed on your system.

### 2. Install Dependencies
Open your command prompt or terminal in the project directory and run:
```bash
pip install -r requirements.txt
```

### 3. Run the Application
Launch the Streamlit web dashboard:
```bash
streamlit run app.py
```
The application will automatically open in your default browser at `http://localhost:8501`.

---

## 📤 Sharing & Deployment Options

- **ZIP Archive**: Compress the entire `food_donation_system` directory and share it via Email or Google Drive. Recipient can unzip and run `streamlit run app.py`.
- **GitHub**: Push code to a public/private GitHub repository for version control and presentation.
- **Streamlit Community Cloud**: Connect your GitHub repository to [share.streamlit.io](https://share.streamlit.io) for free live web deployment!

---

## 📄 License & Credits
Built for AI Food Rescue & Sustainable Logistics in Tiruppur District.
