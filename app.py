from flask import Flask, render_template, request, redirect, flash, session
from passlib.hash import sha256_crypt
from bson import ObjectId
app=Flask(__name__)
import pymongo, os
client=pymongo.MongoClient("mongodb://Aanya:1234@ac-hadaj9d-shard-00-00.xrfiz9v.mongodb.net:27017,ac-hadaj9d-shard-00-01.xrfiz9v.mongodb.net:27017,ac-hadaj9d-shard-00-02.xrfiz9v.mongodb.net:27017/?replicaSet=atlas-mm8h19-shard-0&ssl=true&authSource=admin&retryWrites=true&w=majority&appName=Cluster0", tls=True, tlsAllowInvalidCertificates=True)
db=client.Blog_page
app.secret_key=os.urandom(20)

@app.route("/", methods=["GET","POST"])
def index():
    posts=list(db.posts.find())
    return render_template("index.html", posts=posts)

@app.route("/signup", methods=["POST"])
def signup():
    e=db.users.find_one({"Email":request.form["email"]})
    if e:
        flash("Email already used in another account!", "danger")
        return redirect("/")
    y=sha256_crypt.hash(request.form["password"])
    info={"Name":request.form["name"],"Email":request.form["email"],"Contact":request.form["contact"],"Password":y}
    db.users.insert_one(info)
    flash("Signup Successful!", "success")
    return redirect("/")

@app.route("/login", methods=["POST"])
def login():
    email=request.form["reg_email"]
    password=request.form["reg_password"]
    x=db.users.find_one({"Email":email})
    if not x:
        flash("You haven't signed up yet!", "warning")
        return redirect("/")
    user=db.users.find_one({"Email": email})
    y=user["Password"]
    if sha256_crypt.verify(password,y):
        session["Email"]=email
        session["Name"]=user["Name"]
        flash("Login Complete!", "success")
        return redirect("/account_page")
    else:
        flash("Incorrect password!", "danger")
        return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully!", "info")
    return redirect("/")

@app.route("/account_page")
def account_page():
    if "Email" not in session:
        flash("Please log in first!", "warning")
        return redirect("/")
    user_posts = list(db.posts.find({"Author": session["Name"]}))
    return render_template("account_page.html", user=session["Name"], posts=user_posts)

@app.route("/create_post", methods=["GET", "POST"])
def create_post():
    if "Email" not in session:
        flash("Please log in to create a post.", "danger")
        return redirect("/")
    if request.method=="POST":
        post={"Title": request.form["title"], "Description": request.form["description"], "Content": request.form["content"], "Author": session["Name"]}
        db.posts.insert_one(post)
        flash("Post created successfully!", "success")
        return redirect("/account_page")
    return render_template("create_post.html")

@app.route("/edit_post/<post_id>", methods=["GET","POST"])
def edit_post(post_id):
    post=db.posts.find_one({"_id": ObjectId(post_id)})
    if not post:
        flash("Post not found.", "danger")
        return redirect("/")
    if post["Author"]!=session.get("Name"):
        flash("You are not authorized to edit this post.", "danger")
        return redirect("/")
    if request.method=="POST":
        db.posts.update_one({"_id": ObjectId(post_id)}, {"$set": {"Title": request.form["title"], "Description": request.form["description"], "Content": request.form["content"]}})
        flash("Post updated successfully!", "success")
        return redirect("/account_page")
    return render_template("edit_post.html", post=post)

@app.route("/view_post/<post_id>")
def view_post(post_id):
    post=db.posts.find_one({"_id": ObjectId(post_id)})
    if not post:
        flash("Post not found.", "danger")
        return redirect("/")
    return render_template("view_post.html", post=post)

@app.route("/delete_post/<post_id>", methods=["POST"])
def delete_post(post_id):
    post=db.posts.find_one({"_id": ObjectId(post_id)})
    if not post:
        flash("Post not found.", "danger")
        return redirect("/")
    if post["Author"]!=session.get("Name"):
        flash("You are not authorized to delete this post.", "danger")
        return redirect("/")
    db.posts.delete_one({"_id": ObjectId(post_id)})
    flash("Post deleted successfully", "success")
    return redirect("/account_page")

if __name__=="__main__":
    app.run(debug=True, port=8000)

# Build a simple blog application with user authentication. 
# The main page should display all blog posts with their title, description, and the author’s name. 
# Users should be able to create and edit their own blog posts, but only the author of a post should be allowed to edit it. 
# Lastly Clicking on a blog should open the full post.