from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt, check_password_hash, generate_password_hash
from database.db import db
from config import Config
from bson.objectid import ObjectId
from datetime import datetime

app = Flask(__name__)
app.config["SECRET_KEY"] = Config.SECRET_KEY

bcrypt = Bcrypt(app)

users = db["users"]
resumes = db["resumes"]

# ==========================
# Home Page
# ==========================

@app.route("/")
def home():
    return render_template("home.html")


# ==========================
# Authentication
# ==========================

@app.route("/auth")
def auth():
    return render_template("auth.html")




@app.route("/register", methods=["POST"])
def register():

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirmPassword", "")


    # ==================================================
    # CHECK REQUIRED FIELDS
    # ==================================================

    if not name or not email or not password or not confirm_password:

        flash(
            "Please complete all required fields.",
            "error"
        )

        return render_template(
            "auth.html",

            show_register=True,

            register_name=name,

            register_email=email
        )


    # ==================================================
    # CHECK PASSWORD MATCH
    # ==================================================

    if password != confirm_password:

        flash(
            "Passwords do not match. Please try again.",
            "error"
        )

        return render_template(
            "auth.html",

            show_register=True,

            register_name=name,

            register_email=email
        )


    # ==================================================
    # CHECK EXISTING EMAIL
    # ==================================================

    existing_user = users.find_one({
        "email": email
    })


    if existing_user:

        flash(
            "An account with this email already exists. Please login instead.",
            "error"
        )

        return render_template(
            "auth.html",

            show_register=True,

            register_name=name,

            register_email=email
        )


    # ==================================================
    # HASH PASSWORD
    # ==================================================

    hashed_password = bcrypt.generate_password_hash(
        password
    ).decode("utf-8")


    # ==================================================
    # CREATE USER
    # ==================================================

    users.insert_one({

        "name": name,

        "email": email,

        "password": hashed_password

    })


    # ==================================================
    # SUCCESS
    # ==================================================

    flash(
        "Account created successfully! Please login.",
        "success"
    )


    return redirect(
        url_for("auth")
    )





@app.route("/login", methods=["POST"])
def login():

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")


    # ==================================================
    # CHECK REQUIRED FIELDS
    # ==================================================

    if not email or not password:

        flash(
            "Please enter your email and password.",
            "error"
        )

        return render_template(
            "auth.html",

            login_email=email
        )


    # ==================================================
    # FIND USER
    # ==================================================

    user = users.find_one({
        "email": email
    })


    # ==================================================
    # INVALID EMAIL
    # ==================================================

    if not user:

        flash(
            "Invalid email or password. Please check your credentials and try again.",
            "error"
        )

        return render_template(
            "auth.html",

            login_email=email
        )


    # ==================================================
    # VERIFY PASSWORD
    # ==================================================

    if not bcrypt.check_password_hash(
        user["password"],
        password
    ):

        flash(
            "Invalid email or password. Please check your credentials and try again.",
            "error"
        )

        return render_template(
            "auth.html",

            login_email=email
        )


    # ==================================================
    # CREATE SESSION
    # ==================================================

    session["user_id"] = str(
        user["_id"]
    )

    session["user_name"] = user["name"]


    # ==================================================
    # SUCCESS
    # ==================================================

    flash(
        "Login successful!",
        "success"
    )


    return redirect(
        url_for("dashboard")
    )


# ==========================
# Dashboard
# ==========================

from datetime import datetime

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("auth"))

    # Logged in user
    user = users.find_one({
        "_id": ObjectId(session["user_id"])
    })

    # All resumes of this user
    user_resumes = list(
        resumes.find(
            {
                "userId": session["user_id"]
            }
        ).sort("updatedAt", -1)
    )

    # Dashboard Statistics
    total_resumes = len(user_resumes)

    latest_resume = user_resumes[0] if user_resumes else None

    last_updated = ""

    if latest_resume and latest_resume.get("updatedAt"):
        last_updated = latest_resume["updatedAt"]

    return render_template(
        "dashboard.html",
        user=user,
        resumes=user_resumes,
        total_resumes=total_resumes,
        latest_resume=latest_resume,
        last_updated=last_updated,
        current_hour=datetime.now().hour
    )

#==========================
# Template selection
# ==========================

