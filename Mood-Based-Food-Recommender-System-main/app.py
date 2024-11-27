import streamlit as st
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk

# Ensure necessary NLTK data is downloaded
nltk.download('stopwords')
nltk.download('wordnet')

# Initialize stopwords
stop = set(stopwords.words('english'))
stop.update(['.', ',', '"', "'", '?', '!', ':', ';', '(', ')', '[', ']', '{', '}'])

# Load datasets
food_data = pd.read_csv(r'Mood-Based-Food-Recommender-System/food_choices.csv')
res_data = pd.read_csv(r'Mood-Based-Food-Recommender-System/zomato.csv', encoding='latin-1')
res_data = res_data.loc[(res_data['Country Code'] == 1) & (res_data['City'] == 'New Delhi')]
res_data = res_data.loc[res_data['Longitude'] != 0]
res_data = res_data.loc[res_data['Latitude'] != 0]
res_data = res_data.loc[res_data['Latitude'] < 29]  # Clearing out invalid outliers
res_data = res_data.loc[res_data['Rating text'] != 'Not rated']
res_data['Cuisines'] = res_data['Cuisines'].astype(str)

# Functions
def search_comfort(mood):
    lemmatizer = WordNetLemmatizer()
    foodcount = {}
    for i in range(len(food_data)):
        reasons = [
            temps.strip().replace('.', '').replace(',', '').lower()
            for temps in str(food_data["comfort_food_reasons"][i]).split(' ')
            if temps.strip() not in stop
        ]
        if mood in reasons:
            food_items = [
                lemmatizer.lemmatize(temps.strip().replace('.', '').replace(',', '').lower())
                for temps in str(food_data["comfort_food"][i]).split(',')
                if temps.strip() not in stop
            ]
            for item in food_items:
                foodcount[item] = foodcount.get(item, 0) + 1
    sorted_food = sorted(foodcount, key=foodcount.get, reverse=True)
    return sorted_food

def find_my_comfort_food(mood):
    topn = search_comfort(mood)
    return topn[:3]

# Streamlit App
st.set_page_config(page_title="Mood-Based Food Recommender", page_icon="🍕", layout="wide")

# Add CSS for custom styling
st.markdown(
    """
    <style>
    /* General page styling */
    body {
        background-color: #f0f4f7;
        font-family: 'Arial', sans-serif;
        color: #333;
    }
    .css-18e3th9 {
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 15px;
        padding: 20px;
    }
    .css-1v3v5v6 {
        font-size: 18px;
    }
    /* Styling for headings */
    .stMarkdown h1 {
        color: #4B79A1;
        font-size: 3em;
        text-align: center;
        margin-bottom: 0.5em;
        text-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2);
    }
    .stMarkdown h2 {
        color: #333;
        font-size: 1.5em;
        margin-top: 1.5em;
    }
    /* Button styles */
    .stButton>button {
        background-color: #4b79a1;
        color: white;
        font-size: 18px;
        padding: 10px 20px;
        border-radius: 8px;
        border: none;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stButton>button:hover {
        background-color: #3e6d93;
    }
    /* Radio button style */
    .stRadio>div>label>div {
        font-size: 20px;
        padding: 5px;
        margin-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Title and description
st.title("🍽️ Mood-Based Food Recommender 🍕")
st.write(
    "Welcome to the **Mood-Based Food Recommender**! Select your mood, and we'll suggest comfort foods and the best restaurants in New Delhi for you to enjoy. 🌟"
)

# Mapping moods with emojis
emoji_mood_mapping = {
    "😊 Happy": "happy",
    "😔 Sad": "sad",
    "😠 Angry": "angry",
    "😴 Tired": "tired",
    "🤩 Excited": "excited",
    "🤢 Disgusted": "disgusted"
}

# Check for available moods
available_moods = []
for emoji, mood in emoji_mood_mapping.items():
    if search_comfort(mood):
        available_moods.append(emoji)

# Mood selection
if available_moods:
    mood = st.radio(
        "How are you feeling today? Select an emoji that matches your mood:",
        available_moods,
        index=0,
        key="mood_radio"
    )

    # Convert emoji-based mood to keyword for processing
    mood_text = emoji_mood_mapping.get(mood)

    # Get the food recommendations based on mood
    result = find_my_comfort_food(mood_text)

    # Display results
    if result and len(result) >= 3:
        st.subheader(f"🍴 Comfort Food Recommendations for Your Mood: {mood}")
        st.markdown(f"Try **{result[0]}**, **{result[1]}**, or **{result[2]}**!")

        # Food to cuisine mapping
        food_to_cuisine_map = {
            "pizza": "pizza",
            "ice cream": "ice cream",
            "chicken wings": "mughlai",
            "chinese": "chinese",
            "chip": "bakery",
            "chocolate": "bakery",
            "candy": "bakery",
            "mcdonalds": "burger",
            "burger": "burger",
            "cooky": "bakery",
            "mac and cheese": "american",
            "pasta": "italian",
            "soup": "chinese",
            "dark chocolate": "bakery",
            "terra chips": "bakery",
            "reese's cups(dark chocolate)": "bakery",
        }

        # Find restaurants based on recommendations
        restaurants_list = []
        for item in result:
            if item in food_to_cuisine_map:
                cuisine = food_to_cuisine_map[item]
                restaurants = res_data[res_data.Cuisines.str.contains(cuisine, case=False)].sort_values(by='Aggregate rating', ascending=False).head(3)
                restaurants_list.extend(restaurants.to_dict('records'))

        # Display restaurants
        if restaurants_list:
            st.subheader("🍽️ Top Restaurant Recommendations:")
            for idx, restaurant in enumerate(restaurants_list):
                st.markdown(f"### **Restaurant {idx + 1}: {restaurant['Restaurant Name']}**")
                st.write(f"**Cuisine:** {restaurant['Cuisines']}")
                st.write(f"**Rating:** {restaurant['Aggregate rating']}")
                st.write(f"**Address:** {restaurant['Address']}")
                st.write("---")
    else:
        st.error("Sorry, not enough data for the selected mood. Try another!")
else:
    st.error("No moods are available with sufficient data.")
