import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

#-----------------------------

#DATABASE SETUP (Persistent Storage)

#-----------------------------

conn = sqlite3.connect("users.db", check_same_thread=False) c = conn.cursor()

c.execute(""" CREATE TABLE IF NOT EXISTS users ( username TEXT PRIMARY KEY, password TEXT, skills TEXT, location TEXT ) """) conn.commit()

#-----------------------------

#JOB DATASET (Extended)

#-----------------------------

data = { "Job Title": [ "Software Engineer", "Data Analyst", "Web Developer", "ML Engineer", "Business Analyst", "Python Developer", "Frontend Developer", "Backend Developer", "AI Engineer", "Cloud Engineer" ], "Skills": [ "python java algorithms", "excel sql python data analysis", "html css javascript react", "python machine learning deep learning", "communication analytics business", "python django flask api", "html css react ui ux", "nodejs databases api backend", "ai deep learning nlp python", "aws cloud devops docker kubernetes" ], "Location": [ "Hyderabad", "Bangalore", "Chennai", "Hyderabad", "Mumbai", "Pune", "Bangalore", "Delhi", "Hyderabad", "Bangalore" ], "Interview": [ "Coding + HR", "Aptitude + SQL", "Portfolio + HR", "ML Case Study", "GD + HR", "Coding + System Design", "UI Task + HR", "Backend Task + HR", "AI Project Discussion", "Cloud Scenario + HR" ] }

df = pd.DataFrame(data)

#-----------------------------

#HELPER FUNCTIONS

#-----------------------------

def hash_password(password): return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password, skills, location): try: c.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (username, hash_password(password), skills, location)) conn.commit() return True except: return False

def login_user(username, password): c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hash_password(password))) return c.fetchone()

def update_user(username, skills, location): c.execute("UPDATE users SET skills=?, location=? WHERE username=?", (skills, location, username)) conn.commit()

#-----------------------------

#ADVANCED RECOMMENDATION ENGINE

#-----------------------------

def recommend_jobs(user_skills, location): df["combined"] = df["Skills"] + " " + df["Job Title"]

vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
tfidf_matrix = vectorizer.fit_transform(df["combined"])

user_vec = vectorizer.transform([user_skills])

similarity = cosine_similarity(user_vec, tfidf_matrix).flatten()
df["Score"] = similarity

# Location priority scoring
df["Location Match"] = df["Location"].apply(
    lambda x: 1 if x.lower() == location.lower() else 0
)

df["Final Score"] = df["Score"] + (0.3 * df["Location Match"])

return df.sort_values(by="Final Score", ascending=False)

#-----------------------------

#STREAMLIT UI

#-----------------------------

st.set_page_config(page_title="Advanced Job Portal", layout="wide")

st.title("🚀 AI Job Recommendation Portal")

menu = ["Login", "Register"] choice = st.sidebar.selectbox("Menu", menu)

#-----------------------------

#REGISTER

#-----------------------------

if choice == "Register": st.subheader("Create Account")

username = st.text_input("Username")
password = st.text_input("Password", type="password")
skills = st.text_area("Skills (optional)")
location = st.text_input("Preferred Location")

if st.button("Register"):
    if register_user(username, password, skills, location):
        st.success("Account created successfully")
    else:
        st.error("Username already exists")

#-----------------------------

#LOGIN

#-----------------------------

if choice == "Login": st.subheader("Login")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):
    result = login_user(username, password)

    if result:
        st.session_state.logged_in = True
        st.session_state.username = username
        st.success("Login successful")
    else:
        st.error("Invalid credentials")

#-----------------------------

#DASHBOARD

#-----------------------------

if "logged_in" in st.session_state and st.session_state.logged_in: st.subheader(f"Welcome {st.session_state.username}")

c.execute("SELECT skills, location FROM users WHERE username=?",
          (st.session_state.username,))
user_data = c.fetchone()

skills = user_data[0] if user_data else ""
location = user_data[1] if user_data else ""

st.write("### Update Your Profile")
new_skills = st.text_area("Skills", value=skills)
new_location = st.text_input("Location", value=location)

if st.button("Update Profile"):
    update_user(st.session_state.username, new_skills, new_location)
    st.success("Profile updated")

if st.button("Get Recommendations"):
    if new_skills.strip() == "":
        st.warning("Please enter your skills")
    else:
        results = recommend_jobs(new_skills, new_location)

        st.write("## 🎯 Top Job Matches")

        for _, row in results.head(7).iterrows():
            st.markdown(f"""
            ### {row['Job Title']}
            📍 Location: {row['Location']}  
            🛠 Skills: {row['Skills']}  
            🎯 Interview: {row['Interview']}  
            ⭐ Score: {round(row['Final Score'], 2)}
            """)

if st.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.experimental_rerun()

#-----------------------------

#RUN

#-----------------------------

pip install streamlit pandas scikit-learn

streamlit run app.py
