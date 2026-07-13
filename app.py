from flask import Flask, render_template, request, redirect, session
from flask_bcrypt import Bcrypt
import sqlite3

app = Flask(__name__)
app.secret_key = "secretkey"

bcrypt = Bcrypt(app)

# Database Connection
connection = sqlite3.connect("ngo.db", check_same_thread=False)
cursor = connection.cursor()

# Users Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT,
    email TEXT UNIQUE,
    password_hash TEXT,
    role TEXT
)
""")

# Projects Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS projects(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    description TEXT,
    status TEXT,
    start_date TEXT,
    end_date TEXT,
    location TEXT
)
""")

# Project Images Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS project_images(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    image_url TEXT
)
""")

connection.commit()
# Media Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS media(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    category TEXT,
    description TEXT,
    image_url TEXT,
    video_url TEXT
)
""")

connection.commit()


# Manage Media
@app.route("/manage-media", methods=["GET", "POST"])
def manage_media():

    if request.method == "POST":

        title = request.form["title"]
        category = request.form["category"]
        description = request.form["description"]
        image_url = request.form["image_url"]
        video_url = request.form["video_url"]

        cursor.execute("""
        INSERT INTO media
        (title,category,description,image_url,video_url)
        VALUES(?,?,?,?,?)
        """, (
            title,
            category,
            description,
            image_url,
            video_url
        ))

        connection.commit()

        return redirect("/media")

    return render_template("manage_media.html")
# Home
@app.route("/")
def home():
    return render_template("home.html")

# Manage Images
@app.route("/manage-images")
def manage_images():

    if "user" in session:
        return render_template("manage_images.html")

    return redirect("/login")

# Register
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        full_name = request.form["full_name"]
        email = request.form["email"]

        password = bcrypt.generate_password_hash(
            request.form["password"]
        ).decode("utf-8")

        role = request.form["role"]

        cursor.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        )

        if cursor.fetchone():
            return "Email Already Registered"

        cursor.execute("""
        INSERT INTO users(full_name,email,password_hash,role)
        VALUES(?,?,?,?)
        """,(full_name,email,password,role))

        connection.commit()

        return redirect("/login")

    return render_template("register.html")


# Login
@app.route("/login", methods=["GET","POST"])
def login():

    if request.method=="POST":

        email=request.form["email"]
        password=request.form["password"]

        cursor.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        )

        user=cursor.fetchone()

        if user and bcrypt.check_password_hash(user[3],password):

            session["user"]=user[1]

            return redirect("/dashboard")

        return "Invalid Email or Password"

    return render_template("login.html")

@app.route("/forgot-password", methods=["GET","POST"])
def forgot_password():

    if request.method == "POST":

        email = request.form["email"]

        password = bcrypt.generate_password_hash(
            request.form["password"]
        ).decode("utf-8")

        cursor.execute(
            "UPDATE users SET password_hash=? WHERE email=?",
            (password, email)
        )

        connection.commit()

        return redirect("/login")

    return render_template("forgot_password.html")

# Dashboard
@app.route("/dashboard")
def dashboard():

    if "user" in session:
        return render_template("dashboard.html")

    return redirect("/login")


# Projects
@app.route("/projects")
def projects():

    cursor.execute("SELECT * FROM projects")

    projects = cursor.fetchall()

    return render_template(
        "projects.html",
        projects=projects
    )


# Manage Projects
@app.route("/manage-projects", methods=["GET","POST"])
def manage_projects():

    if request.method=="POST":

        title=request.form["title"]
        description=request.form["description"]
        status=request.form["status"]
        start_date=request.form["start_date"]
        end_date=request.form["end_date"]
        location=request.form["location"]

        cursor.execute("""
        INSERT INTO projects
        (title,description,status,start_date,end_date,location)
        VALUES(?,?,?,?,?,?)
        """,(title,description,status,start_date,end_date,location))

        connection.commit()

        return redirect("/projects")

    return render_template("manage_projects.html")

# Edit Project
@app.route('/edit-project/<int:id>', methods=['GET', 'POST'])
def edit_project(id):

    cursor = connection.cursor()

    if request.method == "POST":

        title = request.form["title"]
        description = request.form["description"]
        status = request.form["status"]
        start_date = request.form["start_date"]
        end_date = request.form["end_date"]
        location = request.form["location"]

        cursor.execute("""
        UPDATE projects
        SET title=?,
            description=?,
            status=?,
            start_date=?,
            end_date=?,
            location=?
        WHERE id=?
        """, (
            title,
            description,
            status,
            start_date,
            end_date,
            location,
            id
        ))

        connection.commit()

        return redirect("/projects")

    cursor.execute("SELECT * FROM projects WHERE id=?", (id,))
    project = cursor.fetchone()

    return render_template(
        "edit_project.html",
        project=project
    )


# Delete Project
@app.route('/delete-project/<int:id>')
def delete_project(id):

    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM projects WHERE id=?",
        (id,)
    )

    connection.commit()

    return redirect("/projects")

# Project Details
@app.route("/project-details")
def project_details():

    return render_template("project_details.html")


# Media Page
@app.route("/media")
def media():

    cursor.execute("SELECT * FROM media")
    media_list = cursor.fetchall()

    return render_template(
        "media.html",
        media_list=media_list
    )


# Edit Media
@app.route("/edit-media/<int:id>", methods=["GET", "POST"])
def edit_media(id):

    if request.method == "POST":

        title = request.form["title"]
        category = request.form["category"]
        description = request.form["description"]
        image_url = request.form["image_url"]
        video_url = request.form["video_url"]

        cursor.execute("""
        UPDATE media
        SET title=?,
            category=?,
            description=?,
            image_url=?,
            video_url=?
        WHERE id=?
        """, (
            title,
            category,
            description,
            image_url,
            video_url,
            id
        ))

        connection.commit()

        return redirect("/media")

    cursor.execute(
        "SELECT * FROM media WHERE id=?",
        (id,)
    )

    media = cursor.fetchone()

    return render_template(
        "edit_media.html",
        media=media
    )


# Delete Media
@app.route("/delete-media/<int:id>")
def delete_media(id):

    cursor.execute(
        "DELETE FROM media WHERE id=?",
        (id,)
    )

    connection.commit()

    return redirect("/media")
# Logout
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)