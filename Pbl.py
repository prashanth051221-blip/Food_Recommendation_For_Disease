import streamlit as st
import pandas as pd
from rapidfuzz import process, fuzz

st.set_page_config(page_title="Food Recommendation for Disease", layout="centered")

st.title("🍎 Food Recommendation for Disease")
st.markdown("An educational tool that recommends foods to eat and avoid for common diseases. *Not medical advice.*")

# ✅ Embedded dataset
data = [
    {
        "Disease": "Type 2 Diabetes",
        "Foods_to_Eat": "Whole grains (brown rice, oats); Non-starchy vegetables (broccoli, spinach); Lean proteins (chicken, tofu, lentils); Nuts; Seeds; Low-fat dairy",
        "Foods_to_Avoid": "Sugary drinks; White bread; Pastries; Sweets; Fried foods; Full-fat dairy",
        "Nutritional_Note": "Aim for low-glycemic foods with high fiber to stabilize blood sugar."
    },
    {
        "Disease": "Hypertension",
        "Foods_to_Eat": "Fruits; Vegetables; Whole grains; Low-fat dairy; Potassium-rich foods",
        "Foods_to_Avoid": "High-salt foods; Pickles; Processed meats; Chips; Fast food",
        "Nutritional_Note": "Follow the DASH diet; reducing sodium and increasing potassium helps lower blood pressure."
    },
    {
        "Disease": "Heart Disease / High Cholesterol",
        "Foods_to_Eat": "Oats; Barley; Fatty fish (salmon, tuna); Legumes; Olive oil; Fruits; Vegetables",
        "Foods_to_Avoid": "Butter; Cheese; Fried foods; Red meats; Processed snacks",
        "Nutritional_Note": "Focus on soluble fiber and unsaturated fats to improve cholesterol levels."
    },
    {
        "Disease": "Chronic Kidney Disease (CKD)",
        "Foods_to_Eat": "Low-sodium meals; Lean proteins in moderation; Apples; Cabbage; Garlic; Olive oil",
        "Foods_to_Avoid": "High-sodium foods; Processed snacks; Dark sodas; High-phosphorus foods",
        "Nutritional_Note": "Control intake of sodium, potassium, and phosphorus to protect kidney function."
    },
    {
        "Disease": "Fatty Liver (NAFLD)",
        "Foods_to_Eat": "Vegetables; Fruits; Whole grains; Olive oil; Fatty fish; Green tea",
        "Foods_to_Avoid": "Sugar-rich drinks; Refined carbs; Processed meats; Alcohol",
        "Nutritional_Note": "Weight loss and high-antioxidant foods reduce fat buildup in the liver."
    }
]

# Create DataFrame
df = pd.DataFrame(data)
df["Disease_lower"] = df["Disease"].str.lower()
diseases = df["Disease"].tolist()

# Sidebar controls
with st.sidebar:
    st.header("Controls")
    use_fuzzy = st.checkbox("Enable fuzzy search (tolerate typos)", value=True)
    pref_veg = st.checkbox("Vegetarian-friendly results", value=False)
    pref_lowsugar = st.checkbox("Low-sugar preference (hide sugary foods)", value=False)
    pref_lowsodium = st.checkbox("Low-sodium preference (hide high-salt foods)", value=False)

st.write("*Search for a disease:*")
col1, col2 = st.columns([3, 1])
with col1:
    query = st.text_input("Type disease name (or pick from dropdown)", value="")
with col2:
    selected = st.selectbox("Or choose", ["-- none --"] + diseases)

def apply_preferences(text, veg=False, lowsugar=False, lowsodium=False):
    txt = str(text)
    lowered = txt.lower()
    if veg:
        blacklist = ["chicken","fish","meat","egg","eggs","salmon","tuna","beef","pork","shellfish"]
        for b in blacklist:
            lowered = lowered.replace(b, "[removed]")
    if lowsugar:
        sugar_words = ["sugar","sugary","sweets","honey","jaggery","syrup"]
        for s in sugar_words:
            lowered = lowered.replace(s, "[removed]")
    if lowsodium:
        salt_words = ["salt","salty","pickles","processed","chips"]
        for s in salt_words:
            lowered = lowered.replace(s, "[removed]")
    return lowered.replace("[removed]", "(removed due to preference)")

def find_matches(query, df, use_fuzzy=True, limit=5):
    q = query.strip().lower()
    if not q:
        return pd.DataFrame()
    if use_fuzzy:
        choices = df["Disease"].tolist()
        results = process.extract(q, choices, scorer=fuzz.token_sort_ratio, limit=limit)
        matches = [r[0] for r in results if r[1] > 50]
        return df[df["Disease"].isin(matches)]
    else:
        return df[df["Disease_lower"].str.contains(q)]

results_df = pd.DataFrame()
if selected != "-- none --":
    results_df = df[df["Disease"] == selected]
elif query.strip():
    results_df = find_matches(query, df, use_fuzzy=use_fuzzy, limit=10)

if results_df.empty:
    st.info("No disease selected. Choose from dropdown or type a name to search.")
else:
    for _, row in results_df.iterrows():
        st.header(row["Disease"])
        eat = apply_preferences(row["Foods_to_Eat"], veg=pref_veg, lowsugar=pref_lowsugar, lowsodium=pref_lowsodium)
        avoid = apply_preferences(row["Foods_to_Avoid"], veg=pref_veg, lowsugar=pref_lowsugar, lowsodium=pref_lowsodium)
        note = row.get("Nutritional_Note", "")
        st.subheader("Foods to Eat ✅")
        for item in str(eat).split(";"):
            item = item.strip()
            if item:
                st.markdown(f"- {item}")
        st.subheader("Foods to Avoid ⛔")
        for item in str(avoid).split(";"):
            item = item.strip()
            if item:
                st.markdown(f"- {item}")
        if note:
            st.subheader("Nutritional Note")
            st.write(note)
        st.markdown("---")

with st.expander("Show full dataset"):
    st.dataframe(df.drop(columns=["Disease_lower"]))

st.caption("Built for educational purposes. Not medical advice.")





