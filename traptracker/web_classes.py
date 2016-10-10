from flask import render_template, request, redirect, url_for, send_file, flash
import flask_login

import traptracker.orm as orm
from traptracker import app, loginManager
from traptracker.orm import Line, Trap, Catch, Animal, create_hashed_line
from traptracker.auth import authenticate, AUTH_NONE, AUTH_CATCH, AUTH_LINE, LoginForm, CreateLineForm

from datetime import datetime
from io import BytesIO
import xlsxwriter
import string


@loginManager.user_loader
def load_user(id):
    sess = orm.get_session()
    line = sess.query(Line).get(id)
    sess.close()
    return line


@app.route("/", methods=["GET"])
def index():
    flask_login.logout_user()
    sess = orm.get_session()
    result = render_template("index.html", lines=sess.query(Line).all())
    sess.close()
    return result


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    next = request.args.get('next')
    id = 0
    if next is not None:
        id = int(next.split('/')[-1])

    if form.validate_on_submit():
        sess = orm.get_session()
        line = sess.query(Line).filter_by(id=form.name.data).first()
        sess.close()

        if not line:
            flash("Username or Password is invalid", "error")
            return redirect(url_for("login"))

        flask_login.login_user(line)

        flash("Logged in successfully", "confirm")
        return redirect(next or url_for("index"))

    # GET Request
    return render_template("login.html", form=form, id=id, next=next)


@app.route("/logout", methods=["GET"])
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return redirect(url_for("index"))


@app.route("/about", methods=["GET"])
def about():
    return render_template("about.html")


@app.route("/create", methods=["GET", "POST"])
def create():
    form = CreateLineForm()
    sess = orm.get_session()
    animals = sess.query(Animal).all()
    sess.close()

    if form.validate_on_submit():
        if form.uPassword.data != form.re_uPassword.data or form.aPassword.data != form.re_aPassword.data:
            flash("The passwords inserted did not match", "error")
            return render_template("create.html", form=form)

        sess = orm.get_session()

        # Get ID's for animals
        animalsID = []
        for name in [form.animal1.data, form.animal2.data, form.animal3.data]:
            animal = sess.query(Animal).filter_by(name=string.capwords(name)).first()
            if not animal:
                new_animal = Animal(name)
                sess.add(new_animal)
                sess.commit()
                animalsID.append(new_animal.id)
            else:
                animalsID.append(animal.id)

        line = create_hashed_line(form.name.data, form.uPassword.data, form.aPassword.data,
                                  animalsID[0], animalsID[1], animalsID[2])

        # Write to database
        try:
            sess.add(line)
            sess.commit()
        except:
            flash("The line name already exists in the database", "error")
            return render_template("create.html", form=form)
        finally:
            sess.close()

        flash("The new line for {} was successfully created".format(form.name.data), "confirm")
        return redirect(url_for("index"))

    # On GET Request
    return render_template("create.html", form=form, animals=animals)


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
@flask_login.login_required
def traps(number):
    sess = orm.get_session()
    trapData = sess.query(Trap).filter_by(line_id=number).all()

    avgLat, avgLong = 0, 0
    for trap in trapData:
        avgLat += trap.lat
        avgLong += trap.long

    avgLat /= len(trapData)
    avgLong /= len(trapData)

    result = render_template("traps.html", traps=trapData, avg=(avgLat, avgLong),
                           name=sess.query(Line).filter_by(id=number).first().name)
    sess.close()
    return result


@app.route("/export/<int:number>", methods=["GET"])
def export(number):
    sess = orm.get_session()
    catchData = sess.query(Catch, Trap, Animal).join(Trap).join(Animal).\
        filter(Trap.line_id == number).order_by(Catch.time.asc(), Trap.line_id.asc()).all()
    line = sess.query(Line).filter_by(id=number).first()
    traps = sess.query(Trap.line_order).filter_by(line_id=number).order_by(Trap.line_order.asc()).all()

    # Because it is returned in tuples
    traps = [trap[0] for trap in traps]
    print(traps)

    sess.close()

    # Incase they access with no catches at all
    if len(catchData) == 0:
        flash("No catches has been recorded for this line", "error")
        return redirect(url_for("index"))


    # Create xlsx writer and byte stream
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet()

    # Create formats
    boldFormat = workbook.add_format({'bold': True})
    dateFormat = workbook.add_format({'num_format': 'dd/mm/yy', 'bold': True})

    row = 2
    col = 0

    # Write headers
    worksheet.write('A1', line.name, boldFormat)
    worksheet.write('A2', 'Traps', boldFormat)

    # Write traps along the side
    for trapi in traps:
        worksheet.write(row, col, trapi)
        row += 1

    # Write data into table
    col = 1
    currentDate = datetime.fromtimestamp(catchData[0][0].time)
    cDateStr = currentDate.strftime("%d/%m/%y")

    worksheet.write(1, col, currentDate, dateFormat)

    for catch in catchData:
        wDate = datetime.fromtimestamp(catch[0].time)
        wDateStr = wDate.strftime("%d/%m/%y")
        if wDateStr != cDateStr:
            cDateStr = wDateStr
            col += 1
            worksheet.write(1, col, wDate, dateFormat)
        worksheet.write(2+traps.index(catch[1].line_order), col, catch[2].name)

    # Wrap up and return file
    workbook.close()
    output.seek(0)
    return send_file(output, attachment_filename="caputres.xlsx", as_attachment="True")
