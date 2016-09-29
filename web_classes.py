from flask import render_template, request, redirect, url_for
import flask_app as fa
from orm import Line, Trap, Catch, Animal
import os
import binascii
import hashlib

def index():
    return render_template("index.html", lines=fa.sess.query(Line).all())

def createLine():
    if request.method == "POST":
        form = request.form
        if form["uPassword"] == form["re_uPassword"] and form["aPassword"] == form["re_aPassword"]:
            # TODO: CAPTCHA
            # Create line and store in database
            salt = os.urandom(40)
            hashed = hashlib.pbkdf2_hmac('sha1', str.encode(form["uPassword"]), salt, 100000)

            line = Line(form["name"], binascii.hexlify(hashed).decode("utf-8"), binascii.hexlify(salt))
            fa.sess.add(line)
            fa.sess.commit()
            return redirect(url_for("index"))
        else:
            return redirect(url_for("index"))

    else:
        return render_template("create.html")

def catches(number):
    return render_template("catches.html", catches=fa.sess.query(Catch).join(Trap).filter(Trap.line_id == number).all(),
                           name=fa.sess.query(Line).filter_by(id=number).first().name)

def edit(number):
    return render_template("traps.html", traps=fa.sess.query(Trap).filter_by(line_id=number).all(),
                           name=fa.sess.query(Line).filter_by(id=number).first().name)

