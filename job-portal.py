import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------- FOLDERS ----------

os.makedirs("profile_images",exist_ok=True)
os.makedirs("resumes",exist_ok=True)
os.makedirs("certificates",exist_ok=True)

# ---------- DATABASE ----------

conn=sqlite3.connect("users.db",check_same_thread=False)
c=conn.cursor()

c.execute("""

CREATE TABLE IF NOT EXISTS users(

username TEXT PRIMARY KEY,
email TEXT,
phone TEXT,
password TEXT,
skills TEXT,
location TEXT,
experience TEXT,
interview_status TEXT,
profile_pic TEXT,
resume TEXT,
certificates TEXT

)

""")

conn.commit()

# ---------- JOB DATA ----------

data={

"Job Title":[
"Software Engineer",
"Data Analyst",
"Web Developer",
"ML Engineer",
"Python Developer",
"Frontend Developer",
"Backend Developer"
],

"Skills":[
"python java algorithms",
"excel sql python",
"html css javascript react",
"python machine learning",
"python django flask",
"html css react",
"nodejs api database"
],

"Location":[
"Hyderabad",
"Bangalore",
"Chennai",
"Hyderabad",
"Pune",
"Bangalore",
"Delhi"
],

"Company":[
"TCS",
"Infosys",
"Wipro",
"Accenture",
"HCL",
"Capgemini",
"Tech Mahindra"
],

"HR":[
"hr@tcs.com",
"jobs@infosys.com",
"careers@wipro.com",
"hr@accenture.com",
"hr@hcl.com",
"jobs@capgemini.com",
"hr@techmahindra.com"
],

"Support":[
"support@tcs.com",
"support@infosys.com",
"support@wipro.com",
"support@accenture.com",
"support@hcl.com",
"support@capgemini.com",
"support@techmahindra.com"
],

"Interview":[
"Coding + HR",
"Aptitude + SQL",
"Portfolio",
"ML Case Study",
"Coding Round",
"UI Task",
"Backend Task"
]

}

df=pd.DataFrame(data)

# ---------- COURSES ----------

courses={

"python":[
"https://youtube.com/watch?v=rfscVS0vtbw",
"https://w3schools.com/python"
],

"machine":[
"https://youtube.com/watch?v=Gv9_4yMHFhI"
],

"learning":[
"https://coursera.org/learn/machine-learning"
],

"react":[
"https://youtube.com/watch?v=bMknfKXIFA8"
],

"sql":[
"https://youtube.com/watch?v=HXV3zeQKqGY"
],

"javascript":[
"https://youtube.com/watch?v=W6NZfCO5SIk"
]

}

# ---------- FUNCTIONS ----------

def hash_password(password):

    return hashlib.sha256(
    password.encode()
    ).hexdigest()

def register_user(username,email,phone,password):

    try:

        c.execute(

        """INSERT INTO users VALUES(?,?,?,?,?,?,?,?,?,?,?)""",

        (

        username,
        email,
        phone,
        hash_password(password),
        "",
        "",
        "",
        "Not Applied",
        "",
        "",
        ""

        )

        )

        conn.commit()

        return True

    except:

        return False

def login_user(username,password):

    c.execute(

    "SELECT * FROM users WHERE username=? AND password=?",

    (

    username,
    hash_password(password)

    )

    )

    return c.fetchone()

def update_profile(
username,
skills,
location,
experience,
profile,
resume,
cert
):

    profile_path=None
    resume_path=None
    cert_path=None

    if profile:

        profile_path="profile_images/"+username+".jpg"

        with open(profile_path,"wb") as f:
            f.write(profile.getbuffer())

    if resume:

        resume_path="resumes/"+resume.name

        with open(resume_path,"wb") as f:
            f.write(resume.getbuffer())

    if cert:

        cert_path="certificates/"+cert.name

        with open(cert_path,"wb") as f:
            f.write(cert.getbuffer())

    c.execute(

    """UPDATE users 
    SET skills=?,location=?,experience=?,
    profile_pic=COALESCE(?,profile_pic),
    resume=COALESCE(?,resume),
    certificates=COALESCE(?,certificates)
    WHERE username=?""",

    (

    skills,
    location,
    experience,
    profile_path,
    resume_path,
    cert_path,
    username

    )

    )

    conn.commit()

def recommend_jobs(user_skills,location):

    vec=TfidfVectorizer(stop_words="english")

    tfidf=vec.fit_transform(df["Skills"])

    user_vec=vec.transform([user_skills])

    sim=cosine_similarity(
    user_vec,
    tfidf
    ).flatten()

    df["score"]=sim

    df["loc"]=df["Location"].apply(

    lambda x:
    0.3 if location and x.lower()==location.lower()
    else 0

    )

    df["final"]=df["score"]+df["loc"]

    return df.sort_values(
    by="final",
    ascending=False
    )

# ---------- SESSION ----------

if "page" not in st.session_state:
    st.session_state.page="login"

if "show_jobs" not in st.session_state:
    st.session_state.show_jobs=False

# ---------- LOGIN ----------

