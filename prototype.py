import streamlit as st
import pandas as pd
import time
from logic import get_mock_inventory, recommend_meals, calculate_impact

st.set_page_config(page_title="Eco-Smart AI Architect", page_icon="🥗", layout="wide")

# Initialize Session States
if "inventory" not in st.session_state:
    with st.status("Training Machine Learning Model...", expanded=True) as status:
        # Now returns accuracy too!
        inv, acc = get_mock_inventory()
        st.session_state.inventory = inv
        st.session_state.accuracy = acc
        time.sleep(1)
        status.update(label=f"Model Trained! Accuracy: {acc:.1%}", state="complete")

if "current_results" not in st.session_state:
    st.session_state.current_results = None

def regenerate():
    if st.session_state.get("last_prompt"):
        st.session_state.current_results = recommend_meals(
            st.session_state.last_prompt, 
            st.session_state.inventory,
            st.session_state.get("excluded_allergens", [])
        )

# UI Layout
st.markdown("# 🥗 Eco-Smart AI Architect")
st.caption("Machine Learning Powered Ingredient Planning | ESADE Assignment #1")

with st.sidebar:
    st.header("🤖 Model Intelligence")
    # Display the Accuracy from the Train-Test Split
    st.metric("Model Test Accuracy", f"{st.session_state.accuracy:.1%}")
    st.info("The model was trained on 80% of your CSV data and tested on 20% to verify safety prediction accuracy.")
    
    st.divider()
    st.header("🛡️ Safety Filters")
    allergens_list = ["Dairy", "Wheat", "Almonds", "Eggs", "Peanuts", "Soy"]
    selected_allergens = st.multiselect("Exclude Allergens:", allergens_list, key="excluded_allergens")

prompt = st.chat_input("Search for an ingredient (e.g., 'Chicken')...")

if prompt:
    st.session_state.last_prompt = prompt
    st.session_state.current_results = recommend_meals(prompt, st.session_state.inventory, selected_allergens)

if st.session_state.current_results is not None:
    st.subheader("Your AI-Curated Cart")
    
    edited_df = st.data_editor(
        st.session_state.current_results[["Food Product", "Main Ingredient", "Allergens", "Final_Price", "Days_to_Expiry", "CO2_Impact"]],
        use_container_width=True,
        hide_index=True
    )

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔄 Regenerate Ideas", use_container_width=True, on_click=regenerate):
            st.toast("Refreshing recommendations...")
    with c2:
        if st.button("🛒 Checkout & Impact", type="primary", use_container_width=True):
            saved, co2, waste = calculate_impact(st.session_state.current_results)
            st.balloons()
            st.markdown(f"### 🌍 Eco-Savings: €{saved:.2f} | CO2 Saved: {co2:.1f}kg")