@app.route("/select-template")
def select_template():
    return render_template("template_selection.html")

# ==========================
# Resume Builder
# ==========================

@app.route("/builder")
def builder():

    if "user_id" not in session:
        return redirect(url_for("auth"))

    return render_template(
        "resume_builder.html",
        edit_mode=False,
        resume=None
    )

# ==========================
# Resume Preview
# ==========================



@app.route("/preview", methods=["POST"])
def preview():

    data = request.form

    selected_template = request.form.get("selectedTemplate")

    return render_template(
        "preview.html",
        data=data,
        template=selected_template
    )


@app.route("/generate-resume", methods=["POST"])
def generate_resume():

    form = request.form

    selected_template = form.get("selectedTemplate", "professional")

    # ======================================================
    # PERSONAL
    # ======================================================

    personal = {

        "resumeTitle": form.get("resumeTitle"),
        "fullName": form.get("fullName"),
        "jobTitle": form.get("jobTitle"),
        "email": form.get("email"),
        "phone": form.get("phone"),
        "location": form.get("location"),
        "linkedin": form.get("linkedin"),
        "github": form.get("github"),
        "portfolio": form.get("portfolio"),
        "summary": form.get("summary")

    }

    # ======================================================
    # EDUCATION
    # ======================================================

    education = []

    degrees = form.getlist("degree[]")

    for i in range(len(degrees)):

        education.append({

            "degree": degrees[i],
            "institute": form.getlist("institute[]")[i],
            "university": form.getlist("university[]")[i],
            "startYear": form.getlist("startYear[]")[i],
            "endYear": form.getlist("endYear[]")[i],
            "cgpa": form.getlist("cgpa[]")[i]

        })

    # ======================================================
    # EXPERIENCE
    # ======================================================

    experience = []

    companies = form.getlist("company[]")

    for i in range(len(companies)):

        experience.append({

            "company": companies[i],
            "role": form.getlist("role[]")[i],
            "employmentType": form.getlist("employmentType[]")[i],
            "experienceLocation": form.getlist("experienceLocation[]")[i],
            "experienceStart": form.getlist("experienceStart[]")[i],
            "experienceEnd": form.getlist("experienceEnd[]")[i],
            "experienceDescription": form.getlist("experienceDescription[]")[i]

        })

    # ======================================================
    # PROJECTS
    # ======================================================

    projects = []

    titles = form.getlist("projectTitle[]")

    for i in range(len(titles)):

        projects.append({

            "projectTitle": titles[i],
            "projectRole": form.getlist("projectRole[]")[i],
            "technologies": form.getlist("technologies[]")[i],
            "duration": form.getlist("duration[]")[i],
            "teamSize": form.getlist("teamSize[]")[i],
            "projectType": form.getlist("projectType[]")[i],
            "projectGithub": form.getlist("projectGithub[]")[i],
            "projectLive": form.getlist("projectLive[]")[i],
            "projectDescription": form.getlist("projectDescription[]")[i]

        })

    # ======================================================
    # SKILLS
    # ======================================================

    skills = {

        "language": form.getlist("skill_languages[]"),
        "framework": form.getlist("skill_frameworks[]"),
        "database": form.getlist("skill_databases[]"),
        "tool": form.getlist("skill_tools[]"),
        "soft": form.getlist("skill_soft[]"),
        "other": form.getlist("skill_other[]")

    }

    # ======================================================
    # CERTIFICATES
    # ======================================================

    certificates = []

    certificate_titles = form.getlist("certificateTitle[]")

    for i in range(len(certificate_titles)):

        certificates.append({

            "certificateTitle": certificate_titles[i],
            "certificateOrganization": form.getlist("certificateOrganization[]")[i],
            "certificateDate": form.getlist("certificateDate[]")[i],
            "credentialId": form.getlist("credentialId[]")[i],
            "credentialUrl": form.getlist("credentialUrl[]")[i]

        })

    # ======================================================
    # LANGUAGES
    # ======================================================

    languages = []

    language_names = form.getlist("language[]")

    for i in range(len(language_names)):

        languages.append({

            "language": language_names[i],
            "proficiency": form.getlist("proficiency[]")[i]

        })

    # ======================================================
    # ADDITIONAL
    # ======================================================

    additional = {

        "achievements": form.get("achievements"),
        "publications": form.get("publications"),
        "volunteer": form.get("volunteer"),
        "interests": form.get("interests"),
        "hobbies": form.get("hobbies"),
        "activities": form.get("activities")

    }

    # ======================================================
    # SAVE RESUME TO MONGODB
    # ======================================================

    # Check logged-in user
    if "user_id" not in session:
        return redirect(url_for("auth"))

    # Get logged-in user's ID
    user_id = session["user_id"]

    # Create complete resume document
    resume_document = {

        "userId": user_id,

        "title": form.get("resumeTitle", "Untitled Resume"),

        "template": selected_template,

        "personal": {

            "fullName": form.get("fullName", ""),
            "jobTitle": form.get("jobTitle", ""),
            "email": form.get("email", ""),
            "phone": form.get("phone", ""),
            "location": form.get("location", ""),
            "linkedin": form.get("linkedin", ""),
            "github": form.get("github", ""),
            "portfolio": form.get("portfolio", ""),
            "summary": form.get("summary", "")

        },

        "skills": skills,

        "education": education,

        "experience": experience,

        "projects": projects,

        "certificates": certificates,

        "languages": languages,

        "additional": additional,

        "createdAt": datetime.utcnow(),

        "updatedAt": datetime.utcnow()

    }

    # Insert resume into MongoDB
    result = resumes.insert_one(resume_document)

    # Get newly created resume ID
    resume_id = str(result.inserted_id)


    # ======================================================
    # TEMPLATE
    # ======================================================

    if selected_template == "professional":

        return render_template(

            "professional_preview.html",

            personal=personal,
            education=education,
            experience=experience,
            projects=projects,
            skills=skills,
            certificates=certificates,
            languages=languages,
            additional=additional

        )

    elif selected_template == "modern":

        return render_template(

            "modern_preview.html",

            personal=personal,
            education=education,
            experience=experience,
            projects=projects,
            skills=skills,
            certificates=certificates,
            languages=languages,
            additional=additional

        )

    elif selected_template == "creative":

        return render_template(

            "creative_preview.html",

            personal=personal,
            education=education,
            experience=experience,
            projects=projects,
            skills=skills,
            certificates=certificates,
            languages=languages,
            additional=additional

        )

    return redirect(url_for("builder"))

