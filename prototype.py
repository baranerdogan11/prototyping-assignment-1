import streamlit as st
import pandas as pd
import time
from logic import get_mock_inventory, recommend_meals, calculate_impact

# 1. Setup & Custom Styling
st.set_page_config(page_title="Eco-Smart Meal Architect", page_icon="🥗", layout="wide")

# Using a standard markdown header for branding since we're skipping the logo
st.markdown("# 🥗 Eco-Smart Meal Architect")
st.caption("AI-Powered Prototyping for Getir/Glovo/GoPuff | Sustainable Analytics Feature")

# 2. Advanced State Management
if "inventory" not in st.session_state:
    st.session_state.inventory = get_mock_inventory()
if "current_results" not in st.session_state:
    st.session_state.current_results = None
if "last_prompt" not in st.session_state:
    st.session_state.last_prompt = ""

# Callback for Regeneration (The "Fix")
def regenerate():
    if st.session_state.last_prompt:
        st.session_state.current_results = recommend_meals(
            st.session_state.last_prompt, st.session_state.inventory
        )

# 3. Sidebar: Prototyping Mindset (Assignment Requirement)
with st.sidebar:
    st.header("⚙️ System Config")
    with st.expander("Prototyping Goals", expanded=True):
        st.write("- **UX:** Intent-based cart building.")
        st.write("- **Data:** Dynamic price-expiry mapping.")
        st.write("- **Accuracy:** Real-time CO2 tracking.")
    
    st.divider()
    if st.button("🗑️ Clear All Sessions", use_container_width=True):
        st.session_state.current_results = None
        st.rerun()

# 4. User Intent Phase
prompt = st.chat_input("Tell the AI what you're craving (e.g. 'A high-protein lunch')")

if prompt:
    st.session_state.last_prompt = prompt
    with st.status("Architecting your eco-friendly meal...", expanded=False):
        st.session_state.current_results = recommend_meals(prompt, st.session_state.inventory)
        time.sleep(0.8)
    st.toast("Model updated with fresh inventory picks!", icon="🔄")

# 5. Interaction Phase
if st.session_state.current_results is not None:
    st.subheader("Your Intelligent Cart")
    
    # Interactive Editor
    edited_df = st.data_editor(
        st.session_state.current_results[["Item", "Final_Price", "Days_to_Expiry", "CO2_Impact"]],
        column_config={
            "Final_Price": st.column_config.NumberColumn("Price (€)", format="%.2f"),
            "Days_to_Expiry": st.column_config.ProgressColumn("Freshness", min_value=0, max_value=7),
            "CO2_Impact": st.column_config.NumberColumn("CO2 (kg)", format="%.1f")
        },
        use_container_width=True,
        hide_index=True,
        key="main_editor"
    )

    # 6. Action Buttons
    c1, c2 = st.columns([1, 1])
    
    with c1:
        # Regenerate Ideas (Fixed using the callback pattern)
        if st.button("🔄 Try Different Ingredients", use_container_width=True, on_click=regenerate):
            st.toast("Regenerating based on your last request...")

    with c2:
        # Finalize (Primary Action)
        if st.button("🛒 Checkout & View Impact", type="primary", use_container_width=True):
            saved, co2, waste = calculate_impact(edited_df)
            st.balloons()
            
            st.markdown("---")
            st.subheader("🌍 Sustainable Impact Report")
            k1, k2, k3 = st.columns(3)
            k1.metric("Eco-Savings", f"€{saved:.2f}", help="Discount from items near expiry")
            k2.metric("Carbon Footprint", f"{co2:.1f}kg", "-0.3kg", delta_color="inverse")
            k3.metric("Waste Prevented", f"{waste:.1f}kg", help="Weight of food diverted from waste bins")