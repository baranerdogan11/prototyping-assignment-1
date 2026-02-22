import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

def get_mock_inventory():
    filename = "food_ingredients_and_allergens.csv"
    if os.path.exists(filename):
        df = pd.read_csv(filename)
    else:
        return pd.DataFrame(columns=["Food Product", "Main Ingredient", "Allergens"]), 0.0

    # 1. PREPROCESSING FOR ML
    df_ml = df.dropna(subset=['Prediction']).copy()
    # Combine text features for training
    df_ml['Features'] = df_ml[['Main Ingredient', 'Sweetener', 'Fat/Oil', 'Seasoning']].fillna('').agg(' '.join, axis=1)
    
    # 2. TRAIN-TEST SPLIT
    X = df_ml['Features']
    y = df_ml['Prediction']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 3. MODEL PIPELINE
    model = Pipeline([
        ('tfidf', TfidfVectorizer()),
        ('clf', LogisticRegression())
    ])
    model.fit(X_train, y_train)
    
    # 4. EVALUATE ACCURACY
    accuracy = model.score(X_test, y_test)

    # Clean the inventory for the UI
    df = df.drop_duplicates(subset=['Food Product']).reset_index(drop=True)
    np.random.seed(42) 
    df['Base_Price'] = np.random.uniform(2.0, 15.0, size=len(df)).round(2)
    df['Days_to_Expiry'] = np.random.randint(1, 11, size=len(df))
    df['CO2_Impact'] = np.random.uniform(0.1, 1.2, size=len(df)).round(1)
    
    df['Discount_Rate'] = df['Days_to_Expiry'].apply(lambda x: 0.30 if x <= 2 else (0.15 if x <= 4 else 0.0))
    df['Final_Price'] = (df['Base_Price'] * (1 - df['Discount_Rate'])).round(2)
    df['Allergens'] = df['Allergens'].fillna('None')
    
    return df, accuracy

def recommend_meals(user_query, inventory_df, excluded_allergens=[]):
    query = user_query.lower()
    df = inventory_df.copy()
    
    if excluded_allergens:
        for allergen in excluded_allergens:
            df = df[~df['Allergens'].str.contains(allergen, case=False)]
    
    if query:
        df = df[df['Food Product'].str.contains(query, case=False) | df['Main Ingredient'].str.contains(query, case=False)]
    
    if df.empty:
        return inventory_df.sample(n=min(5, len(inventory_df)))
    return df.sample(n=min(5, len(df))).sort_values(by="Days_to_Expiry")

def calculate_impact(final_df):
    total_saved = (final_df['Base_Price'] - final_df['Final_Price']).sum()
    co2_total = final_df['CO2_Impact'].sum()
    waste_prev = len(final_df[final_df['Days_to_Expiry'] <= 3]) * 0.45 
    return total_saved, co2_total, waste_prev