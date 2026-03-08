import streamlit as st
import pandas as pd
from rapidfuzz import process, fuzz
from huggingface_hub import InferenceClient
from pymongo import MongoClient
import matplotlib.pyplot as plt

# -----------------------------
# SESSION STATE
# -----------------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

# -----------------------------
# HUGGING FACE API
# -----------------------------

HF_TOKEN = ""

client_ai = InferenceClient(api_key=HF_TOKEN)

# -----------------------------
# MONGODB CONNECTION
# -----------------------------

MONGO_URI = "mongodb+srv://yvasundhara87_db_user:fS7r5CXOllfvIUUw@cluster0.kinaeyu.mongodb.net/?appName=Cluster0"

mongo_client = MongoClient(MONGO_URI)

db = mongo_client["health_app"]

users_collection = db["users"]
bmi_collection = db["bmi_records"]

# -----------------------------
# PAGE CONFIG
# -----------------------------

st.set_page_config(page_title="Food Recommendation System", layout="centered")

st.title("🍎 Food Recommendation System")

# -----------------------------
# LOGIN / REGISTER
# -----------------------------

menu = ["Login", "Register"]

choice = st.sidebar.selectbox("Account", menu)

# LOGOUT
if st.session_state.logged_in:
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

# -----------------------------
# REGISTER
# -----------------------------

if choice == "Register" and not st.session_state.logged_in:

    st.subheader("Create Account")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Register"):

        user = users_collection.find_one({"username": username})

        if user:
            st.warning("User already exists")

        else:

            users_collection.insert_one({
                "username": username,
                "password": password
            })

            st.success("Account created successfully")

# -----------------------------
# LOGIN
# -----------------------------

elif choice == "Login" and not st.session_state.logged_in:

    st.subheader("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        user = users_collection.find_one({
            "username": username,
            "password": password
        })

        if user:

            st.session_state.logged_in = True
            st.session_state.username = username

            st.success("Login successful")

            st.rerun()

        else:
            st.error("Invalid username or password")

# -----------------------------
# MAIN APP AFTER LOGIN
# -----------------------------