@app.route("/professional-template")
def professional_template():
    return render_template("professional_preview.html")


@app.route("/modern-template")
def modern_template():
    return render_template("modern_preview.html")


@app.route("/creative-template")
def creative_template():
    return render_template("creative_preview.html")


# ==========================
# Profile
# ==========================

# ==========================================================
# PROFILE
# ==========================================================

@app.route("/profile")
def profile():

    # ------------------------------------------------------
    # LOGIN CHECK
    # ------------------------------------------------------

    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("auth"))

    # ------------------------------------------------------
    # VALIDATE USER ID
    # ------------------------------------------------------

    try:
        object_id = ObjectId(user_id)

    except Exception:
        session.clear()
        return redirect(url_for("auth"))

    # ------------------------------------------------------
    # GET USER FROM USERS COLLECTION
    # ------------------------------------------------------

    user = users.find_one({
        "_id": object_id
    })

    if not user:
        session.clear()
        return redirect(url_for("auth"))

    # ------------------------------------------------------
    # RENDER PROFILE
    # ------------------------------------------------------

    return render_template(
        "profile.html",
        user=user
    )




# ==========================================================
# UPDATE PROFILE
# ==========================================================

@app.route("/update-profile", methods=["POST"])
def update_profile():

    # ------------------------------------------------------
    # LOGIN CHECK
    # ------------------------------------------------------

    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("auth"))

    # ------------------------------------------------------
    # VALIDATE USER ID
    # ------------------------------------------------------

    try:
        object_id = ObjectId(user_id)

    except Exception:
        session.clear()
        return redirect(url_for("auth"))

    # ------------------------------------------------------
    # GET FORM DATA
    # ------------------------------------------------------

    name = request.form.get(
        "name",
        ""
    ).strip()

    email = request.form.get(
        "email",
        ""
    ).strip().lower()

    phone = request.form.get(
        "phone",
        ""
    ).strip()


    # ------------------------------------------------------
    # VALIDATION
    # ------------------------------------------------------

    if not name:

        flash(
            "Full name is required.",
            "error"
        )

        return redirect(url_for("profile"))

    if not email:

        flash(
            "Email address is required.",
            "error"
        )

        return redirect(url_for("profile"))

    # ------------------------------------------------------
    # FIND CURRENT USER
    # ------------------------------------------------------

    current_user = users.find_one({
        "_id": object_id
    })

    if not current_user:

        session.clear()

        return redirect(url_for("auth"))

    # ------------------------------------------------------
    # CHECK EMAIL DUPLICATE
    # ------------------------------------------------------

    existing_user = users.find_one({
        "email": email,
        "_id": {
            "$ne": object_id
        }
    })

    if existing_user:

        flash(
            "This email address is already registered.",
            "error"
        )

        return redirect(url_for("profile"))

    # ------------------------------------------------------
    # UPDATE USERS COLLECTION
    # ------------------------------------------------------

    users.update_one(

        {
            "_id": object_id
        },

        {
            "$set": {

                "name": name,

                "email": email,

                "phone": phone

            }
        }

    )

    # ------------------------------------------------------
    # UPDATE SESSION
    # ------------------------------------------------------

    session["user_name"] = name

    session["user_email"] = email

    # ------------------------------------------------------
    # SUCCESS
    # ------------------------------------------------------

    flash(
        "Profile updated successfully.",
        "success"
    )

    return redirect(
        url_for("profile")
    )




