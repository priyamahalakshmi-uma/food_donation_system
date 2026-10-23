import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.express as px
from PIL import Image, ImageDraw
import os
import base64
import importlib

# Local project imports
import database.db_manager
import models.classifier
import models.quantity_estimator
import models.safety_evaluator

# Force instant reload of database & models modules
importlib.reload(database.db_manager)
importlib.reload(models.safety_evaluator)
importlib.reload(models.quantity_estimator)
importlib.reload(models.classifier)

from database.db_manager import (
    init_db, get_all_ngos, add_donation, assign_ngo_to_donation,
    update_donation_status, get_all_donations, get_donation_by_id,
    add_food_request, get_all_food_requests, update_request_status
)

from models.classifier import FoodClassifier
from models.quantity_estimator import FoodQuantityEstimator
from models.safety_evaluator import FoodSafetyEvaluator
from matching.smart_matcher import SmartMatcher

# Asset Paths
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
CHEF_IMG_PATH = os.path.join(ASSETS_DIR, "chef_volunteer.jpg")
HERO_IMG_PATH = os.path.join(ASSETS_DIR, "delivery_hero.jpg")

# Page Configuration
st.set_page_config(
    page_title="AI Food Rescue & Tiruppur City Live Tracking System",
    page_icon="🍲",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Premium Modern CSS Design System
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .main-header {
        font-size: 2.3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 50%, #10B981 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
        letter-spacing: -0.5px;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4B5563;
        font-weight: 600;
        margin-bottom: 1.2rem;
    }
    
    /* Workflow Banner */
    .workflow-container {
        background: linear-gradient(135deg, #EFF6FF 0%, #F0FDF4 100%);
        border: 1.5px solid #BFDBFE;
        border-radius: 14px;
        padding: 14px 20px;
        margin-bottom: 22px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 10px;
    }
    .workflow-step {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.88rem;
        font-weight: 700;
        color: #1E40AF;
        background: white;
        padding: 6px 14px;
        border-radius: 20px;
        border: 1px solid #DBEAFE;
        box-shadow: 0 2px 5px rgba(0,0,0,0.04);
    }
    
    /* Info Panel Card */
    .panel-card {
        background: #FFFFFF;
        border-radius: 16px;
        padding: 22px;
        border: 1.5px solid #E5E7EB;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
        margin-bottom: 18px;
    }
    .panel-header {
        font-size: 1.15rem;
        font-weight: 700;
        color: #1F2937;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* KPI Card */
    .kpi-card {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border: 2px solid #3B82F6;
        border-radius: 16px;
        padding: 20px;
        color: white;
        box-shadow: 0 10px 22px rgba(0,0,0,0.12);
        text-align: center;
        transition: transform 0.2s ease;
    }
    .kpi-val {
        font-size: 2.2rem;
        font-weight: 800;
        color: #34D399;
        margin-top: 4px;
    }
    .kpi-lbl {
        font-size: 0.85rem;
        color: #94A3B8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Recommendation Card */
    .rec-card {
        background: white;
        border-radius: 16px;
        padding: 20px;
        border: 2px solid #E5E7EB;
        box-shadow: 0 6px 16px rgba(0,0,0,0.04);
        margin-bottom: 16px;
        position: relative;
    }
    .rec-card-top {
        border-color: #10B981 !important;
        background: linear-gradient(180deg, #F0FDF4 0%, #FFFFFF 100%);
    }
    
    /* Badges */
    .badge-fresh {
        background-color: #D1FAE5;
        color: #065F46;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
    }
    .badge-medium {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
    }
    .badge-urgent {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
    }
    .badge-unsafe {
        background-color: #7F1D1D;
        color: #FEE2E2;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #10B981 0%, #059669 100%) !important;
        color: white !important;
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        padding: 10px 22px !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3) !important;
        border: none !important;
        width: 100% !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4) !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Database & ML Components
@st.cache_resource
def load_components():
    init_db()
    classifier = FoodClassifier()
    quantity_estimator = FoodQuantityEstimator()
    return classifier, quantity_estimator

classifier, quantity_estimator = load_components()

# Helper function to generate synthetic demo food images
def generate_sample_image(food_type):
    img = Image.new('RGB', (400, 300), color=(240, 235, 225))
    draw = ImageDraw.Draw(img)
    colors = {
        "Cooked Rice & Grain Dishes": (230, 220, 180),
        "Rich Curry & Stew": (180, 70, 30),
        "Roti, Naan & Bread": (210, 170, 110),
        "Fresh Salad & Vegetables": (60, 140, 60),
        "Dessert & Sweets": (200, 130, 160),
        "Assorted Mixed Meal / Buffet": (160, 120, 80)
    }
    fill_color = colors.get(food_type, (150, 150, 150))
    draw.ellipse([50, 30, 350, 270], fill=(255, 255, 255), outline=(200, 200, 200), width=4)
    draw.ellipse([80, 60, 320, 240], fill=fill_color)
    draw.text((120, 140), food_type, fill=(255, 255, 255))
    return img

# Header Section
st.markdown('<div class="main-header">🍲 AI Food Rescue & Tiruppur City Live Tracking System</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Bi-directional Food Rescue Platform • Donor Surplus & NGO/Volunteer Need Requests • Live GPS Navigation</div>', unsafe_allow_html=True)

# System Workflow Overview Banner
st.markdown("""
<div class="workflow-container">
    <div style="font-weight:800; color:#1E3A8A; font-size:0.95rem;">⚡ TWO-WAY MARKETPLACE:</div>
    <div class="workflow-step">🍱 Donor Offers Surplus Food</div>
    <div style="color:#94A3B8;">&</div>
    <div class="workflow-step">🙋 NGO & Volunteer Request Food</div>
    <div style="color:#94A3B8;">➔</div>
    <div class="workflow-step">🎯 Smart Matcher</div>
    <div style="color:#94A3B8;">➔</div>
    <div class="workflow-step">🛵 Live GPS Delivery</div>
</div>
""", unsafe_allow_html=True)

# Navigation Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "1️⃣ Donor Surplus & AI Audit",
    "2️⃣ Smart NGO & Demand Matcher",
    "3️⃣ 🙋 NGO & Volunteer Request Hub",
    "4️⃣ 🛵 Live Delivery Tracker",
    "5️⃣ 📊 Executive Analytics"
])

# ==========================================
# TAB 1: DONOR SURPLUS & AI SAFETY AUDITOR
# ==========================================
with tab1:
    st.markdown("### 📝 Step 1: Donor Submits Surplus Food for AI Safety Audit")
    st.caption("Restaurants, hotels, & event caterers upload surplus food details for instant visual mold check, portion estimation, and safety scoring.")

    col_left, col_right = st.columns([1.1, 0.9])
    
    with col_left:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="panel-header">🏢 Donor Information & Pickup Location</div>', unsafe_allow_html=True)
        
        donor_name = st.text_input("Restaurant / Donor Name", value="Sree Annapoorna Restaurant")
        c_p1, c_p2 = st.columns(2)
        with c_p1:
            donor_contact = st.text_input("Contact Phone", value="+91 98422 54321")
        with c_p2:
            donor_address = st.text_input("Pickup Address", value="Palladam Main Road, Tiruppur, TN")
            
        c_g1, c_g2 = st.columns(2)
        with c_g1:
            donor_lat = st.number_input("Latitude", value=11.0850, format="%.4f")
        with c_g2:
            donor_lon = st.number_input("Longitude", value=77.3300, format="%.4f")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="panel-header">⏱️ Food Preparation & Container Specifications</div>', unsafe_allow_html=True)
        
        hours_elapsed = st.slider("Hours elapsed since preparation", min_value=0.5, max_value=12.0, value=2.0, step=0.5)
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            storage_condition = st.selectbox("Storage Condition", [
                "Refrigerated / Chilled (< 5°C)",
                "Covered & Room Temp (20-25°C)",
                "Open Air / Heated / Warm"
            ])
        with col_s2:
            container_type = st.selectbox("Container Type / Portion Size", [
                "Single Portion / Small Item (~0.2-0.5 kg)",
                "Small Packaging Tray (~2-3 kg)",
                "Medium Catering Vessel (~8-10 kg)",
                "Large Commercial Pot (~20-25 kg)",
                "Industrial Bulk Container (~50+ kg)",
                "Custom Weight (Manual Input)"
            ])
            
        if container_type == "Custom Weight (Manual Input)":
            custom_weight = st.number_input("Enter Weight (kg)", min_value=0.1, max_value=500.0, value=1.0)
            container_count = 1
        else:
            container_count = st.number_input("Number of Containers", min_value=1, max_value=50, value=1)
            custom_weight = None
        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="panel-header">📸 Food Photo Input & Visual Mold Detector</div>', unsafe_allow_html=True)
        
        image_source = st.radio("Select Image Input Source", ["Upload Own Photo", "Use Preset Demo Sample"], horizontal=True)
        selected_image = None
        
        if image_source == "Upload Own Photo":
            uploaded_file = st.file_uploader("Upload JPG/PNG photo", type=["jpg", "jpeg", "png"])
            if uploaded_file is not None:
                selected_image = Image.open(uploaded_file)
                st.image(selected_image, caption="Uploaded Food Photo", use_container_width=True)
            else:
                selected_image = generate_sample_image("Cooked Rice & Grain Dishes")
                st.info("👆 Upload a photo above or test with preset sample.")
        else:
            sample_choice = st.selectbox("Select Demo Preset Category", [
                "Cooked Rice & Grain Dishes",
                "Rich Curry & Stew",
                "Roti, Naan & Bread",
                "Fresh Salad & Vegetables",
                "Dessert & Sweets",
                "Assorted Mixed Meal / Buffet"
            ])
            selected_image = generate_sample_image(sample_choice)
            st.image(selected_image, caption=f"Preset Demo Sample: {sample_choice}", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### ⚡ Step 2: Execute AI Pipeline Audit")
    btn_analyze = st.button("🚀 CLICK HERE: RUN AI FOOD ANALYSIS PIPELINE")

    if btn_analyze:
        if selected_image is not None:
            with st.spinner("Analyzing visual features, fungal mold signals, weight estimation, & calculating safety..."):
                class_res = classifier.predict(selected_image)
                food_type = class_res['category']
                confidence = class_res['confidence']
                breakdown = class_res['breakdown']
                
                qty_res = quantity_estimator.estimate(container_type, container_count, food_type, custom_weight)
                
                evaluator = FoodSafetyEvaluator()
                safety_res = evaluator.evaluate(food_type, hours_elapsed, storage_condition, confidence, image=selected_image)
                
                if safety_res['is_safe_for_donation']:
                    donation_id = add_donation(
                        donor_name, donor_contact, donor_lat, donor_lon, donor_address,
                        food_type, confidence, qty_res['estimated_weight_kg'], qty_res['estimated_servings'],
                        safety_res['safety_tag'], safety_res['safety_score'],
                        f"{hours_elapsed} ago", storage_condition
                    )
                else:
                    donation_id = None
                
                st.session_state['last_analysis'] = {
                    "id": donation_id,
                    "food_type": food_type,
                    "confidence": confidence,
                    "breakdown": breakdown,
                    "qty": qty_res,
                    "safety": safety_res,
                    "donor_lat": donor_lat,
                    "donor_lon": donor_lon,
                    "donor_name": donor_name
                }

    if 'last_analysis' in st.session_state:
        res = st.session_state['last_analysis']
        st.markdown("---")
        st.markdown("### 🔍 Step 3: AI Analysis Audit Results")
        
        r1, r2, r3 = st.columns(3)
        
        with r1:
            st.markdown('<div class="panel-card">', unsafe_allow_html=True)
            st.markdown("#### 1. Food Classification (CNN)")
            st.info(f"**Identified Category:** {res['food_type']}")
            st.metric("Model Confidence", f"{int(res['confidence']*100)}%")
            df_probs = pd.DataFrame(list(res['breakdown'].items()), columns=["Category", "Probability"])
            fig_prob = px.bar(df_probs, x="Probability", y="Category", orientation="h", height=200)
            fig_prob.update_layout(margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig_prob, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with r2:
            st.markdown('<div class="panel-card">', unsafe_allow_html=True)
            st.markdown("#### 2. Quantity & Portion (ML)")
            st.metric("Estimated Servings", f"👥 {res['qty']['estimated_servings']} People")
            st.metric("Total Weight", f"⚖️ {res['qty']['estimated_weight_kg']} kg")
            st.caption(f"Estimated Energy: **{res['qty']['total_calories_kcal']:,} kcal**")
            st.caption(f"Landfill CO₂ Saved: **{round(res['qty']['estimated_weight_kg']*2.5, 1)} kg CO₂e**")
            st.markdown('</div>', unsafe_allow_html=True)

        with r3:
            st.markdown('<div class="panel-card">', unsafe_allow_html=True)
            st.markdown("#### 3. Food Safety & Mold Detector")
            tag = res['safety']['safety_tag']
            badge_html = {
                "Fresh": '<span class="badge-fresh">🟢 FRESH (Safe 4-6h)</span>',
                "Medium": '<span class="badge-medium">🟡 MEDIUM (Safe 2-3h)</span>',
                "Urgent": '<span class="badge-urgent">🔴 URGENT (Dispatch 1h)</span>',
                "Unsafe": '<span class="badge-unsafe">❌ REJECTED / SPOILED</span>'
            }.get(tag, tag)
            st.markdown(f"**Safety Status:** {badge_html}", unsafe_allow_html=True)
            st.write("")
            st.metric("Safety Score Index", f"{int(res['safety']['safety_score']*100)} / 100")
            st.write(f"*{res['safety']['description']}*")
            st.markdown('</div>', unsafe_allow_html=True)

        if res['safety']['is_safe_for_donation'] and res['id']:
            st.success(f"🎉 **FOOD APPROVED & REGISTERED!** Donation #{res['id']} added to database. Proceed to **Tab 2 (Smart Matcher)** to assign to recipient NGOs or Volunteer requests.")
        else:
            st.error("❌ **DONATION REJECTED & BLOCKED:** Visual fungal mold / spoilage detected! Food is unsafe for distribution.")

# ==========================================
# TAB 2: SMART NGO & DEMAND MATCHER
# ==========================================
with tab2:
    st.markdown("### 🎯 Step 4: Smart NGO & Community Demand Matcher")
    st.caption("Matches available surplus food donations with registered Tiruppur NGO shelters and active Volunteer community requests.")

    all_donations = get_all_donations()
    valid_donations = [d for d in all_donations if d['status'] in ['Pending', 'Matched'] and d['safety_tag'] != 'Unsafe']
    
    if not valid_donations:
        st.info("💡 **No active pending surplus donations.** Submit a safe donation in **Tab 1** first.")
    else:
        selected_donation_id = st.selectbox(
            "Select Available Surplus Donation to Match",
            options=[d['id'] for d in valid_donations],
            format_func=lambda x: f"Donation #{x} — {next((d['food_type'] for d in valid_donations if d['id'] == x), '')} ({next((d['estimated_servings'] for d in valid_donations if d['id'] == x), '')} servings, {next((d['donor_name'] for d in valid_donations if d['id'] == x), '')})"
        )
        
        target_donation = get_donation_by_id(selected_donation_id)
        
        if target_donation:
            # Active Donation Summary Bar
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1E3A8A 0%, #1E293B 100%); color: white; padding: 18px 24px; border-radius: 14px; margin-bottom: 24px; border-left: 6px solid #10B981;">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
                    <div>
                        <span style="font-size:1.1rem; font-weight:800;">📦 Surplus Order #{target_donation['id']}: {target_donation['food_type']}</span>
                        <div style="font-size:0.88rem; opacity:0.85; margin-top:2px;">Donor: {target_donation['donor_name']} | Address: {target_donation['donor_address']}</div>
                    </div>
                    <div style="display:flex; gap:16px;">
                        <div>👥 <b>{target_donation['estimated_servings']} Servings</b></div>
                        <div>⚖️ <b>{target_donation['estimated_weight_kg']} kg</b></div>
                        <div>🛡️ <b>Safety: {target_donation['safety_tag']}</b></div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Tab sub-navigation: Match with NGO Shelters vs Match with Volunteer Need Requests
            m_type = st.radio("Select Recipient Matching Mode", ["🏢 Match with Registered NGO Shelters", "🙋 Match with Active Volunteer / Community Need Requests"], horizontal=True)

            if "Registered NGO Shelters" in m_type:
                st.markdown("#### 🏆 Top Matched NGO Shelters (Tiruppur District)")
                ngos = get_all_ngos()
                matcher = SmartMatcher(ngos)
                matches = matcher.match(
                    donor_lat=target_donation['donor_lat'],
                    donor_lon=target_donation['donor_lon'],
                    estimated_servings=target_donation['estimated_servings'],
                    safety_tag=target_donation['safety_tag']
                )
                
                for idx, match in enumerate(matches):
                    is_top = (idx == 0)
                    card_class = "rec-card rec-card-top" if is_top else "rec-card"
                    top_tag = '<span style="background:#10B981; color:white; font-size:0.75rem; font-weight:800; padding:4px 10px; border-radius:12px; margin-left:10px;">🌟 #1 RECOMMENDED MATCH</span>' if is_top else ''
                    
                    st.markdown(f"""
                    <div class="{card_class}">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <h4 style="margin:0; color:#1E3A8A; font-weight:800;">#{idx+1} {match['name']} {top_tag}</h4>
                            <span style="background:#E0E7FF; color:#3730A3; font-size:1.1rem; font-weight:800; padding:6px 16px; border-radius:20px;">⚡ {match['match_score']}% Match</span>
                        </div>
                        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:12px; margin-top:14px; font-size:0.9rem; color:#374151;">
                            <div>📍 <b>Address:</b> {match['address']}</div>
                            <div>🚗 <b>Distance:</b> {match['distance_km']} km away</div>
                            <div>⏱️ <b>Transit Time:</b> ~{match['transit_time_mins']} mins</div>
                            <div>🏢 <b>Daily Capacity:</b> {match['capacity_servings']} Meals</div>
                            <div>📞 <b>Contact:</b> {match['contact']}</div>
                            <div>⏰ <b>Hours:</b> {match['operating_hours']}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    btn_assign = st.button(f"🎯 Assign & Send Dispatch Offer to {match['name']}", key=f"assign_{match['ngo_id']}")
                    if btn_assign:
                        assign_ngo_to_donation(target_donation['id'], match['ngo_id'], match['name'])
                        st.success(f"🎉 Offer sent for Donation #{target_donation['id']} to **{match['name']}**! NGO can now approve in Tab 3.")
                        st.rerun()
                    st.markdown("<br>", unsafe_allow_html=True)
            else:
                st.markdown("#### 🙋 Active Volunteer & Community Food Requests")
                reqs = [r for r in get_all_food_requests() if r['status'] == 'Open']
                if not reqs:
                    st.info("✨ No active open volunteer food requests right now. Volunteers can submit requests in Tab 3.")
                else:
                    for req in reqs:
                        urgency_badge = '<span class="badge-urgent">🔴 URGENT NEED</span>' if req['urgency'] == 'Urgent' else '<span class="badge-medium">🟡 STANDARD NEED</span>'
                        st.markdown(f"""
                        <div class="rec-card">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                                <h4 style="margin:0; color:#1E3A8A; font-weight:800;">🙋 {req['requester_name']} ({req['requester_type']})</h4>
                                {urgency_badge}
                            </div>
                            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:10px; font-size:0.9rem; color:#374151;">
                                <div>📍 <b>Location:</b> {req['address']}</div>
                                <div>🍲 <b>Food Needed:</b> {req['food_type']}</div>
                                <div>👥 <b>Servings Required:</b> {req['servings_needed']} Meals</div>
                                <div>📞 <b>Contact:</b> {req['contact']}</div>
                            </div>
                            <div style="margin-top:10px; font-size:0.88rem; color:#6B7280; background:#F8FAFC; padding:8px 12px; border-radius:8px;">
                                💬 <b>Notes:</b> {req['notes']}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button(f"🎯 Fulfill Request #{req['id']} with Donation #{target_donation['id']}", key=f"fulfill_req_{req['id']}"):
                            assign_ngo_to_donation(target_donation['id'], 999, f"{req['requester_name']} ({req['requester_type']})")
                            update_request_status(req['id'], 'Matched', target_donation['id'])
                            st.success(f"🎉 Donation #{target_donation['id']} assigned to fulfill {req['requester_name']}'s request! Track live in Tab 4.")
                            st.rerun()
                        st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# TAB 3: NGO & VOLUNTEER REQUEST HUB
# ==========================================
with tab3:
    st.markdown("### 🙋 NGO & Volunteer Food Need Request Hub")
    st.caption("NGO shelters and community volunteers can post urgent food requirements for people in need, or NGOs can accept incoming surplus food offers.")

    mode_choice = st.radio("Select Portal Action", ["➕ Submit Food Need Request (NGOs & Volunteers)", "📥 NGO Surplus Intake Approval Control Center"], horizontal=True)

    if mode_choice == "➕ Submit Food Need Request (NGOs & Volunteers)":
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="panel-header">📝 Request Food for People in Need</div>', unsafe_allow_html=True)
        
        req_type = st.selectbox("Requester Type", ["NGO Shelter / Welfare Home", "Community Volunteer / Individual Coordinator"])
        req_name = st.text_input("Name of NGO or Volunteer", value="Kavitha (Youth Volunteer)" if req_type != "NGO Shelter / Welfare Home" else "Hope Harbor Shelter")
        req_contact = st.text_input("Contact Phone Number", value="+91 97890 12345")
        req_address = st.text_input("Delivery / Need Location Address", value="Tiruppur Railway Station North Gate, TN")
        
        c_r1, c_r2 = st.columns(2)
        with c_r1:
            req_food_type = st.selectbox("Food Type Required", [
                "Assorted Mixed Meal / Buffet",
                "Cooked Rice & Grain Dishes",
                "Roti, Naan & Bread",
                "Rich Curry & Stew",
                "Fresh Salad & Vegetables",
                "Dessert & Sweets"
            ])
        with c_r2:
            req_servings = st.number_input("Number of Servings / Meals Needed", min_value=5, max_value=1000, value=30)
            
        req_urgency = st.selectbox("Urgency Priority", ["Urgent (Needed within 1-2 hours)", "Standard (Needed today)"])
        req_notes = st.text_area("Detailed Notes / Location Context", value="30 homeless individuals and migrant workers waiting near north gate entrance.")
        
        btn_submit_req = st.button("🚀 SUBMIT FOOD NEED REQUEST")
        if btn_submit_req:
            urg_val = "Urgent" if "Urgent" in req_urgency else "Standard"
            r_type_val = "NGO" if "NGO" in req_type else "Volunteer"
            req_id = add_food_request(r_type_val, req_name, req_contact, 11.1085, 77.3411, req_address, req_food_type, req_servings, urg_val, req_notes)
            st.success(f"🎉 **FOOD REQUEST #{req_id} BROADCASTED!** Donors & NGOs will see this request in **Tab 2 (Smart Matcher)**.")
            st.rerun()
            
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("### 📋 Active Community Need Requests Log")
        all_reqs = get_all_food_requests()
        if all_reqs:
            df_reqs = pd.DataFrame(all_reqs)
            st.dataframe(df_reqs[['id', 'requester_type', 'requester_name', 'food_type', 'servings_needed', 'urgency', 'address', 'status', 'created_at']], use_container_width=True)

    else:
        st.markdown("#### 📥 NGO Surplus Intake Approval Control Center")
        ngos = get_all_ngos()
        selected_ngo_id = st.selectbox(
            "Select Logged-in NGO Account",
            options=[n['id'] for n in ngos],
            format_func=lambda x: next((n['name'] for n in ngos if n['id'] == x), '')
        )
        ngo_info = next((n for n in ngos if n['id'] == selected_ngo_id), None)
        
        if ngo_info:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1F2937 0%, #111827 100%); color: white; padding: 22px; border-radius: 18px; border: 2px solid #10B981; margin-bottom: 25px;">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:15px;">
                    <div>
                        <h3 style="margin:0; color:#10B981; font-weight:800;">🏢 {ngo_info['name']}</h3>
                        <p style="margin:4px 0 0 0; opacity:0.85; font-size:0.92rem;">📍 {ngo_info['address']} | 📞 {ngo_info['contact']}</p>
                    </div>
                    <div style="text-align:right;">
                        <span style="background:#10B981; color:white; font-weight:bold; padding:6px 14px; border-radius:20px; font-size:13px;">🟢 INTAKE OPEN</span>
                        <p style="margin:6px 0 0 0; font-weight:bold; font-size:14px; color:#FBBF24;">Daily Capacity: {ngo_info['capacity_servings']} Meals</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            all_donations = get_all_donations()
            matched_to_this_ngo = [d for d in all_donations if d['matched_ngo_id'] == selected_ngo_id and d['status'] == 'Matched']
            accepted_by_this_ngo = [d for d in all_donations if d['matched_ngo_id'] == selected_ngo_id and d['status'] in ['Accepted', 'En Route', 'Completed']]
            
            st.markdown("### 📥 Active Pending Donation Offers")
            if not matched_to_this_ngo:
                st.info("✨ **No pending donation offers right now.** New food donations assigned to your shelter will appear here live.")
            else:
                for don in matched_to_this_ngo:
                    with st.container():
                        st.markdown(f"""
                        <div style="background:white; border-radius:16px; padding:20px; border:2px solid #3B82F6; box-shadow:0 6px 16px rgba(0,0,0,0.05); margin-bottom:15px;">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; flex-wrap:wrap; gap:10px;">
                                <h4 style="margin:0; color:#1E3A8A; font-weight:800;">📦 Order #{don['id']} — {don['food_type']}</h4>
                                <span class="badge-fresh">🟢 {don['safety_tag'].upper()} SAFETY SCORE: {int(don['safety_score']*100)}/100</span>
                            </div>
                            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:12px; font-size:0.9rem; color:#374151;">
                                <div>🏢 <b>Donor:</b> {don['donor_name']} ({don['donor_contact']})</div>
                                <div>📍 <b>Pickup:</b> {don['donor_address']}</div>
                                <div>⚖️ <b>Weight:</b> {don['estimated_weight_kg']} kg (~{don['estimated_servings']} Servings)</div>
                                <div>⏱️ <b>Prepared:</b> {don['prepared_time']}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        c1, c2 = st.columns(2)
                        with c1:
                            if st.button(f"✅ ACCEPT DONATION #{don['id']}", key=f"accept_ngo_{don['id']}"):
                                update_donation_status(don['id'], 'Accepted')
                                st.success(f"🎉 Donation #{don['id']} Accepted! Delivery driver assigned. Track live in **Tab 4 (Live Delivery Tracker)**.")
                                st.rerun()
                        with c2:
                            if st.button(f"❌ DECLINE OFFER #{don['id']}", key=f"decline_ngo_{don['id']}"):
                                update_donation_status(don['id'], 'Rejected')
                                st.warning("Offer declined.")
                                st.rerun()
                        st.markdown("---")

            if accepted_by_this_ngo:
                st.markdown("### 📜 Accepted & Completed Rescue Log")
                df_ngo_log = pd.DataFrame(accepted_by_this_ngo)
                st.dataframe(
                    df_ngo_log[['id', 'donor_name', 'food_type', 'estimated_weight_kg', 'estimated_servings', 'safety_tag', 'status', 'created_at']],
                    use_container_width=True
                )

# ==========================================
# TAB 4: LIVE DELIVERY TRACKER & SIMULATOR
# ==========================================
with tab4:
    st.markdown("### 🛵 Dynamic Live GPS Delivery Tracker")
    st.caption("Simulates real-time GPS courier navigation from Donor pickup point to recipient NGO shelter or Volunteer drop-off point.")

    all_donations = get_all_donations()
    accepted_donations = [d for d in all_donations if d['status'] in ['Accepted', 'En Route', 'Matched', 'Completed']]
    
    if not accepted_donations:
        st.info("💡 **No active deliveries in progress.** Submit and accept a donation in **Tab 3** to launch live GPS tracking.")
    else:
        selected_delivery_id = st.selectbox(
            "Select Active Delivery Order to Track",
            options=[d['id'] for d in accepted_donations],
            format_func=lambda x: f"Delivery Order #{x} — {next((d['donor_name'] for d in accepted_donations if d['id'] == x), '')} ➔ {next((d['matched_ngo_name'] for d in accepted_donations if d['id'] == x), 'Recipient')} ({next((d['estimated_servings'] for d in accepted_donations if d['id'] == x), '')} servings)"
        )
        
        target_delivery = get_donation_by_id(selected_delivery_id)
        
        if target_delivery:
            donor_name_text = target_delivery['donor_name']
            donor_address_text = target_delivery['donor_address'] or "Pickup Center"
            start_lat = float(target_delivery['donor_lat'])
            start_lon = float(target_delivery['donor_lon'])
            
            ngo_list = get_all_ngos()
            ngo_obj = next((n for n in ngo_list if n['id'] == target_delivery['matched_ngo_id']), None)
            
            ngo_name_text = target_delivery['matched_ngo_name'] or (ngo_obj['name'] if ngo_obj else "Recipient Shelter")
            ngo_address_text = ngo_obj['address'] if ngo_obj else "Recipient Address"
            end_lat = float(ngo_obj['lat']) if ngo_obj else start_lat + 0.015
            end_lon = float(ngo_obj['lon']) if ngo_obj else start_lon + 0.015

            dynamic_gps_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <style>
                @keyframes floatUpVibrant {{
                    0% {{ transform: translateY(100vh) scale(0.7) rotate(0deg); opacity: 0; }}
                    12% {{ opacity: 1; }}
                    88% {{ opacity: 1; }}
                    100% {{ transform: translateY(-130vh) scale(1.15) rotate(20deg); opacity: 0; }}
                }}
                @keyframes shineSparkle {{
                    0% {{ opacity: 0.4; }}
                    50% {{ opacity: 1; }}
                    100% {{ opacity: 0.4; }}
                }}
                body {{
                    margin: 0;
                    padding: 0;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    background-color: #F8FAFC;
                }}
                .swiggy-card-container {{
                    max-width: 950px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 20px;
                    overflow: hidden;
                    box-shadow: 0 12px 28px rgba(0,0,0,0.12);
                    border: 3px solid #10B981;
                    position: relative;
                }}
                .swiggy-header {{
                    background: linear-gradient(90deg, #10B981 0%, #059669 100%);
                    color: white;
                    text-align: center;
                    padding: 18px 20px;
                }}
                .swiggy-title {{
                    font-size: 22px;
                    font-weight: 800;
                    margin: 0;
                }}
                .swiggy-eta {{
                    font-size: 15px;
                    font-weight: 700;
                    margin-top: 6px;
                    background: rgba(255, 255, 255, 0.25);
                    display: inline-block;
                    padding: 4px 16px;
                    border-radius: 20px;
                }}
                .route-info {{
                    background: #1E293B;
                    color: white;
                    padding: 12px 20px;
                    display: flex;
                    justify-content: space-between;
                    font-size: 13.5px;
                    font-weight: 600;
                }}
                #map {{
                    height: 500px;
                    width: 100%;
                }}
                .notification-alert {{
                    display: none;
                    background: linear-gradient(90deg, #FF9F43 0%, #FF6B6B 100%);
                    color: white;
                    font-weight: bold;
                    text-align: center;
                    padding: 12px;
                    font-size: 16px;
                    animation: shineSparkle 1.2s infinite;
                }}

                /* 3D METALLIC BALLOONS OVERLAY */
                .vibrant-balloon-overlay {{
                    display: none;
                    position: fixed;
                    top: 0; left: 0; width: 100vw; height: 100vh;
                    pointer-events: none;
                    z-index: 999999;
                    overflow: hidden;
                }}
                .balloon-3d-vibrant {{
                    position: absolute;
                    bottom: -160px;
                    width: 85px;
                    height: 110px;
                    border-radius: 50% 50% 50% 50% / 40% 40% 60% 60%;
                    animation: floatUpVibrant 6.5s ease-in-out infinite;
                    filter: drop-shadow(0 15px 25px rgba(0,0,0,0.3));
                }}
                .b-gold {{
                    background: radial-gradient(circle at 35% 25%, #FFF066 0%, #FFD700 35%, #FF8C00 75%, #B85B00 100%);
                    box-shadow: inset -10px -12px 22px rgba(0,0,0,0.35), inset 14px 14px 28px rgba(255,255,255,0.95);
                    left: 10%; animation-delay: 0s;
                }}
                .b-magenta {{
                    background: radial-gradient(circle at 35% 25%, #FF85D0 0%, #FF1493 35%, #C70067 75%, #700039 100%);
                    box-shadow: inset -10px -12px 22px rgba(0,0,0,0.35), inset 14px 14px 28px rgba(255,255,255,0.95);
                    left: 26%; animation-delay: 1.2s;
                }}
                .b-cyan {{
                    background: radial-gradient(circle at 35% 25%, #A8FFFB 0%, #00F5D4 35%, #0096C7 75%, #004D7A 100%);
                    box-shadow: inset -10px -12px 22px rgba(0,0,0,0.35), inset 14px 14px 28px rgba(255,255,255,0.95);
                    left: 42%; animation-delay: 0.6s;
                }}
                .b-purple {{
                    background: radial-gradient(circle at 35% 25%, #E2B6FF 0%, #9D4EDD 35%, #5A189A 75%, #240046 100%);
                    box-shadow: inset -10px -12px 22px rgba(0,0,0,0.35), inset 14px 14px 28px rgba(255,255,255,0.95);
                    left: 74%; animation-delay: 0.3s;
                }}
                .balloon-string-white {{
                    position: absolute;
                    bottom: -50px;
                    left: 50%;
                    width: 2px;
                    height: 55px;
                    background: rgba(255,255,255,0.85);
                }}
            </style>
            </head>
            <body>

            <!-- 3D METALLIC BALLOONS OVERLAY -->
            <div class="vibrant-balloon-overlay" id="vibrantBalloons">
                <div class="balloon-3d-vibrant b-gold"><div class="balloon-string-white"></div></div>
                <div class="balloon-3d-vibrant b-magenta"><div class="balloon-string-white"></div></div>
                <div class="balloon-3d-vibrant b-cyan"><div class="balloon-string-white"></div></div>
                <div class="balloon-3d-vibrant b-purple"><div class="balloon-string-white"></div></div>
            </div>

            <div class="swiggy-card-container">
                <div class="swiggy-header">
                    <div class="swiggy-title">🛵 Live Delivery Courier en route for Order #{target_delivery['id']}</div>
                    <div class="swiggy-eta" id="etaText">Arriving in 15 minutes • 3.8 km remaining</div>
                </div>

                <div class="route-info">
                    <div>🏬 Pickup: <b>{donor_name_text}</b> ({donor_address_text})</div>
                    <div>🏢 Drop-off: <b>{ngo_name_text}</b> ({ngo_address_text})</div>
                </div>

                <div class="notification-alert" id="arrivalNotif">
                    🎉 AUTOMATIC ARRIVAL ALERT: Courier Hero arrived at {ngo_name_text}! Meals Handed Over Warm!
                </div>

                <div id="map"></div>
            </div>

            <script>
                const startLat = {start_lat}, startLon = {start_lon};
                const endLat = {end_lat}, endLon = {end_lon};

                const centerLat = (startLat + endLat) / 2.0;
                const centerLon = (startLon + endLon) / 2.0;

                const map = L.map('map', {{
                    center: [centerLat, centerLon],
                    zoom: 13,
                    zoomControl: true
                }});

                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                    maxZoom: 19,
                    minZoom: 10,
                    attribution: '&copy; OpenStreetMap GPS Navigation'
                }}).addTo(map);

                // Dynamic GPS Polyline
                const latlngs = [
                    [startLat, startLon],
                    [startLat + (endLat - startLat)*0.33, startLon + (endLon - startLon)*0.33],
                    [startLat + (endLat - startLat)*0.66, startLon + (endLon - startLon)*0.66],
                    [endLat, endLon]
                ];
                const polyline = L.polyline(latlngs, {{color: '#2563EB', weight: 7, opacity: 0.9, lineCap: 'round'}}).addTo(map);

                // Red Pickup Marker
                const redIcon = L.divIcon({{
                    html: '<div style="font-size: 30px; filter: drop-shadow(0 3px 6px rgba(0,0,0,0.4));">🏬</div>',
                    iconSize: [36, 36],
                    iconAnchor: [18, 18]
                }});
                L.marker([startLat, startLon], {{icon: redIcon}}).addTo(map).bindPopup("<b>🏬 {donor_name_text} (Pickup)</b><br>{donor_address_text}");

                // Green Drop-off Marker
                const greenIcon = L.divIcon({{
                    html: '<div style="font-size: 34px; filter: drop-shadow(0 3px 6px rgba(0,0,0,0.4));">🏢❤️</div>',
                    iconSize: [42, 42],
                    iconAnchor: [21, 21]
                }});
                L.marker([endLat, endLon], {{icon: greenIcon}}).addTo(map).bindPopup("<b>🏢 {ngo_name_text} (Drop-off)</b><br>{ngo_address_text}");

                // Live Moving Scooter Marker
                const scooterIcon = L.divIcon({{
                    html: '<div style="font-size: 38px; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.4));">🛵</div>',
                    iconSize: [45, 45],
                    iconAnchor: [22, 22]
                }});
                const scooterMarker = L.marker([startLat, startLon], {{icon: scooterIcon}}).addTo(map);

                // DYNAMIC REAL-TIME GPS TRIP
                let progress = 0.0;
                const etaEl = document.getElementById("etaText");
                const notifEl = document.getElementById("arrivalNotif");
                const vibrantBalloons = document.getElementById("vibrantBalloons");

                const interval = setInterval(() => {{
                    if (progress <= 1.0) {{
                        const curLat = startLat + (endLat - startLat) * progress;
                        const curLon = startLon + (endLon - startLon) * progress;

                        scooterMarker.setLatLng([curLat, curLon]);
                        
                        const remMins = Math.max(0, Math.round(15 * (1.0 - progress)));
                        const remKm = Math.max(0.0, (4.5 * (1.0 - progress)).toFixed(1));
                        
                        if (remMins > 0) {{
                            etaEl.innerHTML = "Arriving in " + remMins + " minutes • " + remKm + " km remaining";
                        }} else {{
                            etaEl.innerHTML = "🎉 ARRIVED AT {ngo_name_text}!";
                            etaEl.style.background = "#F59E0B";
                            notifEl.style.display = "block";
                            vibrantBalloons.style.display = "block";
                        }}
                        progress += 0.003;
                    }} else {{
                        clearInterval(interval);
                    }}
                }}, 250);
            </script>
            </body>
            </html>
            """

            components.html(dynamic_gps_html, height=620)

# ==========================================
# TAB 5: EXECUTIVE ANALYTICS DASHBOARD
# ==========================================
with tab5:
    st.markdown("### 📊 Executive System Impact & Sustainability Command Center")
    st.caption("Real-time metrics tracking donor surplus food supply, NGO/Volunteer food need requests, meal distributions, & landfill CO₂ offset.")

    donations = get_all_donations()
    requests = get_all_food_requests()

    if not donations and not requests:
        st.info("💡 **No donation or request data recorded yet.** Complete a donation in **Tab 1** or request in **Tab 3** to view real-time impact analytics.")
    else:
        df_donations = pd.DataFrame(donations) if donations else pd.DataFrame()
        df_requests = pd.DataFrame(requests) if requests else pd.DataFrame()
        
        # HIGH-GLOW KPI METRICS GRID
        k1, k2, k3, k4 = st.columns(4)
        accepted_df = df_donations[df_donations['status'].isin(['Accepted', 'Completed'])] if not df_donations.empty else pd.DataFrame()
        
        total_meals = accepted_df['estimated_servings'].sum() if not accepted_df.empty else 0
        total_kg = accepted_df['estimated_weight_kg'].sum() if not accepted_df.empty else 0
        total_donations = len(df_donations) if not df_donations.empty else 0
        total_requests = len(df_requests) if not df_requests.empty else 0
        fulfilled_reqs = len(df_requests[df_requests['status'].isin(['Matched', 'Fulfilled'])]) if not df_requests.empty else 0
        co2_saved_kg = round(total_kg * 2.5, 1)
        
        with k1:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-lbl">🍲 Total Meals Distributed</div>
                <div class="kpi-val">{total_meals:,}</div>
                <div style="font-size:0.8rem; opacity:0.8; margin-top:4px;">Servings Delivered</div>
            </div>
            """, unsafe_allow_html=True)
            
        with k2:
            st.markdown(f"""
            <div class="kpi-card" style="border-color:#10B981;">
                <div class="kpi-lbl">⚖️ Food Waste Prevented</div>
                <div class="kpi-val" style="color:#34D399;">{round(total_kg, 1)} kg</div>
                <div style="font-size:0.8rem; opacity:0.8; margin-top:4px;">Landfill Waste Diverted</div>
            </div>
            """, unsafe_allow_html=True)
            
        with k3:
            st.markdown(f"""
            <div class="kpi-card" style="border-color:#F59E0B;">
                <div class="kpi-lbl">🙋 Need Requests Fulfilled</div>
                <div class="kpi-val" style="color:#FBBF24;">{fulfilled_reqs} / {total_requests}</div>
                <div style="font-size:0.8rem; opacity:0.8; margin-top:4px;">NGO & Volunteer Requests</div>
            </div>
            """, unsafe_allow_html=True)
            
        with k4:
            st.markdown(f"""
            <div class="kpi-card" style="border-color:#8B5CF6;">
                <div class="kpi-lbl">🌱 CO₂ Offset Impact</div>
                <div class="kpi-val" style="color:#A78BFA;">{co2_saved_kg} kg</div>
                <div style="font-size:0.8rem; opacity:0.8; margin-top:4px;">CO₂e Emissions Avoided</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("---")
        
        # Interactive Plotly Charts
        g1, g2 = st.columns(2)
        with g1:
            st.markdown('<div class="panel-card">', unsafe_allow_html=True)
            st.markdown("#### 🥗 Rescued Food Category Breakdown")
            if not df_donations.empty and 'food_type' in df_donations:
                category_counts = df_donations['food_type'].value_counts().reset_index()
                category_counts.columns = ['Food Type', 'Count']
                fig_cat = px.pie(
                    category_counts, names='Food Type', values='Count', hole=0.45,
                    color_discrete_sequence=px.colors.qualitative.Bold
                )
                fig_cat.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=280)
                st.plotly_chart(fig_cat, use_container_width=True)
            else:
                st.info("No category data available.")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with g2:
            st.markdown('<div class="panel-card">', unsafe_allow_html=True)
            st.markdown("#### 🛡️ AI Food Safety Audit Distribution")
            if not df_donations.empty and 'safety_tag' in df_donations:
                safety_counts = df_donations['safety_tag'].value_counts().reset_index()
                safety_counts.columns = ['Safety Tag', 'Count']
                fig_safe = px.bar(
                    safety_counts, x='Safety Tag', y='Count', color='Safety Tag',
                    color_discrete_map={'Fresh': '#10B981', 'Medium': '#F59E0B', 'Urgent': '#EF4444', 'Unsafe': '#7F1D1D'}
                )
                fig_safe.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=280)
                st.plotly_chart(fig_safe, use_container_width=True)
            else:
                st.info("No safety audit data available.")
            st.markdown('</div>', unsafe_allow_html=True)
            
        # Table 1: Master Donor Surplus Registry
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown("#### 🏢 Master Food Donation & Surplus Registry (Donors List)")
        if not df_donations.empty:
            st.dataframe(
                df_donations[['id', 'donor_name', 'food_type', 'estimated_weight_kg', 'estimated_servings', 'safety_tag', 'matched_ngo_name', 'status', 'created_at']],
                use_container_width=True
            )
        else:
            st.info("No donor listings recorded.")
        st.markdown('</div>', unsafe_allow_html=True)

        # Table 2: Master Community Need & Food Distribution Registry
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown("#### 🙋 Master Community Need & Food Distribution Registry (NGO & Volunteer Requests)")
        if not df_requests.empty:
            st.dataframe(
                df_requests[['id', 'requester_type', 'requester_name', 'food_type', 'servings_needed', 'urgency', 'address', 'status', 'matched_donation_id', 'created_at']],
                use_container_width=True
            )
        else:
            st.info("No community need requests recorded.")
        st.markdown('</div>', unsafe_allow_html=True)
