from flask import render_template, request, redirect, url_for, send_file, flash, session, make_response
import flask_login

import traptracker.orm as orm
from traptracker import app, loginManager
from traptracker.orm import Line, Trap, Catch, Animal, User, create_hashed_line
from traptracker.auth import authenticate, AUTH_NONE, AUTH_CATCH, AUTH_LINE
from traptracker.website_forms import LoginForm, CreateLineForm, SettingsForm

from datetime import datetime
import string
import hashlib
import binascii

def get_auth_level(line_id, level):
    if 'line_auths' not in session:
        session['line_auths'] = {}
    if str(line_id) not in session['line_auths'] or 'password' not in session['line_auths'][str(line_id)]:
        return redirect(url_for('login', level=level, next=request.url))
    if authenticate(line_id, session['line_auths'][str(line_id)]['password'])<level:
        return redirect(url_for('login', level=level, next=request.url))
    return True;

@loginManager.user_loader
def load_user(id):
    sess = orm.get_session()
    line = sess.query(User).get(id)
    sess.close()
    return line


@app.route("/", methods=["GET"])
def index():
    sess = orm.get_session()
    result = render_template("index.html", lines=sess.query(Line).all())
    sess.close()
    return result


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    next = request.args.get('next')
    line_id = 0
    if next is not None:
        line_id = int(next.split('/')[-1])

    if form.validate_on_submit():
        level = authenticate(form.name.data, form.password.data)

        if level == AUTH_NONE:
            flash("Password is invalid", "error")
            return redirect(url_for("login"))

        #store the password they used in their session for later API access
        if str(line_id) not in session['line_auths']: session['line_auths'][str(line_id)] = {}
        session['line_auths'][str(line_id)]['password'] = form.password.data

        #sess = orm.get_session()
        #user = sess.query(User).filter_by(line_id=form.name.data).filter_by(auth=level).first()
        #sess.close()

        #flask_login.login_user(user)

        flash("Logged in successfully", "confirm")
        return redirect(next or url_for("index"))

    # GET Request
    return render_template("login.html", form=form, line_id=line_id, next=next)


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
    flask_login.logout_user()
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
            sess.add(User(line.id, 1))
            sess.add(User(line.id, 2))
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
    get_auth = get_auth_level(number, AUTH_CATCH)
    if get_auth!=True:
        flash("Authentication isn't high enough", "error")
        return get_auth

    sess = orm.get_session()
    result = render_template("catches.html",
                line_id = number,
                password=session['line_auths'][str(number)]['password'],
                catches=sess.query(Catch, Trap, Animal).join(Trap).join(Animal).filter(Trap.line_id == number).all(),
                name=sess.query(Line).filter_by(id=number).first().name,
                number=number,
                datetime=datetime)
    sess.close()
    return result


@app.route("/edit/<int:number>", methods=["GET"])
def traps(number):
    get_auth = get_auth_level(number, AUTH_CATCH)
    if get_auth!=True:
        flash("Authentication isn't high enough", "error")
        return get_auth

    sess = orm.get_session()
    trapData = sess.query(Trap).filter_by(line_id=number).all()

    avgLat, avgLong = -40.351115, 176.547251

    if len(trapData) > 0:
        avgLat, avgLong = 0, 0
        for trap in trapData:
            avgLat += trap.lat
            avgLong += trap.long

        avgLat /= len(trapData)
        avgLong /= len(trapData)

    result = render_template("traps.html", line_id=number, password=session['line_auths'][str(number)]['password'], traps=trapData, avg=(avgLat, avgLong),
                             name=sess.query(Line).filter_by(id=number).first().name)
    sess.close()
    return result


