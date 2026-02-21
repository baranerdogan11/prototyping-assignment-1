import pandas as pd

def get_mock_inventory():
    """Diverse inventory for a high-end grocery delivery prototype."""
    data = {
        "Item": [
            "Organic Bananas", "Chicken Breast", "Greek Yogurt", "Sourdough Bread", 
            "Almond Milk", "Avocado", "Spinach Pack", "Red Wine (Rioja)", 
            "Pasta (Fusilli)", "Eggs (6pk)", "Blueberries", "Hummus",
            "Oat Biscuits", "Sparkling Water", "Gorgonzola", "Beyond Burger",
            "Quinoa Pack", "Cherry Tomatoes", "Oat Milk", "Dark Chocolate"
        ],
        "Base_Price": [1.2, 7.5, 2.3, 3.1, 2.1, 1.8, 1.5, 12.0, 1.1, 2.4, 3.5, 2.0, 1.9, 0.9, 4.2, 6.0, 3.8, 2.5, 2.2, 2.8],
        "Days_to_Expiry": [2, 6, 4, 1, 12, 3, 2, 300, 180, 5, 2, 7, 60, 200, 3, 4, 150, 3, 10, 45],
        "Category": ["Produce", "Meat", "Dairy", "Bakery", "Dairy", "Produce", "Produce", "Alcohol", "Pantry", "Dairy", "Produce", "Prepared", "Snacks", "Beverage", "Dairy", "Meat", "Pantry", "Produce", "Dairy", "Snacks"],
        "CO2_Impact": [0.1, 1.5, 0.4, 0.3, 0.2, 0.2, 0.1, 0.8, 0.2, 0.6, 0.2, 0.3, 0.2, 0.1, 0.7, 0.5, 0.2, 0.1, 0.2, 0.3]
    }
    df = pd.DataFrame(data)
    df['Discount_Rate'] = df['Days_to_Expiry'].apply(lambda x: 0.30 if x <= 2 else (0.15 if x <= 3 else 0.0))
    df['Final_Price'] = df['Base_Price'] * (1 - df['Discount_Rate'])
    return df

def recommend_meals(user_query, inventory_df):
    """Semantic-lite filtering with randomization for variety."""
    query = user_query.lower()
    if any(word in query for word in ["breakfast", "morning", "healthy"]):
        pool = inventory_df[inventory_df['Category'].isin(['Dairy', 'Produce', 'Bakery'])]
    elif any(word in query for word in ["dinner", "protein", "heavy"]):
        pool = inventory_df[inventory_df['Category'].isin(['Meat', 'Produce', 'Pantry', 'Dairy'])]
    else:
        pool = inventory_df
    
    # Always return a random sample of 5 to ensure 'Regenerate' feels fresh
    return pool.sample(n=min(5, len(pool))).sort_values(by="Days_to_Expiry")

def calculate_impact(final_df):
    """Calculation logic using columns guaranteed to be in the editor."""
    total_price = final_df['Final_Price'].sum()
    savings_est = total_price * 0.25 # Modelled eco-savings
    co2_total = final_df['CO2_Impact'].sum()
    waste_prev = len(final_df[final_df['Days_to_Expiry'] <= 3]) * 0.4 
    return savings_est, co2_total, waste_prev 