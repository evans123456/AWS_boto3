from flask import Flask, redirect,url_for, render_template, request

app = Flask(__name__)



@app.route("/",methods = ["POST","GET"])
def home():
    if request.method == "POST":
        # user = request.form["nm"]
        service = request.form["flexRadioDefault"]
        print("The service: ",service)
        return redirect(url_for("resources",srv=service))

        
    else:
        return render_template("home.html")



@app.route("/output")
def output():
    return render_template("output.html")





@app.route("/input/lastpage",methods = ["POST","GET"])
def lastPage():
    if request.method == "POST":
        s = request.form["number_of_shots"]
        q = request.form["reporting_rate"]
        d = request.form["matching_digits"]
        print(f"S : {s}, Q: {q},D : {d}")
        return redirect(url_for("output"))

        
    else:
        return render_template("lastpage.html")
    



@app.route("/history")
def history():
    return render_template("history.html")


@app.route("/<srv>",methods = ["POST","GET"])
def resources(srv):
    if request.method == "POST":
        no_of_resources = request.form["no_of_resource"]
        print("Resources: ",no_of_resources)
        return redirect(url_for("lastPage"))

        
    else:
        return render_template("resources.html",content=srv)


if __name__ == "__main__":
    app.run(debug=True)