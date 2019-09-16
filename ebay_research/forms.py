from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField, PasswordField, IntegerField
from wtforms.validators import DataRequired, Length, optional, Email, EqualTo

STATES = [
    "Alabama",
    "Alaska",
    "Arizona",
    "Arkansas",
    "California",
    "Colorado",
    "Connecticut",
    "Delaware",
    "Florida",
    "Georgia",
    "Hawaii",
    "Idaho",
    "Illinois",
    "Indiana",
    "Iowa",
    "Kansas",
    "Kentucky",
    "Louisiana",
    "Maine",
    "Maryland",
    "Massachusetts",
    "Michigan",
    "Minnesota",
    "Mississippi",
    "Missouri",
    "Montana",
    "Nebraska",
    "Nevada",
    "New Hampshire",
    "New Jersey",
    "New Mexico",
    "New York",
    "North Carolina",
    "North Dakota",
    "Ohio",
    "Oklahoma",
    "Oregon",
    "Pennsylvania",
    "Rhode Island",
    "South Carolina",
    "South Dakota",
    "Tennessee",
    "Texas",
    "Utah",
    "Vermont",
    "Virginia",
    "Washington",
    "West Virginia",
    "Wisconsin",
    "Wyoming",
]


class EmailForm(FlaskForm):
    email = StringField(
        u"Enter your email address",
        validators=[
            Email(),
            Length(min=4, max=98),
            EqualTo("confirm_email", message="Emails must match"),
            DataRequired()
        ],
    )
    confirm_email = StringField(
        u"Confirm your email address",
        validators=[
            DataRequired()
        ]
    )
    password = PasswordField(
        u"Choose a Password",
        validators=[
            Length(min=6, max=98),
            EqualTo("confirm_password", "Passwords must match"),
            DataRequired()
        ]
    )
    confirm_password = PasswordField(
        u"Confirm Password",
        validators=[
            DataRequired()
        ]
    )
    location = SelectField(
        u"Select your location",
        choices=[("", ""), ("USA", "USA"), ("International", "International")],
        validators=[DataRequired()],
    )
    state = SelectField(
        u"Select your state", choices=[(state, state) for state in STATES]
    )


class FreeSearch(FlaskForm):
    keywords_include = StringField(
        u"Keywords to Include:", validators=[DataRequired(), Length(min=2, max=80)]
    )
    keywords_exclude = StringField(
        u"Keywords to Exclude:", validators=[optional(), Length(min=2, max=80)]
    )
    minimum_price = DecimalField("Minimum Price:", places=2, validators=[optional()])
    maximum_price = DecimalField("Maximum Price:", places=2, validators=[optional()])


class LoginForm(FlaskForm):
    email = StringField(
        u"Enter your email address",
        validators=[
            Email(),
            Length(min=4, max=98),
            DataRequired()
            ]
    )
    password = StringField(
        u"Enter your password",
        validators=[
            Length(min=6, max=98),
            DataRequired()
        ]
    )


class SendConfirmation(FlaskForm):
    email = StringField(
        u"Enter your email address",
        validators=[
            Email(),
            Length(min=4, max=98),
            EqualTo("confirm_email", "Emails must match"),
            DataRequired()
        ]
    )
    confirm_email = StringField(
        u"Confirm email address",
        validators=[
            Email(),
            Length(min=4, max=98),
            DataRequired()
        ]
    )


class ChangePassword(FlaskForm):
    password = PasswordField(
        u"Choose a Password",
        validators=[
            Length(min=6, max=98),
            EqualTo("confirm_password", "Passwords must match"),
            DataRequired()
        ]
    )
    confirm_password = PasswordField(
        u"Confirm Password",
        validators=[
            DataRequired()
        ]
    )


class RepeatSearch(FlaskForm):
    search_id = IntegerField(
        u"Enter the search id",
        validators=[
            Length(min=1, max=12),
            DataRequired()
        ]
    )


class ChooseNewPassword(FlaskForm):
    old_password = PasswordField(
        u"Enter current password ",
        validators=[
            DataRequired()
        ]
    )
    password = PasswordField(
        u"Choose a new password",
        validators=[
            Length(min=6, max=98),
            EqualTo("confirm_password", "Passwords must match"),
            DataRequired()
        ]
    )
    confirm_password = PasswordField(
        u"Confirm new password",
        validators=[
            DataRequired()
        ]
    )