# ==========================================================
# UPDATE PASSWORD
# ==========================================================

@app.route("/update-password", methods=["POST"])
def update_password():

    # ------------------------------------------------------
    # LOGIN CHECK
    # ------------------------------------------------------

    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("auth"))

    # ------------------------------------------------------
    # GET FORM DATA
    # ------------------------------------------------------

    current_password = request.form.get(
        "currentPassword",
        ""
    ).strip()

    new_password = request.form.get(
        "newPassword",
        ""
    ).strip()

    confirm_password = request.form.get(
        "confirmPassword",
        ""
    ).strip()

    # ------------------------------------------------------
    # VALIDATION
    # ------------------------------------------------------

    if not current_password:

        flash(
            "Please enter your current password.",
            "error"
        )

        return redirect(url_for("profile"))

    if not new_password:

        flash(
            "Please enter a new password.",
            "error"
        )

        return redirect(url_for("profile"))

    if len(new_password) < 6:

        flash(
            "New password must contain at least 6 characters.",
            "error"
        )

        return redirect(url_for("profile"))

    if new_password != confirm_password:

        flash(
            "New password and confirm password do not match.",
            "error"
        )

        return redirect(url_for("profile"))

    if current_password == new_password:

        flash(
            "New password must be different from your current password.",
            "error"
        )

        return redirect(url_for("profile"))

    # ------------------------------------------------------
    # VALIDATE USER ID
    # ------------------------------------------------------

    try:

        object_id = ObjectId(user_id)

    except Exception:

        session.clear()

        return redirect(url_for("auth"))

    # ------------------------------------------------------
    # FIND USER
    # ------------------------------------------------------

    user = users.find_one({
        "_id": object_id
    })

    if not user:

        session.clear()

        return redirect(url_for("auth"))

    # ------------------------------------------------------
    # CHECK CURRENT PASSWORD
    # ------------------------------------------------------

    stored_password = user.get(
        "password",
        ""
    )

    try:

        password_is_correct = bcrypt.check_password_hash(
            stored_password,
            current_password
        )

    except Exception:

        password_is_correct = False

    if not password_is_correct:

        flash(
            "Current password is incorrect.",
            "error"
        )

        return redirect(url_for("profile"))

    # ------------------------------------------------------
    # HASH NEW PASSWORD WITH FLASK-BCRYPT
    # ------------------------------------------------------

    hashed_password = bcrypt.generate_password_hash(
        new_password
    ).decode("utf-8")

    # ------------------------------------------------------
    # UPDATE USERS COLLECTION
    # ------------------------------------------------------

    result = users.update_one(

        {
            "_id": object_id
        },

        {
            "$set": {
                "password": hashed_password
            }
        }

    )

    # ------------------------------------------------------
    # CHECK UPDATE
    # ------------------------------------------------------

    if result.modified_count == 1:

        flash(
            "Password updated successfully.",
            "success"
        )

    else:

        flash(
            "Password could not be updated.",
            "error"
        )

    return redirect(
        url_for("profile")
    )


