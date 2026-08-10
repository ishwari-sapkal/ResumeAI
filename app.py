from flask import Flask, render_template

app = Flask(__name__)


# ==========================
# Home
# ==========================

@app.route("/")
def home():
    return render_template("home.html")


# ==========================
# Authentication
# ==========================

@app.route("/auth")
def auth():
    return "<h1>Authentication Page (Coming Soon)</h1>"


# ==========================
# Dashboard
# ==========================

@app.route("/dashboard")
def dashboard():
    return "<h1>Dashboard (Coming Soon)</h1>"


# ==========================
# Resume Builder
# ==========================

@app.route("/resume-builder")
def resume_builder():
    return "<h1>Resume Builder (Coming Soon)</h1>"


# ==========================
# Preview
# ==========================

@app.route("/preview")
def preview():
    return "<h1>Resume Preview (Coming Soon)</h1>"


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

@app.route("/profile")
def profile():
    return "<h1>Profile (Coming Soon)</h1>"


# ==========================
# Run Application
# ==========================

if __name__ == "__main__":
    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )