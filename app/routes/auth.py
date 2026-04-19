from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_login import login_user, logout_user, login_required, current_user
import socket

from app.extensions import db, bcrypt
from app.models.user import User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user, remember=True)
            return redirect(url_for("dashboard.dashboard"))
        else:
            flash("Sai tài khoản hoặc mật khẩu", "danger")

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@auth_bp.route("/create-user", methods=["GET", "POST"])
@login_required
def create_user():
    if current_user.role != "admin":
        return "Unauthorized", 403

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        role = request.form.get("role")

        hash_pw = bcrypt.generate_password_hash(password).decode("utf-8")

        user = User(username=username, password_hash=hash_pw, role=role)
        db.session.add(user)
        db.session.commit()

        return redirect(url_for("dashboard.dashboard"))

    return render_template("create_user.html")


@auth_bp.route("/api/server-ip")
def get_server_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
    except:
        ip = "127.0.0.1"

    return {"ip": ip}