@app.route("/templates")
def templates():
    return render_template("templates.html")




# ==========================================================
# MY RESUME
# ==========================================================

@app.route("/my-resume")
def my_resume():

    # ------------------------------------------------------
    # LOGIN CHECK
    # ------------------------------------------------------

    if "user_id" not in session:

        return redirect(url_for("auth"))


    user_id = session["user_id"]


    # ------------------------------------------------------
    # GET USER'S RESUMES
    # ------------------------------------------------------

    user_resumes = list(
        resumes.find(
            {
                "userId": user_id
            }
        ).sort(
            "updatedAt",
            -1
        )
    )


    # ------------------------------------------------------
    # TOTAL RESUMES
    # ------------------------------------------------------

    total_resumes = len(user_resumes)


    # ------------------------------------------------------
    # MOST USED TEMPLATE
    # ------------------------------------------------------

    template_counts = {

        "professional": 0,

        "modern": 0,

        "creative": 0

    }


    for resume in user_resumes:

        template = resume.get(
            "template",
            "professional"
        ).lower()


        if template in template_counts:

            template_counts[template] += 1


    if total_resumes > 0:

        most_used_template = max(
            template_counts,
            key=template_counts.get
        )

    else:

        most_used_template = "professional"



    # ------------------------------------------------------
    # LAST UPDATED
    # ------------------------------------------------------

    if user_resumes:
        updated_at = user_resumes[0].get("updatedAt")
    else:
        updated_at = None

    if updated_at:
        today = datetime.now().date()
        updated_date = updated_at.date()

        days_ago = (today - updated_date).days

        if days_ago == 0:
            last_updated = "Today"

        elif days_ago == 1:
            last_updated = "Yesterday"

        else:
            last_updated = f"{days_ago} days ago"

    else:
        last_updated = "Recently"


    # ------------------------------------------------------
    # RENDER PAGE
    # ------------------------------------------------------

    return render_template(

        "my-resume.html",

        resumes=user_resumes,

        total_resumes=total_resumes,

        most_used_template=most_used_template,

        last_updated=last_updated

    )




@app.route("/preview-resume/<resume_id>")
def preview_resume(resume_id):

    # ------------------------------------------------------
    # LOGIN CHECK
    # ------------------------------------------------------

    if "user_id" not in session:

        return redirect(
            url_for("auth")
        )


    # ------------------------------------------------------
    # VALIDATE OBJECT ID
    # ------------------------------------------------------

    try:

        object_id = ObjectId(resume_id)

    except Exception:

        flash(
            "Invalid resume.",
            "error"
        )

        return redirect(
            url_for("my_resume")
        )


    # ------------------------------------------------------
    # GET USER'S RESUME
    # ------------------------------------------------------

    resume = resumes.find_one({

        "_id": object_id,

        "userId": session["user_id"]

    })


    if not resume:

        flash(
            "Resume not found.",
            "error"
        )

        return redirect(
            url_for("my_resume")
        )


    # ------------------------------------------------------
    # GET DATA
    # ------------------------------------------------------

    personal = resume.get(
        "personal",
        {}
    )

    skills = resume.get(
        "skills",
        {}
    )

    education = resume.get(
        "education",
        []
    )

    experience = resume.get(
        "experience",
        []
    )

    projects = resume.get(
        "projects",
        []
    )

    certificates = resume.get(
        "certificates",
        []
    )

    languages = resume.get(
        "languages",
        []
    )

    additional = resume.get(
        "additional",
        {}
    )


    # ------------------------------------------------------
    # TEMPLATE
    # ------------------------------------------------------

    template = resume.get(
        "template",
        "professional"
    )


    if not isinstance(template, str):

        template = "professional"

    template = template.lower().strip()


    # ------------------------------------------------------
    # DATA SENT TO TEMPLATE
    # ------------------------------------------------------

    preview_data = {

        "personal": personal,

        "skills": skills,

        "education": education,

        "experience": experience,

        "projects": projects,

        "certificates": certificates,

        "languages": languages,

        "additional": additional,

        "resume_id": resume_id

    }


    # ------------------------------------------------------
    # PROFESSIONAL
    # ------------------------------------------------------

    if template == "professional":

        return render_template(

            "professional_preview.html",

            **preview_data

        )


    # ------------------------------------------------------
    # MODERN
    # ------------------------------------------------------

    if template == "modern":

        return render_template(

            "modern_preview.html",

            **preview_data

        )


    # ------------------------------------------------------
    # CREATIVE
    # ------------------------------------------------------

    if template == "creative":

        return render_template(

            "creative_preview.html",

            **preview_data

        )


    # ------------------------------------------------------
    # FALLBACK
    # ------------------------------------------------------

    return render_template(

        "professional_preview.html",

        **preview_data

    )


