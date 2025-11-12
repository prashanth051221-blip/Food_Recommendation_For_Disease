import streamlit as st
import pandas as pd
from pathlib import Path
from rapidfuzz import process, fuzz

st.set_page_config(page_title="Food Recommendation for Disease", layout="centered")

st.title("🍎 Food Recommendation for Disease")
st.markdown("An educational tool that recommends foods to eat and avoid for common diseases. *Not medical advice.*")

# ✅ Your dataset path
DATA_PATH = Path(r"C:\Users\prash\Downloads\food_dataset_updated.csv")

@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    df["Disease_lower"] = df["Disease"].str.lower()
    return df

# Try to load the dataset from the provided path
try:
    df = load_data(DATA_PATH)
except FileNotFoundError:
    st.error(f"❌ Could not find dataset file at: {DATA_PATH}")
    st.stop()

diseases = df["Disease"].tolist()

with st.sidebar:
    st.header("Controls")
    use_fuzzy = st.checkbox("Enable fuzzy search (tolerate typos)", value=True)
    pref_veg = st.checkbox("Vegetarian-friendly results", value=False)
    pref_lowsugar = st.checkbox("Low-sugar preference (hide sugary foods)", value=False)
    pref_lowsodium = st.checkbox("Low-sodium preference (hide high-salt foods)", value=False)
    st.markdown("---")
    st.markdown("*Data management*")
    uploaded = st.file_uploader("Upload CSV to replace dataset", type=["csv"])
    if uploaded is not None:
        try:
            newdf = pd.read_csv(uploaded)
            st.session_state["uploaded_df"] = newdf
            st.success("CSV uploaded — use 'Save dataset' below to download the updated CSV.")
        except Exception as e:
            st.error(f"Failed to read CSV: {e}")
    if st.button("Save dataset (download updated CSV)"):
        outcsv = df.drop(columns=["Disease_lower"]).to_csv(index=False)
        st.download_button("Download CSV", data=outcsv, file_name="food_dataset_updated.csv", mime="text/csv")

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



