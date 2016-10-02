from flask import render_template, request, redirect, url_for, make_response, flash
import flask_app as fa
from orm import Line, Trap, Catch, Animal
from datetime import datetime
import os
import binascii
import hashlib


def index():
    return render_template("index.html", lines=fa.sess.query(Line).all())

def login():
    if request.method == "POST":
        return "Test" # Obv not going to be here, TODO: Log in users
    else:
        return render_template("login.html")


def createLine():
    if request.method == "POST":
        form = request.form
        if form["uPassword"] == form["re_uPassword"] and form["aPassword"] == form["re_aPassword"]:
            # TODO: CAPTCHA
            # Create line and store in database (TODO: Change to function)
            salt = os.urandom(40)
            hashed = hashlib.pbkdf2_hmac('sha1', str.encode(form["uPassword"]), salt, 100000)

            line = Line(form["name"], binascii.hexlify(hashed).decode("utf-8"), binascii.hexlify(salt))
            fa.sess.add(line)
            fa.sess.commit()

            flash("The new line for {} was successfully created".format(form["name"]), "confirm")
            return redirect(url_for("index"))
        else:
            flash("The passwords inserted did not match", "error")
            return redirect(url_for("create"))

    else:
        return render_template("create.html")

def catches(number):
    return render_template("catches.html",
                catches=fa.sess.query(Catch, Trap, Animal).join(Trap).join(Animal).filter(Trap.line_id == number).all(),
                name=fa.sess.query(Line).filter_by(id=number).first().name,
                number=number,
                datetime=datetime)

def traps(number):
    return render_template("traps.html", traps=fa.sess.query(Trap).filter_by(line_id=number).all(),
                           name=fa.sess.query(Line).filter_by(id=number).first().name)

def export(number):
    catchData = fa.sess.query(Catch, Trap, Animal).join(Trap).join(Animal).filter(Trap.line_id == number).all()
    exportData = ["Trap Number,Animal,Time"]

    # Convert data into csv format
    for catch in catchData:
        exportData.append("{},{},{}".format(catch[1].line_order,
                                            catch[2].name,
                                            datetime.fromtimestamp(catch[0].time).strftime("%d/%m/%y") ))

    # Make response that downloads and saves locally for user
    response = make_response("\n".join(exportData))
    response.headers["Content-Disposition"] = "attachment; filename=captures.csv"
    return response