# ==========================================================
# EDIT RESUME
# ==========================================================

@app.route("/edit-resume/<resume_id>")
def edit_resume(resume_id):

    # ------------------------------------------------------
    # LOGIN CHECK
    # ------------------------------------------------------

    if "user_id" not in session:
        return redirect(url_for("auth"))

    # ------------------------------------------------------
    # VALIDATE RESUME ID
    # ------------------------------------------------------

    try:
        object_id = ObjectId(resume_id)

    except Exception:

        flash(
            "Invalid resume.",
            "error"
        )

        return redirect(
            url_for("my_resume")
        )

    # ------------------------------------------------------
    # GET ONLY LOGGED-IN USER'S RESUME
    # ------------------------------------------------------

    resume = resumes.find_one({
        "_id": object_id,
        "userId": session["user_id"]
    })

    # ------------------------------------------------------
    # RESUME NOT FOUND
    # ------------------------------------------------------

    if not resume:

        flash(
            "Resume not found.",
            "error"
        )

        return redirect(
            url_for("my_resume")
        )

    # ------------------------------------------------------
    # REMOVE MONGODB OBJECTID
    #
    # This is the important fix.
    # ObjectId cannot be converted directly to JSON.
    # ------------------------------------------------------

    resume["_id"] = str(resume["_id"])

    # ------------------------------------------------------
    # OPEN BUILDER IN EDIT MODE
    # ------------------------------------------------------

    return render_template(
        "resume_builder.html",
        edit_mode=True,
        resume=resume
    )









# ==========================================================
# UPDATE EXISTING RESUME
# ==========================================================