if st.session_state.page=="login":

    st.title("AI JOB PORTAL")

    user=st.text_input("Username")

    pwd=st.text_input(
    "Password",
    type="password"
    )

    if st.button("Login"):

        data=login_user(user,pwd)

        if data:

            st.session_state.user=user
            st.session_state.page="dashboard"

            st.rerun()

        else:

            st.error("Invalid login")

    if st.button("Register"):

        st.session_state.page="register"
        st.rerun()

# ---------- REGISTER ----------

if st.session_state.page=="register":

    st.title("Create Account")

    name=st.text_input("Name")

    email=st.text_input("Email")

    phone=st.text_input("Phone")

    pwd=st.text_input(
    "Password",
    type="password"
    )

    if st.button("Create Account"):

        if register_user(
        name,email,phone,pwd
        ):

            st.session_state.user=name
            st.session_state.page="profile"

            st.rerun()

        else:

            st.error("User exists")

# ---------- FIRST PROFILE ----------

if st.session_state.page=="profile":

    st.title("Complete Profile")

    skills=st.text_area("Skills")

    location=st.text_input("Location")

    exp=st.selectbox(

    "Experience",

    [
    "Fresher",
    "1-2 Years",
    "3-5 Years"
    ]

    )

    if st.button("Save Profile"):

        update_profile(

        st.session_state.user,
        skills,
        location,
        exp,
        None,
        None,
        None

        )

        st.session_state.page="dashboard"

        st.rerun()

# ---------- DASHBOARD ----------

if st.session_state.page=="dashboard":

    left,right=st.columns([1,2])

    c.execute(

    "SELECT * FROM users WHERE username=?",

    (st.session_state.user,)

    )

    user=c.fetchone()

    with left:

        st.subheader("Profile")

        if user[8]:

            st.image(user[8],width=150)

        else:

            st.image(
            "https://cdn-icons-png.flaticon.com/512/149/149071.png",
            width=150
            )

        st.write("Name:",user[0])
        st.write("Email:",user[1])
        st.write("Phone:",user[2])
        st.write("Skills:",user[4])
        st.write("Location:",user[5])
        st.write("Experience:",user[6])

        st.info(
        "Interview: "+str(user[7])
        )

        if st.button("Logout"):

            st.session_state.page="login"
            st.session_state.show_jobs=False

            st.rerun()

    with right:

        tab1,tab2=st.tabs([
        "Update Profile",
        "Job Recommendation"
        ])

        with tab1:

            skills=st.text_area(
            "Skills",
            value=user[4]
            )

            location=st.text_input(
            "Location",
            value=user[5]
            )

            exp=st.selectbox(

            "Experience",

            [
            "Fresher",
            "1-2 Years",
            "3-5 Years",
            "5+ Years"
            ]

            )

            photo=st.file_uploader(
            "Profile Photo"
            )

            resume=st.file_uploader(
            "Resume"
            )

            cert=st.file_uploader(
            "Certificate"
            )

            if st.button("Update"):

                update_profile(

                st.session_state.user,
                skills,
                location,
                exp,
                photo,
                resume,
                cert

                )

                st.success("Updated")

        with tab2:

            if st.button("Find Jobs"):

                st.session_state.show_jobs=True

            if st.session_state.show_jobs:

                jobs=recommend_jobs(
                user[4],
                user[5]
                )

                user_skills=set(
                user[4].lower().split()
                )

                for i,row in jobs.iterrows():

                    if row["final"]<0.35:
                        continue

                    job_skills=set(
                    row["Skills"].lower().split()
                    )

                    missing=job_skills-user_skills

                    st.subheader(
                    row["Job Title"]
                    )

                    st.write(
                    "Company:",
                    row["Company"]
                    )

                    st.write(
                    "HR:",
                    row["HR"]
                    )

                    st.write(
                    "Support:",
                    row["Support"]
                    )

                    st.progress(
                    int(row["final"]*100)/100
                    )

                    if missing:

                        st.warning(
                        "Missing skills: "+
                        ",".join(missing)
                        )

                        for m in missing:

                            if m in courses:

                                if st.button(

                                "Learn "+m,

                                key="learn"+str(i)+m

                                ):

                                    st.session_state.skill=m
                                    st.session_state.page="learn"

                                    st.rerun()

                        continue

                    if st.button(
                    "Apply",
                    key=row["Job Title"]
                    ):

                        c.execute(

                        """UPDATE users 
                        SET interview_status=? 
                        WHERE username=?""",

                        (

                        "Applied at "+
                        row["Company"],

                        st.session_state.user

                        )

                        )

                        conn.commit()

                        st.success("Applied")

# ---------- LEARNING ----------

if st.session_state.page=="learn":

    skill=st.session_state.skill

    st.title("Learn "+skill)

    if skill in courses:

        for link in courses[skill]:

            st.write(link)

    else:

        st.write(
        "Search basics of "+skill+" on YouTube"
        )

    if st.button("Back to jobs"):

        st.session_state.page="dashboard"

        st.rerun()
