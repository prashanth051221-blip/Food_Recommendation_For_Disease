import streamlit as st
import pandas as pd
import pickle
from pymongo import MongoClient
import os
from rapidfuzz import process, fuzz
import matplotlib.pyplot as plt
import gdown

# -----------------------------
# BACKGROUND
# -----------------------------
def set_bg():
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(to bottom right, #a8d8e8, #1e6fb9);
        }
        .block-container {
            background: rgba(0,0,0,0.6);
            padding: 1.5rem;
            border-radius: 15px;
        }
        h1,h2,h3 { color:white; }
        </style>
    """, unsafe_allow_html=True)

# -----------------------------
# DOWNLOAD MODEL FILES (FIXED)
# -----------------------------
def download_files():
    files = {
        "model.pkl": "1YM1m34g0d9FXvmAk8YFTeT9mq0ccuFeN",
        "columns.pkl": "1cO6XOBDWPl3PlOIJ-RVZsa3pHO-qtT46",
        "label_encoder.pkl": "10szcH40veSjYbH3N1XX1DNND6t3UW6PH"
    }

    for file, fid in files.items():
        if not os.path.exists(file):
            url = f"https://drive.google.com/uc?id={fid}"
            gdown.download(url, file, quiet=False)

# -----------------------------
# LOAD MODEL
# -----------------------------
@st.cache_resource
def load_model():
    download_files()

    model = pickle.load(open("model.pkl", "rb"))
    columns = pickle.load(open("columns.pkl", "rb"))
    le = pickle.load(open("label_encoder.pkl", "rb"))

    return model, columns, le

model, columns, le = load_model()

# -----------------------------
# MONGO (FIXED)
# -----------------------------
client = MongoClient(st.secrets["MONGO_URI"])
db = client["health_app"]
users_collection = db["users"]
bmi_collection = db["bmi_records"]

# -----------------------------
# SESSION
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# -----------------------------
# UI
# -----------------------------
st.set_page_config(page_title="AI Health Assistant")
set_bg()
st.title("🩺 AI Health Assistant")

menu = st.sidebar.selectbox("Menu", ["Login", "Register"])

# -----------------------------
# REGISTER
# -----------------------------
if menu == "Register" and not st.session_state.logged_in:
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        if users_collection.find_one({"username": username}):
            st.warning("User exists")
        else:
            users_collection.insert_one({"username": username, "password": password})
            st.success("Registered")

# -----------------------------
# LOGIN
# -----------------------------
elif menu == "Login" and not st.session_state.logged_in:
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = users_collection.find_one({"username": username, "password": password})
        if user:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.rerun()
        else:
            st.error("Invalid credentials")

# -----------------------------
# MAIN APP
# -----------------------------
if st.session_state.logged_in:

    st.sidebar.success(f"Logged in as {st.session_state.username}")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    # -----------------------------
    # DATASET
    # -----------------------------
    data = [
        {"Disease":"Common Cold","Description":"Viral infection affecting nose and throat.","Foods_to_Eat":"Warm soup; Ginger tea; Honey; Citrus fruits; Garlic; Herbal tea","Foods_to_Avoid":"Cold drinks; Ice cream; Junk food; Fried food","Note":"Stay hydrated"},
        {"Disease":"Diabetes","Description":"High blood sugar condition.","Foods_to_Eat":"Whole grains; Vegetables; Nuts","Foods_to_Avoid":"Sugar; Soft drinks","Note":"Control glucose"},
        {"Disease":"Hypertension","Description":"High BP.","Foods_to_Eat":"Fruits; Vegetables","Foods_to_Avoid":"Salt","Note":"Low sodium"},
        {"Disease":"Asthma","Description":"Breathing issue.","Foods_to_Eat":"Fruits; Vegetables","Foods_to_Avoid":"Cold drinks","Note":"Avoid triggers"},
        {"Disease":"Migraine","Description":"Headache.","Foods_to_Eat":"Banana; Almonds","Foods_to_Avoid":"Caffeine","Note":"Avoid triggers"}
    ]

    df = pd.DataFrame(data)
    diseases = df["Disease"].tolist()

    def find_matches(q):
        results = process.extract(q, diseases, scorer=fuzz.token_sort_ratio, limit=5)
        return df[df["Disease"].isin([r[0] for r in results if r[1] > 50])]

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["🔎 Search", "📊 BMI", "📈 History", "🥗 Diet", "🧠 Prediction"]
    )

    # SEARCH
    with tab1:
        query = st.text_input("Search Disease")
        if query:
            results = find_matches(query)
            for _, row in results.iterrows():
                st.subheader(row["Disease"])
                st.write("🧾", row["Description"])

                for i in row["Foods_to_Eat"].split(";"):
                    st.write("✅", i.strip())

                for i in row["Foods_to_Avoid"].split(";"):
                    st.write("❌", i.strip())

                st.info(row["Note"])

    # BMI
    with tab2:
        weight = st.number_input("Weight", min_value=1.0)
        height = st.number_input("Height", min_value=0.5)

        if st.button("Calculate BMI"):
            bmi = weight / (height**2)
            st.success(f"BMI: {round(bmi,2)}")

            bmi_collection.insert_one({
                "username": st.session_state.username,
                "bmi": bmi
            })

    # HISTORY
    with tab3:
        records = list(bmi_collection.find({"username": st.session_state.username}))

        if records:
            vals = [r["bmi"] for r in records]
            st.dataframe(pd.DataFrame(records))

            fig, ax = plt.subplots()
            ax.plot(vals)
            st.pyplot(fig)
        else:
            st.info("No history found")

    # DIET
    with tab4:
        goal = st.selectbox("Goal", ["Weight Loss","Muscle Gain","Healthy"])
        if st.button("Generate Diet Plan"):
            st.write("Diet plan for", goal)

    # ML
    with tab5:
        input_dict = {}
        cols_ui = st.columns(2)

        for i, col in enumerate(columns):
            with cols_ui[i % 2]:
                input_dict[col] = st.checkbox(col)

        if st.button("Predict"):
            input_data = [1 if input_dict[col] else 0 for col in columns]
            pred = model.predict([input_data])
            disease_name = le.inverse_transform(pred)

            st.success(f"Predicted: {disease_name[0]}")
