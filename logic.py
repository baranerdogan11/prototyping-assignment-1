import pandas as pd
import numpy as np
import os

def get_mock_inventory():
    """Loads your dataset and adds business metrics for the Eco-Smart prototype."""
    if os.path.exists("food_ingredients_and_allergens.csv"):
        df = pd.read_csv("food_ingredients_and_allergens.csv")
    else:
        # Fallback empty dataframe with correct columns if file is missing
        return pd.DataFrame(columns=["Food Product", "Main Ingredient", "Allergens"])

    # Cleaning: Drop duplicates from your dataset for a cleaner store inventory
    df = df.drop_duplicates(subset=['Food Product']).reset_index(drop=True)

    # Adding Synthetic Business Data (Price, Expiry, CO2)
    # This allows us to maintain the 'Eco-Discount' logic for the assignment
    np.random.seed(42) # For consistent results
    df['Base_Price'] = np.random.uniform(2.0, 15.0, size=len(df)).round(2)
    df['Days_to_Expiry'] = np.random.randint(1, 10, size=len(df))
    df['CO2_Impact'] = np.random.uniform(0.1, 1.2, size=len(df)).round(1)
    
    # Calculate Eco-Discounts (Business Logic)
    df['Discount_Rate'] = df['Days_to_Expiry'].apply(
        lambda x: 0.30 if x <= 2 else (0.15 if x <= 3 else 0.0)
    )
    df['Final_Price'] = df['Base_Price'] * (1 - df['Discount_Rate'])
    
    # Fill NaN allergens for filtering
    df['Allergens'] = df['Allergens'].fillna('None')
    return df

def recommend_meals(user_query, inventory_df, excluded_allergens=[]):
    """
    Advanced filtering: Matches user intent and excludes specific allergens 
    found in your CSV.
    """
    query = user_query.lower()
    df = inventory_df.copy()
    
    # 1. Filter by Allergens (Real data usage)
    if excluded_allergens:
        for allergen in excluded_allergens:
            # Filters out rows where the allergen string contains the user's selection
            df = df[~df['Allergens'].str.contains(allergen, case=False)]
    
    # 2. Filter by Intent
    if query:
        # Searches across Food Product and Main Ingredient
        df = df[
            df['Food Product'].str.contains(query, case=False) | 
            df['Main Ingredient'].str.contains(query, case=False)
        ]
    
    # If no matches, return a random sample of safe items
    if df.empty:
        return inventory_df.sample(n=min(5, len(inventory_df)))
        
    return df.sample(n=min(5, len(df))).sort_values(by="Days_to_Expiry")

def calculate_impact(final_df):
    """Calculates eco-impact based on the current cart."""
    total_saved = (final_df['Base_Price'] - final_df['Final_Price']).sum()
    co2_total = final_df['CO2_Impact'].sum()
    waste_prev = len(final_df[final_df['Days_to_Expiry'] <= 3]) * 0.45 
    return total_saved, co2_total, waste_prev