@app.route(
    "/update-resume/<resume_id>",
    methods=["POST"]
)
def update_resume(resume_id):

    # ------------------------------------------------------
    # LOGIN CHECK
    # ------------------------------------------------------

    if "user_id" not in session:

        return redirect(
            url_for("auth")
        )


    # ------------------------------------------------------
    # VALIDATE OBJECT ID
    # ------------------------------------------------------

    try:

        object_id = ObjectId(resume_id)

    except Exception:

        flash(
            "Invalid resume.",
            "error"
        )

        return redirect(
            url_for("my_resume")
        )


    # ------------------------------------------------------
    # GET ONLY USER'S RESUME
    # ------------------------------------------------------

    existing_resume = resumes.find_one({

        "_id": object_id,

        "userId": session["user_id"]

    })


    if not existing_resume:

        flash(
            "Resume not found.",
            "error"
        )

        return redirect(
            url_for("my_resume")
        )


    # ------------------------------------------------------
    # FORM
    # ------------------------------------------------------

    form = request.form

    selected_template = form.get(
        "selectedTemplate",
        existing_resume.get(
            "template",
            "professional"
        )
    )


    # ======================================================
    # PERSONAL
    # ======================================================

    personal = {

        "resumeTitle": form.get(
            "resumeTitle",
            ""
        ),

        "fullName": form.get(
            "fullName",
            ""
        ),

        "jobTitle": form.get(
            "jobTitle",
            ""
        ),

        "email": form.get(
            "email",
            ""
        ),

        "phone": form.get(
            "phone",
            ""
        ),

        "location": form.get(
            "location",
            ""
        ),

        "linkedin": form.get(
            "linkedin",
            ""
        ),

        "github": form.get(
            "github",
            ""
        ),

        "portfolio": form.get(
            "portfolio",
            ""
        ),

        "summary": form.get(
            "summary",
            ""
        )

    }


    # ======================================================
    # EDUCATION
    # ======================================================

    education = []

    degrees = form.getlist(
        "degree[]"
    )

    institutes = form.getlist(
        "institute[]"
    )

    universities = form.getlist(
        "university[]"
    )

    start_years = form.getlist(
        "startYear[]"
    )

    end_years = form.getlist(
        "endYear[]"
    )

    cgpas = form.getlist(
        "cgpa[]"
    )


    for i in range(len(degrees)):

        education.append({

            "degree":
                degrees[i],

            "institute":
                institutes[i]
                if i < len(institutes)
                else "",

            "university":
                universities[i]
                if i < len(universities)
                else "",

            "startYear":
                start_years[i]
                if i < len(start_years)
                else "",

            "endYear":
                end_years[i]
                if i < len(end_years)
                else "",

            "cgpa":
                cgpas[i]
                if i < len(cgpas)
                else ""

        })


    # ======================================================
    # EXPERIENCE
    # ======================================================

    experience = []

    companies = form.getlist(
        "company[]"
    )

    roles = form.getlist(
        "role[]"
    )

    employment_types = form.getlist(
        "employmentType[]"
    )

    experience_locations = form.getlist(
        "experienceLocation[]"
    )

    experience_starts = form.getlist(
        "experienceStart[]"
    )

    experience_ends = form.getlist(
        "experienceEnd[]"
    )

    experience_descriptions = form.getlist(
        "experienceDescription[]"
    )


    for i in range(len(companies)):

        experience.append({

            "company":
                companies[i],

            "role":
                roles[i]
                if i < len(roles)
                else "",

            "employmentType":
                employment_types[i]
                if i < len(employment_types)
                else "",

            "experienceLocation":
                experience_locations[i]
                if i < len(experience_locations)
                else "",

            "experienceStart":
                experience_starts[i]
                if i < len(experience_starts)
                else "",

            "experienceEnd":
                experience_ends[i]
                if i < len(experience_ends)
                else "",

            "experienceDescription":
                experience_descriptions[i]
                if i < len(experience_descriptions)
                else ""

        })


    # ======================================================
    # PROJECTS
    # ======================================================

    projects = []

    titles = form.getlist(
        "projectTitle[]"
    )

    project_roles = form.getlist(
        "projectRole[]"
    )

    technologies = form.getlist(
        "technologies[]"
    )

    durations = form.getlist(
        "duration[]"
    )

    team_sizes = form.getlist(
        "teamSize[]"
    )

    project_types = form.getlist(
        "projectType[]"
    )

    project_githubs = form.getlist(
        "projectGithub[]"
    )

    project_lives = form.getlist(
        "projectLive[]"
    )

    project_descriptions = form.getlist(
        "projectDescription[]"
    )


    for i in range(len(titles)):

        projects.append({

            "projectTitle":
                titles[i],

            "projectRole":
                project_roles[i]
                if i < len(project_roles)
                else "",

            "technologies":
                technologies[i]
                if i < len(technologies)
                else "",

            "duration":
                durations[i]
                if i < len(durations)
                else "",

            "teamSize":
                team_sizes[i]
                if i < len(team_sizes)
                else "",

            "projectType":
                project_types[i]
                if i < len(project_types)
                else "",

            "projectGithub":
                project_githubs[i]
                if i < len(project_githubs)
                else "",

            "projectLive":
                project_lives[i]
                if i < len(project_lives)
                else "",

            "projectDescription":
                project_descriptions[i]
                if i < len(project_descriptions)
                else ""

        })


    # ======================================================
    # SKILLS
    # ======================================================

    skills = {

        "language":
            form.getlist(
                "skill_languages[]"
            ),

        "framework":
            form.getlist(
                "skill_frameworks[]"
            ),

        "database":
            form.getlist(
                "skill_databases[]"
            ),

        "tool":
            form.getlist(
                "skill_tools[]"
            ),

        "soft":
            form.getlist(
                "skill_soft[]"
            ),

        "other":
            form.getlist(
                "skill_other[]"
            )

    }


    # ======================================================
    # CERTIFICATES
    # ======================================================

    certificates = []

    certificate_titles = form.getlist(
        "certificateTitle[]"
    )

    certificate_organizations = form.getlist(
        "certificateOrganization[]"
    )

    certificate_dates = form.getlist(
        "certificateDate[]"
    )

    credential_ids = form.getlist(
        "credentialId[]"
    )

    credential_urls = form.getlist(
        "credentialUrl[]"
    )


    for i in range(len(certificate_titles)):

        certificates.append({

            "certificateTitle":
                certificate_titles[i],

            "certificateOrganization":
                certificate_organizations[i]
                if i < len(certificate_organizations)
                else "",

            "certificateDate":
                certificate_dates[i]
                if i < len(certificate_dates)
                else "",

            "credentialId":
                credential_ids[i]
                if i < len(credential_ids)
                else "",

            "credentialUrl":
                credential_urls[i]
                if i < len(credential_urls)
                else ""

        })


    # ======================================================
    # LANGUAGES
    # ======================================================

    languages = []

    language_names = form.getlist(
        "language[]"
    )

    proficiencies = form.getlist(
        "proficiency[]"
    )


    for i in range(len(language_names)):

        languages.append({

            "language":
                language_names[i],

            "proficiency":
                proficiencies[i]
                if i < len(proficiencies)
                else ""

        })


    # ======================================================
    # ADDITIONAL
    # ======================================================

    additional = {

        "achievements":
            form.get(
                "achievements",
                ""
            ),

        "publications":
            form.get(
                "publications",
                ""
            ),

        "volunteer":
            form.get(
                "volunteer",
                ""
            ),

        "interests":
            form.get(
                "interests",
                ""
            ),

        "hobbies":
            form.get(
                "hobbies",
                ""
            ),

        "activities":
            form.get(
                "activities",
                ""
            )

    }


    # ======================================================
    # UPDATE MONGODB
    # ======================================================

    updated_at = datetime.utcnow()


    result = resumes.update_one(

        {
            "_id": object_id,

            "userId": session["user_id"]

        },

        {
            "$set": {

                "title":
                    personal["resumeTitle"],

                "template":
                    selected_template,

                "personal":
                    personal,

                "skills":
                    skills,

                "education":
                    education,

                "experience":
                    experience,

                "projects":
                    projects,

                "certificates":
                    certificates,

                "languages":
                    languages,

                "additional":
                    additional,

                "updatedAt":
                    updated_at

            }

        }

    )


    # ======================================================
    # PREVIEW UPDATED RESUME
    # ======================================================

    if result.matched_count == 1:

        flash(
            "Resume updated successfully.",
            "success"
        )

    else:

        flash(
            "Resume could not be updated.",
            "error"
        )


    preview_data = {

        "personal":
            personal,

        "skills":
            skills,

        "education":
            education,

        "experience":
            experience,

        "projects":
            projects,

        "certificates":
            certificates,

        "languages":
            languages,

        "additional":
            additional

    }


    if selected_template == "modern":

        return render_template(
            "modern_preview.html",
            **preview_data
        )


    elif selected_template == "creative":

        return render_template(
            "creative_preview.html",
            **preview_data
        )


    return render_template(
        "professional_preview.html",
        **preview_data
    )







