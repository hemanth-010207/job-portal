import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title=" Job Portal",page_icon="💼",layout="wide")

st.markdown("""
<style>

.stApp{
background:linear-gradient(135deg,#eef2ff,#ffffff);
}

.profile{
background:white;
padding:20px;
border-radius:15px;
box-shadow:0 5px 15px rgba(0,0,0,0.1);
text-align:center;
}

.job{
background:white;
padding:20px;
border-radius:12px;
margin-bottom:15px;
box-shadow:0 4px 10px rgba(0,0,0,0.08);
}

.learn{
background:white;
padding:20px;
border-radius:12px;
box-shadow:0 4px 10px rgba(0,0,0,0.08);
}

.stButton>button{
background:#2563eb;
color:white;
border-radius:8px;
height:40px;
}

</style>
""",unsafe_allow_html=True)

os.makedirs("profile_images",exist_ok=True)
os.makedirs("resumes",exist_ok=True)
os.makedirs("certificates",exist_ok=True)

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
interview TEXT,
profile_pic TEXT,
resume TEXT,
certificate TEXT

)

""")

conn.commit()

df=pd.read_csv("jobs.csv")
df.drop_duplicates(inplace=True)

courses={

"python":[("Python Course","https://youtube.com/watch?v=rfscVS0vtbw")],

"java":[("Java Course","https://youtube.com/watch?v=grEKMHGYyns")],

"react":[("React Course","https://youtube.com/watch?v=bMknfKXIFA8")],

"sql":[("SQL Course","https://youtube.com/watch?v=HXV3zeQKqGY")],

"machine":[("ML Course","https://youtube.com/watch?v=Gv9_4yMHFhI")],

"aws":[("AWS Course","https://youtube.com/watch?v=3hLmDS179YE")],

"docker":[("Docker Course","https://youtube.com/watch?v=fqMOX6JJhGo")],

"linux":[("Linux Course","https://youtube.com/watch?v=ivO0tYw2XkY")],

"html":[("HTML Course","https://youtube.com/watch?v=qz0aGYrrlhU")],

"css":[("CSS Course","https://youtube.com/watch?v=1Rs2ND1ryYc")],

"javascript":[("JavaScript Course","https://youtube.com/watch?v=W6NZfCO5SIk")]

}

def hash_password(p):

    return hashlib.sha256(p.encode()).hexdigest()

def register(u,e,p,ph):

    try:

        c.execute(
        "INSERT INTO users VALUES(?,?,?,?,?,?,?,?,?,?,?)",

        (u,e,ph,hash_password(p),
        "","","Not Updated",
        "Not Applied","","","")
        )

        conn.commit()

        return True

    except:

        return False

def login(u,p):

    c.execute(
    "SELECT * FROM users WHERE username=? AND password=?",
    (u,hash_password(p))
    )

    return c.fetchone()

def update_profile(u,s,l,e,photo,resume,cert):

    pic=None
    r=None
    ce=None

    if photo:

        pic="profile_images/"+u+".jpg"

        with open(pic,"wb") as f:
            f.write(photo.getbuffer())

    if resume:

        r="resumes/"+resume.name

        with open(r,"wb") as f:
            f.write(resume.getbuffer())

    if cert:

        ce="certificates/"+cert.name

        with open(ce,"wb") as f:
            f.write(cert.getbuffer())

    c.execute("""

    UPDATE users SET 
    skills=?,
    location=?,
    experience=?,
    profile_pic=COALESCE(?,profile_pic),
    resume=COALESCE(?,resume),
    certificate=COALESCE(?,certificate)

    WHERE username=?

    """,(s,l,e,pic,r,ce,u))

    conn.commit()

def recommend_jobs(sk):

    vec=TfidfVectorizer()

    tfidf=vec.fit_transform(df["Skills"])

    user=vec.transform([sk])

    sim=cosine_similarity(user,tfidf).flatten()

    df["score"]=sim

    return df.sort_values(
    by="score",
    ascending=False
    )

if "page" not in st.session_state:
    st.session_state.page="login"

if "jobs" not in st.session_state:
    st.session_state.jobs=None

if "learn_skill" not in st.session_state:
    st.session_state.learn_skill=None

# LOGIN

if st.session_state.page=="login":

    st.title(" Job Recommendation Portal")

    u=st.text_input("Full Name")

    p=st.text_input("Password",type="password")

    if st.button("Login"):

        data=login(u,p)

        if data:

            st.session_state.user=u
            st.session_state.page="dashboard"
            st.rerun()

        else:

            st.error("Invalid username or password")

    if st.button("Create Account"):

        st.session_state.page="register"
        st.rerun()

# REGISTER

if st.session_state.page=="register":

    st.title("Register")

    n=st.text_input("Name")

    e=st.text_input("Email")

    ph=st.text_input("Phone")

    pw=st.text_input("Password",type="password")

    if st.button("Register"):

        if register(n,e,pw,ph):

            st.session_state.user=n
            st.session_state.page="profile"
            st.rerun()

        else:

            st.error("User already exists")

# PROFILE SETUP

if st.session_state.page=="profile":

    st.title("Complete Profile")

    s=st.text_area("Skills")

    l=st.text_input("Location")

    ex=st.selectbox(
    "Experience",
    ["Fresher","1-2 years","3+ years"]
    )

    photo=st.file_uploader("Profile Photo")

    resume=st.file_uploader("Resume")

    cert=st.file_uploader("Certificate")

    if st.button("Save"):

        update_profile(
        st.session_state.user,
        s,l,ex,
        photo,resume,cert
        )

        st.session_state.page="dashboard"
        st.rerun()

# DASHBOARD

if st.session_state.page=="dashboard":

    c.execute(
    "SELECT * FROM users WHERE username=?",
    (st.session_state.user,)
    )

    user=c.fetchone()

    col1,col2=st.columns([1,2])

    with col1:

        st.markdown('<div class="profile">',
        unsafe_allow_html=True)

        if user[8]:

            st.image(user[8],width=120)

        else:

            st.image(
            "https://cdn-icons-png.flaticon.com/512/149/149071.png",
            width=120
            )

        st.write("Name:",user[0])
        st.write("Email:",user[1])
        st.write("Skills:",user[4])
        st.write("Interview:",user[7])

        st.markdown('</div>',
        unsafe_allow_html=True)

        if st.button("Logout"):

            st.session_state.page="login"
            st.rerun()

    with col2:

        tab1,tab2=st.tabs(
        ["Update Profile","Job Recommendation"]
        )

        with tab1:

            s=st.text_area(
            "Skills",
            value=user[4]
            )

            l=st.text_input(
            "Location",
            value=user[5]
            )

            ex=st.selectbox(
            "Experience",
            ["Fresher","1-2 years","3+ years"]
            )

            photo=st.file_uploader("Photo")

            resume=st.file_uploader("Resume")

            cert=st.file_uploader("Certificate")

            if st.button("Update"):

                update_profile(
                user[0],
                s,l,ex,
                photo,resume,cert
                )

                st.success("Profile Updated")

        with tab2:

            if st.button("Find Jobs"):

                st.session_state.jobs = recommend_jobs(user[4])

            if st.session_state.jobs is not None:

                jobs=st.session_state.jobs

                user_skills=set(
                user[4].lower().split()
                )

                for i,row in jobs.iterrows():

                    if row["score"]<0.25:
                        continue

                    job_skills=set(
                    row["Skills"].lower().split()
                    )

                    missing = job_skills - user_skills

                    st.markdown('<div class="job">',
                    unsafe_allow_html=True)

                    st.subheader(row["Job"])

                    st.write("Company:",row["Company"])

                    st.write("Location:",row["Location"])

                    st.write("HR Email:",row["HR_Email"])

                    st.write("Phone:",row["HR_Phone"])

                    st.progress(float(row["score"]))

                    if len(missing)>0:

                        st.warning(
                        "Missing skills: "+
                        ",".join(missing)
                        )

                        for m in missing:

                            if m in courses:

                                if st.button(
                                "Learn "+m,
                                key="learn_"+str(i)+"_"+m
                                ):

                                    st.session_state.learn_skill=m

                                    st.session_state.page="learn"

                                    st.rerun()

                    else:

                        if st.button(
                        "Apply",
                        key="apply_"+row["Job"]+str(i)
                        ):

                            c.execute("""

                            UPDATE users SET interview=?
                            WHERE username=?

                            """,

                            ("Interview Scheduled - "+
                            row["Company"],user[0])

                            )

                            conn.commit()

                            st.success(
                            "Applied Successfully"
                            )

                    if st.button(
                    "Contact Support",
                    key="contact_"+str(i)
                    ):

                        st.info(
                        row["HR_Email"]+
                        " | "+
                        str(row["HR_Phone"])
                        )

                    st.markdown('</div>',
                    unsafe_allow_html=True)

# LEARNING PAGE

if st.session_state.page=="learn":

    skill=st.session_state.learn_skill

    st.title("Learning Resources")

    st.markdown('<div class="learn">',
    unsafe_allow_html=True)

    if skill:

        st.subheader(
        "Required skill: "+skill
        )

        if skill in courses:

            for name,link in courses[skill]:

                st.write(name)

                st.link_button(
                "Start Learning",
                link
                )

    st.markdown('</div>',
    unsafe_allow_html=True)

    if st.button("Back to Dashboard"):

        st.session_state.page="dashboard"

        st.rerun()"Accenture",
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