@app.route("/settings/<int:number>", methods=["GET", "POST"])
def settings(number):
    get_auth = get_auth_level(number, AUTH_LINE)
    if get_auth!=True:
        flash("Authentication isn't high enough", "error")
        return get_auth

    #if flask_login.current_user.auth == 1:
    #    session.pop('_flashes', None)
    #    flash("Authentication isn't high enough", "error")
    #    return redirect(url_for("index"))

    # Set up forms and data
    form = SettingsForm()
    sess = orm.get_session()
    line = sess.query(Line).filter_by(id=number).first()
    animals = sess.query(Animal).order_by(Animal.id.asc()).all()
    sess.close()

    currentPref = [animals[i].name for i in [line.animal_1, line.animal_2, line.animal_3]]

    if form.validate_on_submit():
        userChange = False
        adminChange = False
        preferenceChange = False

        if form.oldUPassword.data and form.newUPassword.data:
            if authenticate(number, form.oldUPassword.data) == AUTH_CATCH:
                userChange = True

        if form.oldAPassword.data and form.newAPassword.data:
            if authenticate(number, form.oldAPassword.data) == AUTH_LINE:
                adminChange = True

        if form.animal1.data or form.animal2.data or form.animal3.data:
            preferenceChange = True

        print(preferenceChange)

        if userChange or adminChange or preferenceChange:
            sess = orm.get_session()
            line = sess.query(Line).filter_by(id=number).first()
            if userChange:
                hashed = hashlib.pbkdf2_hmac('sha1', str.encode(form.newUPassword.data),
                                             binascii.unhexlify(line.salt), 100000)
                line.password_hashed = binascii.hexlify(hashed).decode("utf-8")

            if adminChange:
                hashed = hashlib.pbkdf2_hmac('sha1', str.encode(form.newAPassword.data),
                                                                 binascii.unhexlify(line.salt), 100000)
                line.admin_password_hashed = binascii.hexlify(hashed).decode("utf-8")

            if preferenceChange:
                # Closure for changing preference
                def changePref(data):
                    animal = sess.query(Animal).filter_by(name=string.capwords(data)).first()
                    if not animal:
                        animal = Animal(form.animal1.data)
                        sess.add(animal)
                        sess.commit()
                    return animal.id

                if form.animal1.data:
                    line.animal_1 = changePref(form.animal1.data)

                if form.animal2.data:
                    line.animal_2 = changePref(form.animal2.data)

                if form.animal3.data:
                    line.animal_3 = changePref(form.animal3.data)

                # Update current preference
                currentPref = [animals[i].name for i in [line.animal_1, line.animal_2, line.animal_3]]

            sess.add(line)
            sess.commit()
            sess.close()

            flash("Changes to line made", "confirm")
            return render_template("settings.html", form=form, animals=animals, currentPref=currentPref)

        else:
            flash("Incorrect password given", "error")
            return render_template("settings.html", form=form, animals=animals, currentPref=currentPref)

    # GET Request
    return render_template("settings.html", form=form, animals=animals, currentPref=currentPref)



@app.route("/export/<int:number>", methods=["GET"])
def export(number):
    sess = orm.get_session()
    catchData = sess.query(Catch, Trap, Animal).join(Trap).join(Animal).\
        filter(Trap.line_id == number).order_by(Catch.time.asc(), Trap.line_id.asc()).all()
    line = sess.query(Line).filter_by(id=number).first()
    traps = sess.query(Trap.line_order).filter_by(line_id=number).order_by(Trap.line_order.asc()).all()

    # Because it is returned in tuples
    traps = ["Traps"] + [str(trap[0]) for trap in traps]

    sess.close()

    # Incase they access with no catches at all
    if len(catchData) == 0:
        flash("No catches has been recorded for this line", "error")
        return redirect(url_for("index"))

    # Get ready to export
    exportData = [traps]
    currentDate = datetime.fromtimestamp(int(catchData[0][0].time))
    cDateStr = currentDate.strftime("%d/%m/%y")

    period = [cDateStr] + ["" for i in range(len(traps)-1)]

    for catch in catchData:
        wDate = datetime.fromtimestamp(int(catch[0].time))
        wDateStr = wDate.strftime("%d/%m/%y")
        if wDateStr != cDateStr:
            cDateStr = wDateStr
            exportData.append(period)
            period = [cDateStr] + ["" for i in range(len(traps)-1)]
        period[traps.index(str(catch[1].line_order))] = catch[2].name

    # Add unadded period to the end
    exportData.append(period)

    # Transpose
    exportData = list(map(list, zip(*exportData)))

    # Make resposne and return
    response = make_response(line.name + "\n" + "\n".join([",".join(l) for l in exportData]))
    response.headers["Content-Disposition"] = "attachment; filename=captures.csv"
    return response

