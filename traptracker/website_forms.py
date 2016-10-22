from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, HiddenField
from wtforms.validators import DataRequired

animalPlaceholder = "Select animal or type in a new animal "


class LoginForm(FlaskForm):
    name = HiddenField("id")
    password = PasswordField("password", validators=[DataRequired()])
    next = HiddenField("next")


class CreateLineForm(FlaskForm):
    name = StringField("name", validators=[DataRequired()], render_kw={"placeholder": "Name of line"})
    uPassword = PasswordField("User Password", validators=[DataRequired()], render_kw={"placeholder": "User password"})
    re_uPassword = PasswordField("re_uPassword", validators=[DataRequired()], render_kw={"placeholder": "Re-enter user password"})
    aPassword = PasswordField("Admin Password", validators=[DataRequired()], render_kw={"placeholder": "Admin password"})
    re_aPassword = PasswordField("re_aPassword", validators=[DataRequired()], render_kw={"placeholder": "Re-enter admin password"})
    animal1 = StringField("Animal Preference", validators=[DataRequired()], render_kw={"placeholder": animalPlaceholder})
    animal2 = StringField("Animal Preference", validators=[DataRequired()], render_kw={"placeholder": animalPlaceholder})
    animal3 = StringField("Animal Preference", validators=[DataRequired()], render_kw={"placeholder": animalPlaceholder})
    recaptcha = RecaptchaField()


class SettingsForm(FlaskForm):
    newUPassword = PasswordField("Change user password", render_kw={"placeholder": "Enter new user password"})
    newAPassword = PasswordField("Change admin password", render_kw={"placeholder": "Enter new admin password"})
    animal1 = StringField("Animal Preference")
    animal2 = StringField("Animal Preference")
    animal3 = StringField("Animal Preference")