from app import app, db
from flask import render_template, url_for, redirect, flash, request, session, jsonify
from models import Article, User, Comment
from datetime import datetime
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
import os, random, string
from flask import send_from_directory


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "log_in"


# consumer_key = secret_data.consumer_key
# consumer_secret = secret_data.consumer_secret
# google_bp = make_google_blueprint(
#     client_id=consumer_key,
#     client_secret=consumer_secret,
#     scope=["profile", "email"],
#     redirect_to="login_google_authorized",
#     reprompt_consent=True,
# )
# app.register_blueprint(google_bp, url_prefix="/login")


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def random_string(n):
    return "".join(random.choices(string.ascii_letters + string.digits, k=n))


def generate_random_name(filename):
    name, extention = os.path.splitext(filename)
    random_part = random_string(25)
    return f"{name}_{random_part}{extention}"


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@login_manager.user_loader
def load_user(user_id):
    print(user_id)
    return User.query.get(int(user_id))


@app.route("/")
def index():
    recent_articles = Article.query.order_by(Article.date.desc()).limit(10).all()
    return render_template("index.html", recent_articles=recent_articles)


@app.route("/profile")
@login_required
def profile():
    user = current_user
    your_articles = Article.query.filter_by(author=user.id).all()
    return render_template("profile.html", user=user, your_articles=your_articles)


@app.route("/profile/change_profile_picture", methods=["GET", "POST"])
@login_required
def change_profile_picture():
    if request.method == "POST":
        if "new_profile_picture" in request.files:
            new_picture = request.files["new_profile_picture"]
            if new_picture.filename != "" and allowed_file(new_picture.filename):
                picture_name = secure_filename(generate_random_name(new_picture.filename))
                new_picture.save(os.path.join(app.config['UPLOAD_FOLDER'], picture_name))
                flash("New Picture was successfully saved")
            else:
                flash("Something wrong with a name of the picture")
            current_user.profile_picture = picture_name
            db.session.commit()
            return redirect(url_for("profile"))
        return redirect(url_for("change_profile_picture"))
    return render_template("change_profile_picture.html")


@app.route("/article/<int:article_id>", methods=["GET", "POST"])
def article(article_id):
    article = Article.query.get_or_404(article_id)
    recent_comments = Comment.query.filter_by(article=article_id).order_by(Comment.date_in_seconds.desc()).limit(10).all()
    if request.method == "POST":
        comment = Comment(author = current_user.login,
                          text = request.form["comment_text"],
                          article = article_id,
                          date = datetime.now())
        db.session.add(comment)
        db.session.commit()
        flash("Comment was successfully added")
        return redirect(url_for("article", article_id=article_id))
    return render_template("article.html", article=article, recent_comments=recent_comments)


@app.route("/add_comment", methods=["POST"])
def add_comment():
    comment_text = request.form["comment"]
    article_id = request.form["article_id"]
    author = current_user.login
    comment = Comment(author = author,
                    text = comment_text,
                    article = article_id,
                    date = datetime.now())
    db.session.add(comment)
    db.session.commit()
    print("success")
    return jsonify({"comment": comment_text, "author": author})


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        formatted_date = datetime.now()
        filename = None

        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(generate_random_name(file.filename))
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                flash("File was successfully saved")
            else:
                flash("File is not allowed")
        else:
            flash("There is no image")
        
        article = Article(title = request.form["title"],
                    description = request.form["description"],
                    text = request.form["text"],
                    date = formatted_date,
                    author = current_user.id,
                    likes = 0,
                    views = 0,
                    image = filename)
        db.session.add(article)
        db.session.commit()
        flash("New Article was added")
        return redirect(url_for("index"))
    return render_template("add.html")


@app.route("/sign_up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        user = User(name = request.form["name"],
                    login = request.form["username"])
        user.set_password(request.form["password"])
        db.session.add(user)
        db.session.commit()
        flash("New User was added")
        return redirect(url_for("index"))
    return render_template("add_user.html")


@app.route("/log_in", methods=["GET", "POST"])
def log_in():
    if request.method == "POST":
        user = User.query.filter_by(login=request.form['username']).first()
        if user:
            if user.check_password(request.form['password']):
                login_user(user)
                flash("You are successfully logged in", category="success")
                return redirect(url_for("index"))
            else:
                flash("Password is incorrect", category="error")
        else:
            flash("There is no user with such a ligin", category="error")
    return render_template("log_in.html")


# @app.route("/login/google")
# def login_google():
#     if not google.authorized:
#         return redirect(url_for("google.login"))


# @app.route("/login/google/authorized")
# def login_google_authorized():
#     resp = google.get("/oauth2/v1/userinfo")
#     if resp.ok:
#         email = resp.json()["email"]
#         user = User.query.filter_by(email=email).first()
#         if user:
#             login_user(user)
#             flash("User was successfully logged in by email")
#         else:
#             flash("There is no user with such an email")
#         return redirect(url_for("index"))
#     return redirect(url_for("sign_up"))


@app.route("/log_out", methods=["GET"])
@login_required
def log_out():
    logout_user()
    flash("You are successfully logged out", category="success")
    return redirect(url_for("index"))


