from flask import render_template, redirect

def register_login_routes(app):

    @app.route("/")
    def home():
        return redirect("/login")

    @app.route("/login")
    def login():
        return render_template("login.html")