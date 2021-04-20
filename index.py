from flask import Flask, redirect,url_for, render_template, request

app = Flask(__name__)

@app.route("/<name>")
def index(name):
    return render_template("index.html",content=name, r= 2)

@app.route("/login",methods = ["POST","GET"])
def login():
    if request.method == "POST":
        user = request.form["nm"]
        print(user)
        return redirect(url_for("user",usr=user))

        
    else:
        return render_template("login.html")


@app.route("/<usr>")
def user(usr):
    return render_template("user.html",content="evans")



@app.route("/adm")
def adm():
    return redirect(url_for("user",name="Admin!"))

if __name__ == "__main__":
    app.run(debug=True)