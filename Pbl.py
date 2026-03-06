import streamlit as st
import pandas as pd
from rapidfuzz import process, fuzz

st.set_page_config(page_title="Food Recommendation for Disease", layout="centered")

st.title("🍎 Food Recommendation System")
st.markdown("Educational tool that recommends foods for diseases. *Not medical advice.*")

# Tabs
tab1, tab2, tab3 = st.tabs([
    "🔎 Disease Search",
    "📊 BMI Calculator",
    "🥗 Diet Planner"
])

# ---------------------------
# DATASET
# ---------------------------

data = [

{"Disease":"Type 2 Diabetes","Foods_to_Eat":"Whole grains; Vegetables; Legumes; Lean proteins; Nuts","Foods_to_Avoid":"Sugary drinks; White bread; Pastries","Nutritional_Note":"Low glycemic foods recommended"},

{"Disease":"Hypertension","Foods_to_Eat":"Fruits; Vegetables; Whole grains; Low fat dairy","Foods_to_Avoid":"High salt foods; Chips; Processed meat","Nutritional_Note":"Follow DASH diet"},

{"Disease":"Heart Disease","Foods_to_Eat":"Oats; Fish; Nuts; Fruits; Vegetables","Foods_to_Avoid":"Fried food; Red meat","Nutritional_Note":"Focus on fiber and healthy fats"},

{"Disease":"Fatty Liver","Foods_to_Eat":"Vegetables; Fruits; Whole grains; Olive oil","Foods_to_Avoid":"Sugar drinks; Alcohol","Nutritional_Note":"Weight loss recommended"},

{"Disease":"Anemia","Foods_to_Eat":"Spinach; Beans; Red meat; Eggs; Vitamin C foods","Foods_to_Avoid":"Tea; Coffee after meals","Nutritional_Note":"Iron + vitamin C improves absorption"}

]

df = pd.DataFrame(data)
df["Disease_lower"] = df["Disease"].str.lower()
diseases = df["Disease"].tolist()

# ---------------------------
# SEARCH FUNCTION
# ---------------------------

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

# ---------------------------
# TAB 1 — DISEASE SEARCH
# ---------------------------

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

            st.write("### ✅ Foods to Eat")

            for item in row["Foods_to_Eat"].split(";"):
                st.write("•", item.strip())

            st.write("### ⛔ Foods to Avoid")

            for item in row["Foods_to_Avoid"].split(";"):
                st.write("•", item.strip())

            st.write("### 📌 Nutrition Note")

            st.write(row["Nutritional_Note"])

            st.markdown("---")

    with st.expander("View dataset"):
        st.dataframe(df.drop(columns=["Disease_lower"]))

# ---------------------------
# TAB 2 — BMI CALCULATOR
# ---------------------------

with tab2:

    st.header("📊 BMI Calculator")

    weight = st.number_input("Enter weight (kg)", min_value=1.0)
    height = st.number_input("Enter height (meters)", min_value=0.5)

    if st.button("Calculate BMI"):

        bmi = weight / (height ** 2)

        st.subheader(f"Your BMI: {round(bmi,2)}")

        if bmi < 18.5:
            st.warning("Underweight")

        elif bmi < 25:
            st.success("Normal Weight")

        elif bmi < 30:
            st.warning("Overweight")

        else:
            st.error("Obese")

# ---------------------------
# TAB 3 — DIET PLANNER
# ---------------------------

with tab3:

    st.header("🥗 Daily Diet Planner")

    goal = st.selectbox(
        "Select your goal",
        ["Weight Loss", "Muscle Gain", "Healthy Diet"]
    )

    if st.button("Generate Diet Plan"):

        if goal == "Weight Loss":

            st.write("🍳 Breakfast: Oatmeal + Fruits")
            st.write("🥗 Lunch: Brown rice + Vegetables")
            st.write("🍲 Dinner: Soup + Salad")
            st.write("🥜 Snacks: Nuts")

        elif goal == "Muscle Gain":

            st.write("🍳 Breakfast: Eggs + Whole wheat toast")
            st.write("🥗 Lunch: Chicken / Paneer + Brown rice")
            st.write("🍲 Dinner: Fish / Dal + Vegetables")
            st.write("🥜 Snacks: Peanut butter + Banana")

        else:

            st.write("🍳 Breakfast: Fruits + Yogurt")
            st.write("🥗 Lunch: Rice + Dal + Vegetables")
            st.write("🍲 Dinner: Chapati + Paneer")
            st.write("🥜 Snacks: Dry fruits")

st.caption("⚠ Educational tool only. Not medical advice.")








