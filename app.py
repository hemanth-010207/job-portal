import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------------- DATABASE ----------------

conn = sqlite3.connect("users.db",check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users(
username TEXT PRIMARY KEY,
password TEXT,
skills TEXT,
location TEXT
)
""")

conn.commit()

# ---------------- JOB DATA ----------------

data={

"Job Title":[
"Software Engineer",
"Data Analyst",
"Web Developer",
"ML Engineer",
"Business Analyst",
"Python Developer",
"Frontend Developer",
"Backend Developer"
],

"Skills":[
"python java algorithms",
"excel sql python data analysis",
"html css javascript react",
"python machine learning",
"communication analytics business",
"python django flask",
"html css react ui",
"nodejs api backend database"
],

"Location":[
"Hyderabad",
"Bangalore",
"Chennai",
"Hyderabad",
"Mumbai",
"Pune",
"Bangalore",
"Delhi"
],

"Interview":[
"Coding + HR",
"Aptitude + SQL",
"Portfolio + HR",
"ML Case Study",
"GD + HR",
"Coding Round",
"UI Task",
"Backend Task"
]

}

df=pd.DataFrame(data)

# ---------------- FUNCTIONS ----------------

def hash_password(password):

    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username,password,skills,location):

    try:

        c.execute(
        "INSERT INTO users VALUES(?,?,?,?)",
        (username,hash_password(password),skills,location)
        )

        conn.commit()

        return True

    except:

        return False

def login_user(username,password):

    c.execute(
    "SELECT * FROM users WHERE username=? AND password=?",
    (username,hash_password(password))
    )

    return c.fetchone()

def update_user(username,skills,location):

    c.execute(
    "UPDATE users SET skills=?,location=? WHERE username=?",
    (skills,location,username)
    )

    conn.commit()

# ---------------- RECOMMEND ENGINE ----------------

def recommend_jobs(user_skills,location):

    df["combined"]=df["Skills"]+" "+df["Job Title"]

    vectorizer=TfidfVectorizer(
    stop_words="english",
    ngram_range=(1,2)
    )

    tfidf_matrix=vectorizer.fit_transform(df["combined"])

    user_vec=vectorizer.transform([user_skills])

    similarity=cosine_similarity(
    user_vec,
    tfidf_matrix
    ).flatten()

    df["Score"]=similarity

    df["Location Match"]=df["Location"].apply(
    lambda x:1 if x.lower()==location.lower() else 0
    )

    df["Final Score"]=df["Score"]+(0.3*df["Location Match"])

    return df.sort_values(
    by="Final Score",
    ascending=False
    )

# ---------------- STREAMLIT UI ----------------

st.set_page_config(
page_title="Job Portal",
layout="wide"
)

# CSS Styling
st.markdown("""

<style>

.main{
background:#f4f6fb;
}

.title{
font-size:32px;
font-weight:600;
color:#2c3e50;
}

.job-card{

background:white;

padding:20px;

border-radius:12px;

margin-bottom:20px;

box-shadow:0 5px 15px rgba(0,0,0,0.08);

border-left:6px solid #2e86de;

}

.skill{

background:#e8f0fe;

padding:6px 12px;

border-radius:6px;

margin:4px;

display:inline-block;

font-size:13px;

}

.subtitle{

color:gray;

}

</style>

""",unsafe_allow_html=True)

st.markdown(
"<div class='title'>AI Job Recommendation System</div>",
unsafe_allow_html=True
)

st.image(
"https://images.unsplash.com/photo-1492724441997-5dc865305da7",
use_container_width=True
)

menu=["Login","Register"]

choice=st.sidebar.selectbox("Menu",menu)

# ---------------- REGISTER ----------------

if choice=="Register":

    st.subheader("Create Account")

    col1,col2=st.columns(2)

    with col1:

        username=st.text_input("Username")

        password=st.text_input(
        "Password",
        type="password"
        )

    with col2:

        skills=st.text_area("Skills")

        location=st.text_input("Location")

    if st.button("Register"):

        if register_user(
        username,
        password,
        skills,
        location
        ):

            st.success("Account created")

        else:

            st.error("Username already exists")

# ---------------- LOGIN ----------------

if choice=="Login":

    st.subheader("Login")

    username=st.text_input("Username")

    password=st.text_input(
    "Password",
    type="password"
    )

    if st.button("Login"):

        result=login_user(
        username,
        password
        )

        if result:

            st.session_state.logged_in=True

            st.session_state.username=username

            st.success("Login successful")

        else:

            st.error("Invalid credentials")

# ---------------- DASHBOARD ----------------

if "logged_in" in st.session_state and st.session_state.logged_in:

    st.subheader("Dashboard")

    c.execute(
    "SELECT skills,location FROM users WHERE username=?",
    (st.session_state.username,)
    )

    user_data=c.fetchone()

    skills=user_data[0] if user_data else ""

    location=user_data[1] if user_data else ""

    st.write("Update Profile")

    new_skills=st.text_area(
    "Skills",
    value=skills
    )

    new_location=st.text_input(
    "Location",
    value=location
    )

    col1,col2,col3=st.columns(3)

    with col1:

        if st.button("Update Profile"):

            update_user(
            st.session_state.username,
            new_skills,
            new_location
            )

            st.success("Profile updated")

    with col2:

        recommend=st.button("Get Recommendations")

    with col3:

        if st.button("Logout"):

            st.session_state.logged_in=False

            st.experimental_rerun()

    if recommend:

        results=recommend_jobs(
        new_skills,
        new_location
        )

        st.write("Top Job Matches")

        for _,row in results.head(6).iterrows():

            st.markdown(f"""

<div class="job-card">

<h3>{row['Job Title']}</h3>

<p class="subtitle">
Location: {row['Location']}
</p>

<p>

<b>Skills:</b>

<span class="skill">
{row['Skills']}
</span>

</p>

<p>

<b>Interview:</b>

{row['Interview']}

</p>

<p>

<b>Match Score:</b>

{round(row['Final Score'],2)}

</p>

</div>

""",unsafe_allow_html=True)        "python machine learning",
        "communication analytics business",
        "python django flask",
        "html css react ui",
        "nodejs api backend database"
    ],
    "Location": [
        "Hyderabad", "Bangalore", "Chennai", "Hyderabad",
        "Mumbai", "Pune", "Bangalore", "Delhi"
    ],
    "Interview": [
        "Coding + HR",
        "Aptitude + SQL",
        "Portfolio + HR",
        "ML Case Study",
        "GD + HR",
        "Coding Round",
        "UI Task",
        "Backend Task"
    ]
}

df = pd.DataFrame(data)

# -----------------------------
# FUNCTIONS
# -----------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password, skills, location):
    try:
        c.execute("INSERT INTO users VALUES (?, ?, ?, ?)",
                  (username, hash_password(password), skills, location))
        conn.commit()
        return True
    except:
        return False

def login_user(username, password):
    c.execute("SELECT * FROM users WHERE username=? AND password=?",
              (username, hash_password(password)))
    return c.fetchone()

def update_user(username, skills, location):
    c.execute("UPDATE users SET skills=?, location=? WHERE username=?",
              (skills, location, username))
    conn.commit()

def recommend_jobs(user_skills, location):
    df["combined"] = df["Skills"] + " " + df["Job Title"]

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(df["combined"])

    user_vec = vectorizer.transform([user_skills])
    similarity = cosine_similarity(user_vec, tfidf_matrix).flatten()

    df["Score"] = similarity

    df["Location Match"] = df["Location"].apply(
        lambda x: 1 if x.lower() == location.lower() else 0
    )

    df["Final Score"] = df["Score"] + (0.3 * df["Location Match"])

    return df.sort_values(by="Final Score", ascending=False)

# -----------------------------
# STREAMLIT UI
# -----------------------------
st.set_page_config(page_title="Job Portal")

st.title("💼 Job Recommendation Portal")

menu = ["Login", "Register"]
choice = st.sidebar.selectbox("Menu", menu)

# -----------------------------
# REGISTER
# -----------------------------
if choice == "Register":
    st.subheader("Create Account")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    skills = st.text_area("Skills (optional)")
    location = st.text_input("Location")

    if st.button("Register"):
        if register_user(username, password, skills, location):
            st.success("Account created successfully")
        else:
            st.error("Username already exists")

# -----------------------------
# LOGIN
# -----------------------------
if choice == "Login":
    st.subheader("Login")

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

# -----------------------------
# DASHBOARD
# -----------------------------
if "logged_in" in st.session_state and st.session_state.logged_in:

    st.subheader(f"Welcome {st.session_state.username}")

    c.execute("SELECT skills, location FROM users WHERE username=?",
              (st.session_state.username,))
    user_data = c.fetchone()

    skills = user_data[0] if user_data else ""
    location = user_data[1] if user_data else ""

    st.write("### Update Profile")

    new_skills = st.text_area("Skills", value=skills)
    new_location = st.text_input("Location", value=location)

    if st.button("Update Profile"):
        update_user(st.session_state.username, new_skills, new_location)
        st.success("Profile updated")

    if st.button("Get Recommendations"):
        if new_skills.strip() == "":
            st.warning("Enter your skills")
        else:
            results = recommend_jobs(new_skills, new_location)

            st.write("## 🎯 Recommended Jobs")

            for _, row in results.head(5).iterrows():
                st.markdown(f"""
                ### {row['Job Title']}
                📍 Location: {row['Location']}  
                🛠 Skills: {row['Skills']}  
                🎯 Interview: {row['Interview']}  
                ⭐ Score: {round(row['Final Score'], 2)}
                """)

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()    
        return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password, skills, location): 
    
    try:
        c.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (username, hash_password(password), skills, location)) 
        conn.commit() 
        return True
    except:
            return False

def login_user(username, password):
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hash_password(password))) 
    return c.fetchone()

def update_user(username, skills, location):
    c.execute("UPDATE users SET skills=?, location=? WHERE username=?", (skills, location, username)) 
    conn.commit()

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

menu = ["Login", "Register"] 
choice = st.sidebar.selectbox("Menu", menu)

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
