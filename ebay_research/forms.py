from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField
from wtforms.validators import DataRequired, Length, optional, Email, EqualTo


class FreeSearch(FlaskForm):
    keywords_include = StringField(u'Keywords to Include', validators=[
        DataRequired(),
        Length(min=2, max=98)])
    keywords_exclude = StringField(u'Keywords to Exclude', validators=[
        optional(),
        Length(min=2, max=98)])
    minimum_price = DecimalField('Minimum Price', places=2,
                                 validators=[optional()])
    maximum_price = DecimalField('Maximum Price', places=2,
                                 validators=[optional()])


class EmailForm(FlaskForm):
    email = StringField(u'Enter your email address', validators=[Email(), Length(min=4, max=98),
                                                                 EqualTo('confirm_email', message='Emails must match')])
    confirm_email = StringField(u'Confirm your email address')
