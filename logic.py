import pandas as pd
import numpy as np
import os

def get_mock_inventory():
    """Loads your specific CSV and adds business metrics."""
    filename = "food_ingredients_and_allergens.csv"
    
    if os.path.exists(filename):
        df = pd.read_csv(filename) #
    else:
        return pd.DataFrame(columns=["Food Product", "Main Ingredient", "Allergens"])

    # Cleaning: Standardizing store inventory
    df = df.drop_duplicates(subset=['Food Product']).reset_index(drop=True)

    # Synthetic Business Data for Assignment requirements
    np.random.seed(42) 
    df['Base_Price'] = np.random.uniform(2.0, 15.0, size=len(df)).round(2)
    df['Days_to_Expiry'] = np.random.randint(1, 10, size=len(df))
    df['CO2_Impact'] = np.random.uniform(0.1, 1.2, size=len(df)).round(1)
    
    # Sustainability logic: proximity to expiration equals higher discount
    df['Discount_Rate'] = df['Days_to_Expiry'].apply(
        lambda x: 0.30 if x <= 2 else (0.15 if x <= 3 else 0.0)
    )
    df['Final_Price'] = (df['Base_Price'] * (1 - df['Discount_Rate'])).round(2)
    
    df['Allergens'] = df['Allergens'].fillna('None')
    return df

def recommend_meals(user_query, inventory_df, excluded_allergens=[]):
    """Filters data based on user intent and allergen safety."""
    query = user_query.lower()
    df = inventory_df.copy()
    
    # 1. Allergen filtering using CSV data
    if excluded_allergens:
        for allergen in excluded_allergens:
            df = df[~df['Allergens'].str.contains(allergen, case=False)]
    
    # 2. Intent matching across CSV headers
    if query:
        df = df[
            df['Food Product'].str.contains(query, case=False) | 
            df['Main Ingredient'].str.contains(query, case=False)
        ]
    
    if df.empty:
        return inventory_df.sample(n=min(5, len(inventory_df)))
        
    return df.sample(n=min(5, len(df))).sort_values(by="Days_to_Expiry")

def calculate_impact(final_df):
    """Calculates the environmental impact metrics for the accuracy aspect."""
    total_saved = (final_df['Base_Price'] - final_df['Final_Price']).sum()
    co2_total = final_df['CO2_Impact'].sum()
    waste_prev = len(final_df[final_df['Days_to_Expiry'] <= 3]) * 0.45 
    return total_saved, co2_total, waste_prev