# ==========================================================
# DELETE RESUME
# ==========================================================

@app.route(
    "/delete-resume/<resume_id>",
    methods=["POST"]
)
def delete_resume(resume_id):

    # ------------------------------------------------------
    # LOGIN CHECK
    # ------------------------------------------------------

    if "user_id" not in session:

        return redirect(
            url_for("auth")
        )


    # ------------------------------------------------------
    # VALIDATE OBJECT ID
    # ------------------------------------------------------

    try:

        object_id = ObjectId(resume_id)

    except Exception:

        flash(
            "Invalid resume.",
            "error"
        )

        return redirect(
            url_for("my_resume")
        )


    # ------------------------------------------------------
    # DELETE ONLY USER'S RESUME
    # ------------------------------------------------------

    result = resumes.delete_one({

        "_id": object_id,

        "userId": session["user_id"]

    })


    if result.deleted_count == 1:

        flash(
            "Resume deleted successfully.",
            "success"
        )

    else:

        flash(
            "Resume not found.",
            "error"
        )


    return redirect(
        url_for("my_resume")
    )








# ==========================================================
# LOGOUT
# ==========================================================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out successfully.",
        "success"
    )

    return redirect(
        url_for("auth")
    )




# ==========================
# Run Application
# ==========================

if __name__ == "__main__":
    app.run(debug=True)