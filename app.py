import streamlit as st
import pandas as pd
import re
import base64

# Load the image and convert to base64
def load_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

# Replace with your local image path
image_path = "./image/various-vegetables-black-table-with-space-message_1220-616.avif"  # Update this path to your local image
image_base64 = load_image(image_path)

# Inject CSS to set the background image
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url('data:image/jpg;base64,{image_base64}');
        background-size: cover;  /* Cover the entire background */
        background-position: center;  /* Center the image */
        background-repeat: no-repeat;  /* Do not repeat the image */
        color: white;  /* Change text color for better readability */
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Load the Excel file
@st.cache_data
def load_data(file):
    return pd.read_excel(file)

# Load the data
df = load_data("./data/food composition table.xlsx")

# Remove NaN values from Food Name and keep the relevant columns
df = df.dropna(subset=["Food Name"])

# Ensure the required columns are present
required_columns = [
    "Food Code", "Food Name", "Moisture", "Protein", "Ash", "Total Fat",
    "Total", "Insoluble", "Soluble", "Carbohydrate", "Energy"
]
if not all(column in df.columns for column in required_columns):
    st.error("Excel file must contain the required columns.")
    st.stop()

# Streamlit app
st.title("Food Nutrient Calculator")

# Select food name with food code
food_options = df[["Food Code", "Food Name"]].dropna().values
food_selection = st.selectbox(
    "Select Food Item",
    ["Select a food item"] + [f"{code} - **{name}**" for code, name in food_options]
)

# Check if a valid food item is selected
if food_selection != "Select a food item":
    # Extract selected food code and name
    selected_code, selected_name = food_selection.split(" - **")

    # Input quantity with a default value
    quantity = st.number_input("Enter Quantity (in grams)", min_value=1, value=100)  # Default value set to 100 grams

    def extract_value(s):
        match = re.match(r"([0-9]*\.?[0-9]+)", s)
        return float(match.group(1)) if match else None

    # Calculate nutrients
    food_data = df[df["Food Code"] == selected_code.strip()]
    if not food_data.empty:
        # Extracting each nutrient
        nutrients = {
            "Moisture": food_data["Moisture"].values[0],
            "Protein": food_data["Protein"].values[0],
            "Ash": food_data["Ash"].values[0],
            "Total Fat": food_data["Total Fat"].values[0],
            "Total": food_data["Total"].values[0],
            "Insoluble": food_data["Insoluble"].values[0],
            "Soluble": food_data["Soluble"].values[0],
            "Carbohydrate": food_data["Carbohydrate"].values[0],
            "Energy": food_data["Energy"].values[0]
        }

        # Process each nutrient
        for nutrient, value in nutrients.items():
            if isinstance(value, str) and "±" in value:
                nutrients[nutrient] = extract_value(value)

        # Calculate total values based on quantity
        total_nutrients = {nutrient: value * (quantity / 100) for nutrient, value in nutrients.items()}

        # Display results
        st.write(f"For {quantity}g of **{selected_name.strip()}** (Code: {selected_code.strip()}):")
        for nutrient, total in total_nutrients.items():
            st.write(f"{nutrient}: {total:.2f} g" if nutrient != "Energy" else f"{nutrient}: {total:.2f} kcal")
else:
    st.warning("Please select a food item to see the nutrient values.")
