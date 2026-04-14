import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
import joblib
import os

# Set random seed for reproducibility
np.random.seed(42)

# Generate synthetic dataset for training
num_samples = 1500

# 1. Age: 5 to 80
ages = np.random.randint(5, 81, num_samples)

# 2. Gender: 0=Male, 1=Female, 2=Other
genders = np.random.choice([0, 1, 2], num_samples, p=[0.48, 0.48, 0.04])

# 3. BMI: 15.0 to 40.0
bmis = np.round(np.random.uniform(15.0, 40.0, num_samples), 1)

# 4. Smoking History: 0=No, 1=Yes (probability correlated with age)
smoking = np.where(ages > 16, np.random.choice([0, 1], num_samples, p=[0.8, 0.2]), 0)

# 5. Family History of Asthma: 0=No, 1=Yes
family_history = np.random.choice([0, 1], num_samples, p=[0.7, 0.3])

# 6. Frequent Wheezing: 0=No, 1=Yes
wheezing = np.random.choice([0, 1], num_samples, p=[0.8, 0.2])

# 7. Shortness of Breath: 0=No, 1=Yes
shortness_of_breath = np.random.choice([0, 1], num_samples, p=[0.85, 0.15])

# Construct Target: Risk Level (Low, Medium, High)
# Based on logical simulated clinical rules
risks = []
for i in range(num_samples):
    w = wheezing[i]
    sob = shortness_of_breath[i]
    sm = smoking[i]
    fh = family_history[i]
    bmi = bmis[i]
    
    if w == 1 and sob == 1 and (sm == 1 or fh == 1):
        risks.append("High")
    elif (w == 1 or sob == 1):
        if bmi > 25 or sm == 1 or fh == 1:
            risks.append("High")
        else:
            risks.append("Medium")
    elif fh == 1 and (bmi > 30 or sm == 1):
        risks.append("Medium")
    else:
        # Add some slight random noise for realistic ML behavior
        if np.random.random() > 0.95:
            risks.append(np.random.choice(["Medium", "High"]))
        else:
            risks.append("Low")

df = pd.DataFrame({
    'age': ages,
    'gender': genders,
    'bmi': bmis,
    'smoking': smoking,
    'family_history': family_history,
    'wheezing': wheezing,
    'shortness_of_breath': shortness_of_breath,
    'risk': risks
})

# Separate features & targets
X = df.drop(columns=['risk'])
y = df['risk']

# Initialize & Train Decision Tree Classifier
# Max depth restricted to prevent overfitting on synthetic data and for generalization
clf = DecisionTreeClassifier(random_state=42, max_depth=5, min_samples_split=10)
clf.fit(X, y)

# Ensure the parent directory exists
os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'api'), exist_ok=True)
save_path = os.path.join(os.path.dirname(__file__), '..', 'api', 'model.pkl')

joblib.dump(clf, save_path)
print(f"Model trained with {len(X)} samples. Saved to {save_path}")
print("Classes:", clf.classes_)