if st.session_state.logged_in:

    username = st.session_state.username

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔎 Disease Search",
        "📊 BMI Calculator",
        "📈 BMI History",
        "🥗 Diet Planner",
        "🤖 AI Chatbot"
    ])

    # -----------------------------
    # DATASET
    # -----------------------------

    data = [
    {"Disease":"Type 2 Diabetes","Foods_to_Eat":"Whole grains; Vegetables; Legumes; Lean proteins; Nuts","Foods_to_Avoid":"Sugary drinks; White bread; Pastries","Nutritional_Note":"Low glycemic foods recommended"},
    {"Disease":"Hypertension","Foods_to_Eat":"Fruits; Vegetables; Whole grains; Low fat dairy","Foods_to_Avoid":"High salt foods; Chips; Processed meat","Nutritional_Note":"Follow DASH diet"},
    {"Disease":"Heart Disease","Foods_to_Eat":"Oats; Fish; Nuts; Fruits; Vegetables","Foods_to_Avoid":"Fried food; Red meat","Nutritional_Note":"Focus on fiber and healthy fats"},
    {"Disease":"Fatty Liver","Foods_to_Eat":"Vegetables; Fruits; Whole grains; Olive oil","Foods_to_Avoid":"Sugar drinks; Alcohol","Nutritional_Note":"Weight loss recommended"},
    {"Disease":"Anemia","Foods_to_Eat":"Spinach; Beans; Red meat; Eggs; Vitamin C foods","Foods_to_Avoid":"Tea; Coffee after meals","Nutritional_Note":"Iron + vitamin C improves absorption"}
    ]

    df = pd.DataFrame(data)

    diseases = df["Disease"].tolist()

    # -----------------------------
    # FUZZY SEARCH FUNCTION
    # -----------------------------

    def find_matches(query):

        q = query.strip().lower()

        if not q:
            return pd.DataFrame()

        choices = df["Disease"].tolist()

        results = process.extract(
            q,
            choices,
            scorer=fuzz.token_sort_ratio,
            limit=5
        )

        matches = [r[0] for r in results if r[1] > 50]

        return df[df["Disease"].isin(matches)]

    # -----------------------------
    # TAB 1 DISEASE SEARCH
    # -----------------------------

    with tab1:

        st.header("🔎 Search Disease")

        query = st.text_input("Type disease name")

        selected = st.selectbox(
            "Or select disease",
            ["-- none --"] + diseases
        )

        results_df = pd.DataFrame()

        if selected != "-- none --":
            results_df = df[df["Disease"] == selected]

        elif query:
            results_df = find_matches(query)

        if results_df.empty:
            st.info("Search or select a disease")

        else:

            for _, row in results_df.iterrows():

                st.subheader(row["Disease"])

                st.write("### Foods to Eat")

                for item in row["Foods_to_Eat"].split(";"):
                    st.write("•", item.strip())

                st.write("### Foods to Avoid")

                for item in row["Foods_to_Avoid"].split(";"):
                    st.write("•", item.strip())

                st.write("### Nutrition Note")
                st.write(row["Nutritional_Note"])

    # -----------------------------
    # TAB 2 BMI CALCULATOR
    # -----------------------------

    with tab2:

        st.header("📊 BMI Calculator")

        weight = st.number_input("Weight (kg)", min_value=1.0)

        height = st.number_input("Height (meters)", min_value=0.5)

        if st.button("Calculate BMI"):

            bmi = weight / (height ** 2)

            st.subheader(f"Your BMI: {round(bmi,2)}")

            bmi_collection.insert_one({
                "username": username,
                "weight": weight,
                "height": height,
                "bmi": bmi
            })

            st.success("BMI saved")

    # -----------------------------
    # TAB 3 BMI HISTORY GRAPH
    # -----------------------------

    with tab3:

        st.header("📈 BMI History")

        records = list(bmi_collection.find({"username": username}))

        if records:

            bmi_values = [r["bmi"] for r in records]

            st.write("Past BMI Records")

            st.dataframe(pd.DataFrame(records))

            fig, ax = plt.subplots()

            ax.plot(bmi_values, marker='o')

            ax.set_title("BMI Progress")

            ax.set_ylabel("BMI")

            ax.set_xlabel("Record")

            st.pyplot(fig)

        else:

            st.info("No BMI history yet")

    # -----------------------------
    # TAB 4 DIET PLANNER
    # -----------------------------

    with tab4:

        st.header("🥗 Diet Planner")

        goal = st.selectbox(
            "Select your goal",
            ["Weight Loss", "Muscle Gain", "Healthy Diet"]
        )

        if st.button("Generate Diet Plan"):

            if goal == "Weight Loss":

                st.write("Breakfast: Oatmeal + Fruits")
                st.write("Lunch: Brown rice + Vegetables")
                st.write("Dinner: Soup + Salad")

            elif goal == "Muscle Gain":

                st.write("Breakfast: Eggs + Toast")
                st.write("Lunch: Chicken + Rice")
                st.write("Dinner: Fish + Vegetables")

            else:

                st.write("Breakfast: Fruits + Yogurt")
                st.write("Lunch: Rice + Dal")
                st.write("Dinner: Chapati + Paneer")

    # -----------------------------
    # TAB 5 AI CHATBOT
    # -----------------------------

    with tab5:

        st.header("🤖 AI Nutrition Chatbot")

        question = st.text_input("Ask health question")

        if st.button("Ask AI"):

            if question:

                completion = client_ai.chat.completions.create(
                    model="mistralai/Mistral-7B-Instruct-v0.3",
                    messages=[
                        {"role":"system","content":"You are a nutrition expert"},
                        {"role":"user","content":question}
                    ],
                    max_tokens=200
                )

                answer = completion.choices[0].message.content

                st.write(answer)



