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
# MODEL
# -----------------------------
if not os.path.exists("model.pkl"):
    url = "https://1drv.ms/u/c/b6927c3fb5126c71/IQD2frYLeQ9GQrDyCpBTOIdiAU5RQ8YGMhwCM106XSFk-_g?e=PQVZDI"
    gdown.download(url, "model.pkl", quiet=False)
@st.cache_resource
def load_model():
    model = pickle.load(open("model.pkl", "rb"))
    columns = pickle.load(open("columns.pkl", "rb"))
    le = pickle.load(open("label_encoder.pkl", "rb"))
    return model, columns, le

model, columns, le = load_model()

# -----------------------------
# MONGO (UNCHANGED)
# -----------------------------
client = MongoClient(st.secrets("MONGO_URI"))
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
    # DATASET (FULL)
    # -----------------------------
    data = [
        {"Disease":"Common Cold","Description":"Viral infection affecting nose and throat.","Foods_to_Eat":"Warm soup; Ginger tea; Honey; Citrus fruits; Garlic; Herbal tea","Foods_to_Avoid":"Cold drinks; Ice cream; Junk food; Fried food","Note":"Stay hydrated"},
        {"Disease":"Osteoporosis","Description":"Weak bones.","Foods_to_Eat":"Milk; Cheese; Yogurt; Almonds; Broccoli","Foods_to_Avoid":"Caffeine; Soda","Note":"Calcium needed"},
        {"Disease":"Bronchitis","Description":"Lung inflammation.","Foods_to_Eat":"Warm fluids; Honey; Ginger","Foods_to_Avoid":"Smoking; Cold drinks","Note":"Avoid pollution"},
        {"Disease":"Eczema","Description":"Skin inflammation.","Foods_to_Eat":"Fruits; Vegetables; Omega-3","Foods_to_Avoid":"Dairy; Sugar","Note":"Hydrate skin"},
        {"Disease":"Multiple Sclerosis","Description":"Nerve disease.","Foods_to_Eat":"Healthy fats; Fish","Foods_to_Avoid":"Processed food","Note":"Balanced diet"},
        {"Disease":"Osteoarthritis","Description":"Joint pain.","Foods_to_Eat":"Fish; Nuts; Vegetables","Foods_to_Avoid":"Fried food","Note":"Maintain weight"},
        {"Disease":"Hypothyroidism","Description":"Low thyroid.","Foods_to_Eat":"Eggs; Dairy","Foods_to_Avoid":"Soy","Note":"Balanced nutrition"},
        {"Disease":"Gastroenteritis","Description":"Stomach infection.","Foods_to_Eat":"Rice; Banana; ORS","Foods_to_Avoid":"Spicy food","Note":"Hydration"},
        {"Disease":"Allergic Rhinitis","Description":"Allergy condition.","Foods_to_Eat":"Fruits; Vitamin C","Foods_to_Avoid":"Dust","Note":"Avoid triggers"},
        {"Disease":"Depression","Description":"Mental disorder.","Foods_to_Eat":"Fish; Nuts","Foods_to_Avoid":"Alcohol","Note":"Healthy lifestyle"},
        {"Disease":"Hyperthyroidism","Description":"High thyroid.","Foods_to_Eat":"Vegetables","Foods_to_Avoid":"Iodine excess","Note":"Monitor"},
        {"Disease":"Migraine","Description":"Headache.","Foods_to_Eat":"Banana; Almonds","Foods_to_Avoid":"Caffeine","Note":"Avoid triggers"},
        {"Disease":"Psoriasis","Description":"Skin disease.","Foods_to_Eat":"Vegetables","Foods_to_Avoid":"Alcohol","Note":"Reduce inflammation"},
        {"Disease":"Stroke","Description":"Brain damage.","Foods_to_Eat":"Fruits; Fish","Foods_to_Avoid":"Salt","Note":"Heart diet"},
        {"Disease":"Hypertension","Description":"High BP.","Foods_to_Eat":"Bananas","Foods_to_Avoid":"Salt","Note":"Low sodium"},
        {"Disease":"Urinary Tract Infection","Description":"Urinary infection.","Foods_to_Eat":"Water; Juice","Foods_to_Avoid":"Caffeine","Note":"Hydrate"},
        {"Disease":"Pneumonia","Description":"Lung infection.","Foods_to_Eat":"Soup; Fluids","Foods_to_Avoid":"Cold drinks","Note":"Rest"},
        {"Disease":"Alzheimer's Disease","Description":"Memory loss.","Foods_to_Eat":"Nuts; Fish","Foods_to_Avoid":"Sugar","Note":"Brain diet"},
        {"Disease":"Coronary Artery Disease","Description":"Heart blockage.","Foods_to_Eat":"Oats; Fish","Foods_to_Avoid":"Fried food","Note":"Low fat"},
        {"Disease":"Rheumatoid Arthritis","Description":"Joint disease.","Foods_to_Eat":"Omega-3","Foods_to_Avoid":"Sugar","Note":"Anti-inflammatory"},
        {"Disease":"Liver Cancer","Description":"Liver cancer.","Foods_to_Eat":"Fruits","Foods_to_Avoid":"Alcohol","Note":"Care needed"},
        {"Disease":"Parkinson's Disease","Description":"Movement disorder.","Foods_to_Eat":"Fiber","Foods_to_Avoid":"Processed food","Note":"Balanced diet"},
        {"Disease":"Kidney Disease","Description":"Kidney issue.","Foods_to_Eat":"Low sodium foods","Foods_to_Avoid":"Salt","Note":"Monitor"},
        {"Disease":"Anxiety Disorders","Description":"Mental issue.","Foods_to_Eat":"Nuts","Foods_to_Avoid":"Caffeine","Note":"Relax"},
        {"Disease":"Liver Disease","Description":"Liver problem.","Foods_to_Eat":"Vegetables","Foods_to_Avoid":"Alcohol","Note":"Avoid toxins"},
        {"Disease":"Diabetes","Description":"High sugar.","Foods_to_Eat":"Whole grains","Foods_to_Avoid":"Sugar","Note":"Control"},
        {"Disease":"Asthma","Description":"Breathing issue.","Foods_to_Eat":"Fruits","Foods_to_Avoid":"Cold drinks","Note":"Avoid triggers"},
        {"Disease":"Influenza","Description":"Flu.","Foods_to_Eat":"Soup","Foods_to_Avoid":"Cold drinks","Note":"Rest"},
        {"Disease":"Kidney Cancer","Description":"Kidney cancer.","Foods_to_Eat":"Healthy diet","Foods_to_Avoid":"Processed food","Note":"Medical care"}
    ]

    df = pd.DataFrame(data)
    diseases = df["Disease"].tolist()

    def find_matches(q):
        results = process.extract(q, diseases, scorer=fuzz.token_sort_ratio, limit=5)
        return df[df["Disease"].isin([r[0] for r in results if r[1] > 50])]

    # -----------------------------
    # TABS
    # -----------------------------
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["🔎 Search", "📊 BMI", "📈 History", "🥗 Diet", "🧠 Prediction"]
    )

    # TAB 1
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

    # TAB 2 BMI
    with tab2:
        weight = st.number_input("Weight", min_value=1.0)
        height = st.number_input("Height", min_value=0.5)

        if st.button("Calculate BMI"):
            bmi = weight / (height**2)
            st.success(f"BMI: {round(bmi,2)}")
            bmi_collection.insert_one({"username": st.session_state.username, "bmi": bmi})

    # TAB 3 HISTORY
    with tab3:
        records = list(bmi_collection.find({"username": st.session_state.username}))
        if records:
            vals = [r["bmi"] for r in records]
            st.dataframe(pd.DataFrame(records))
            fig, ax = plt.subplots()
            ax.plot(vals)
            st.pyplot(fig)

    # TAB 4 DIET
    with tab4:
        goal = st.selectbox("Goal", ["Weight Loss","Muscle Gain","Healthy"])
        if st.button("Generate"):
            st.write("Diet plan for", goal)

    # TAB 5 ML
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
            st.success(disease_name[0])
