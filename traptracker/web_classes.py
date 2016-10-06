from flask import render_template, request, redirect, url_for, send_file, flash
import traptracker.orm as orm
from traptracker import app
from traptracker.orm import Line, Trap, Catch, Animal
from traptracker.auth import authenticate, AUTH_NONE, AUTH_CATCH, AUTH_LINE
from flask_googlemaps import Map
from datetime import datetime
import os
import binascii
import hashlib
from io import BytesIO
import xlsxwriter


@app.route("/", methods=["GET"])
def index():
    sess = orm.get_session()
    result = render_template("index.html", lines=sess.query(Line).all())
    sess.close()
    return result


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        return "Test" # Obv not going to be here, TODO: Log in users
    else:
        return render_template("login.html")


@app.route("/about", methods=["GET"])
def about():
    return render_template("about.html")


@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        form = request.form
        if form["uPassword"] == form["re_uPassword"] and form["aPassword"] == form["re_aPassword"]:
            # TODO: CAPTCHA
            # Create line and store in database (TODO: Change to function)
            salt = os.urandom(40)
            hashed = hashlib.pbkdf2_hmac('sha1', str.encode(form["uPassword"]), salt, 100000)

            line = Line(form["name"], binascii.hexlify(hashed).decode("utf-8"), binascii.hexlify(salt))
            sess = orm.get_session()
            sess.add(line)
            sess.commit()
            sess.close()

            flash("The new line for {} was successfully created".format(form["name"]), "confirm")
            return redirect(url_for("index"))
        else:
            flash("The passwords inserted did not match", "error")
            return redirect(url_for("create"))

    else:
        return render_template("create.html")


@app.route("/catches/<int:number>", methods=["GET"])
def catches(number):
    sess = orm.get_session()
    result = render_template("catches.html",
                catches=sess.query(Catch, Trap, Animal).join(Trap).join(Animal).filter(Trap.line_id == number).all(),
                name=sess.query(Line).filter_by(id=number).first().name,
                number=number,
                datetime=datetime)
    sess.close()
    return result


@app.route("/edit/<int:number>", methods=["GET"])
def traps(number):
    sess = orm.get_session()
    trapData = sess.query(Trap).filter_by(line_id=number).all()

    avgLat, avgLong = 0, 0
    for trap in trapData:
        avgLat += trap.lat
        avgLong += trap.long

    avgLat /= len(trapData)
    avgLong /= len(trapData)

    map = Map(
        identifier="map",
        lat = avgLat,
        lng = avgLong,
        style="height:400px;width:400px;margin:0;float=right;",
        markers=[
          { 'icon': 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png',
            'lat': trap.lat,
            'lng': trap.long,
            'infobox': "Number: {}".format(trap.line_order)
          } for trap in trapData
        ]
    )

    result = render_template("traps.html", traps=trapData, map=map,
                           name=sess.query(Line).filter_by(id=number).first().name)
    sess.close()
    return result


@app.route("/export/<int:number>", methods=["GET"])
def export(number):
    sess = orm.get_session()
    catchData = sess.query(Catch, Trap, Animal).join(Trap).join(Animal).\
        filter(Trap.line_id == number).order_by(Catch.time.asc()).all()

    # Convert data into csv format

    # Create xlsx writer and byte stream
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet()

    # Create formats
    boldFormat = workbook.add_format({'bold': True})
    dateFormat = workbook.add_format({'num_format': 'dd/mm/yy'})

    row = 1
    col = 0

    # Write headers
    worksheet.write('A1', 'Number', boldFormat)
    worksheet.write('B1', 'Animal', boldFormat)
    worksheet.write('C1', 'Date', boldFormat)

    # Write data into table
    for catch in catchData:
        worksheet.write(row, col, catch[1].line_order)
        worksheet.write(row, col+1, catch[2].name)
        worksheet.write(row, col+2, datetime.fromtimestamp(catch[0].time), dateFormat)
        row += 1

    # Wrap up and return file
    workbook.close()
    output.seek(0)
    return send_file(output, attachment_filename="caputres.xlsx", as_attachment="True")
