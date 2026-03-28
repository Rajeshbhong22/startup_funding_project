import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import os

def train_model(data_path, model_dir='utils/models/'):
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
        
    df = pd.read_csv(data_path)
    
    # Dropping missing amounts for training
    df = df.dropna(subset=['amount'])
    
    # Feature selection
    # We will use 'vertical', 'city', 'year', 'month'
    features = ['vertical', 'city', 'year', 'month']
    X = df[features].copy()
    y = df['amount']
    
    # Handle categorical variables with Label Encoding for simplicity in streamlit 
    # (One-hot is better but more complex to manage mapping in UI)
    encoders = {}
    for col in ['vertical', 'city']:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        encoders[col] = le
        
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    print(f"R2 Score: {r2_score(y_test, y_pred):.2f}")
    print(f"MAE: {mean_absolute_error(y_test, y_pred):.2f}")
    
    # Save model and encoders
    joblib.dump(model, os.path.join(model_dir, 'funding_model.pkl'))
    joblib.dump(encoders, os.path.join(model_dir, 'encoders.pkl'))
    
    print(f"✅ Model and encoders saved to {model_dir}")

if __name__ == "__main__":
    train_model('data/cleaned_startup_data.csv')
