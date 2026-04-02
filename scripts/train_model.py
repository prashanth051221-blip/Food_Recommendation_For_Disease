import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

# Sample disease-symptom dataset
data = {
    'fever': [1, 1, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1],
    'cough': [1, 1, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 0],
    'fatigue': [1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1],
    'headache': [0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0],
    'body_pain': [1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1],
    'nausea': [0, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0],
    'sore_throat': [1, 1, 1, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 0, 0],
    'runny_nose': [1, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 0, 0],
    'shortness_of_breath': [0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 0, 1, 1],
    'chest_pain': [0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0],
    'diarrhea': [0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0],
    'vomiting': [0, 0, 1, 0, 1, 0, 1, 1, 0, 0, 0, 1, 0, 1, 0],
    'disease': ['Flu', 'Common Cold', 'Food Poisoning', 'COVID-19', 'Migraine', 
                'COVID-19', 'Flu', 'Food Poisoning', 'Heart Disease', 'Flu',
                'COVID-19', 'Common Cold', 'Common Cold', 'Migraine', 'Heart Disease']
}

df = pd.DataFrame(data)

# Features and target
symptom_columns = [col for col in df.columns if col != 'disease']
X = df[symptom_columns]
y = df['disease']

# Encode labels
le = LabelEncoder()
y_encoded = le.fit_transform(y)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y_encoded)

# Save files
pickle.dump(model, open("model.pkl", "wb"))
pickle.dump(symptom_columns, open("columns.pkl", "wb"))
pickle.dump(le, open("label_encoder.pkl", "wb"))

print("Model trained and saved successfully!")
print(f"Symptoms: {symptom_columns}")
print(f"Diseases: {list(le.classes_)}")
