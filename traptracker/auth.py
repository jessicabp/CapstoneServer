import traptracker.orm as orm
from traptracker.orm import Line

import flask_login
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired

import hashlib
import binascii

AUTH_NONE = 0
AUTH_CATCH = 1
AUTH_LINE = 2

def authenticate(line_id, password):
    """
    Authenticate an inputed password by comparing the line_id hashed password against given password

    Args:
        line_id -- Line id to compared hashed password stored in database to
        password -- Password to compared hashed password against

    Returned:
        Integer: level of authorisation, AUTH_NONE < AUTH_CATCH < AUTH_LINE
    """
    sess = orm.get_session()
    line = sess.query(Line).filter_by(id=line_id).first()
    if line is None:
        return False

    sess.close()

    hash_compare = hashlib.pbkdf2_hmac('sha1', str.encode(password), binascii.unhexlify(line.salt), 100000)

    if binascii.hexlify(hash_compare).decode("utf-8") == line.admin_password_hashed:
        return AUTH_LINE
    if binascii.hexlify(hash_compare).decode("utf-8") == line.password_hashed:
        return AUTH_CATCH
    return AUTH_NONE


class Anonymous(flask_login.AnonymousUserMixin):
    def __init__(self):
        self.username = "Guest"

    def __repr__(self):
        return "<User: {}>".format(self.username)


class LoginForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])


class CreateLineForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    uPassword = PasswordField('User Password', validators=[DataRequired()], render_kw={"placeholder": "User Password"})
    re_uPassword = PasswordField('re_uPassword', validators=[DataRequired()], render_kw={"placeholder": "Re-enter user password"})
    aPassword = PasswordField('Admin Password', validators=[DataRequired()], render_kw={"placeholder": "Admin Password"})
    re_aPassword = PasswordField('re_aPassword', validators=[DataRequired()], render_kw={"placeholder": "Re-enter admin Password"})
    recaptcha = RecaptchaField()
