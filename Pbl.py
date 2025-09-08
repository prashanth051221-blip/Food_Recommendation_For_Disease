import streamlit as st
import pandas as pd

# Sample Indian food data for disease conditions
data = {
    'Food': [
        'Moong Dal Chilla', 'Oats Upma', 'Palak (Spinach) Sabzi', 'Chana Salad',
        'Dahi (Curd)', 'Brown Rice Pulao', 'Roti (Whole Wheat)', 'Bhindi (Okra) Curry',
        'Grilled Tandoori Chicken', 'Mixed Vegetable Curry', 'Rajma (Kidney Beans) Curry'
    ],
    'Suitable_for': [
        'Diabetes, Heart Disease', 'Diabetes, Hypertension', 'Heart Disease, Hypertension',
        'Diabetes, Heart Disease', 'Diabetes, Heart Disease, Hypertension',
        'Diabetes, Heart Disease', 'Diabetes, Heart Disease, Hypertension',
        'Heart Disease, Hypertension', 'Heart Disease', 'Hypertension, Heart Disease', 'Diabetes, Hypertension'
    ]
}
df = pd.DataFrame(data)

# Streamlit ui
st.title("Disease-Based Indian Food Recommendation System")

diseases = ['Diabetes', 'Heart Disease', 'Hypertension', 'None']
selected_disease = st.selectbox("Select your disease/condition", diseases)

if selected_disease != 'None':
    st.subheader(f"Recommended Indian Foods for {selected_disease}:")
    filtered = df[df['Suitable_for'].str.contains(selected_disease)]
    st.table(filtered[['Food']])
else:
    st.subheader("Recommended Healthy Indian Foods:")
    st.table(df[['Food']])
# app.py
import base64
from pathlib import Path

# 1) Point to the attached image path (save the file into your repo/app folder)
BG_PATH = Path("backround-image.jpeg")  # exact filename from the attachment

def set_background(image_path: Path):
    if not image_path.exists():
        st.error(f"Background image not found: {image_path.resolve()}")
        return

    ext = image_path.suffix.lstrip(".").lower() or "jpeg"
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/{ext};base64,{encoded}");
        background-size: cover;
        background-repeat: no-repeat;
        background-position: center center;
        background-attachment: fixed;
    }}
    /* Optional readability overlays */
    [data-testid="stAppViewContainer"] > .main {{
        background: rgba(255,255,255,0.72);
        backdrop-filter: blur(2px);
    }}
    [data-testid="stSidebar"] {{
        background: rgba(255,255,255,0.85);
        backdrop-filter: blur(2px);
    }}
    [data-testid="stHeader"] {{
        background: rgba(255,255,255,0.60);
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Call this before building the UI
set_background(BG_PATH)

st.title("Disease-Based Indian Food Recommendation")
st.write("Background set from local file: backround-image.jpeg")



