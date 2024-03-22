
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, RadioField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from models import Restaurant



class LoginForm(FlaskForm):

    username = StringField('Username', validators=[DataRequired()],render_kw={'autocomplete': 'off'})
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=32)])
    
    submit = SubmitField('Login', render_kw={"class": "btn btn-primary"})

    # def generate_csrf_token(self, csrf_context):
    #     return hidden_tag()



class CreateAccount(FlaskForm):

    username = StringField('Username', validators=[DataRequired()], render_kw={'placeholder': 'Username', 'autocomplete': 'off'})
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={'placeholder': 'Email', 'autocomplete': 'off'})
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=32)], render_kw={'placeholder': 'Password'})
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')], render_kw={'placeholder': 'Confirm Password'})

    submit = SubmitField('Create Account', render_kw={'placeholder': 'Create Account', 'class': 'btn btn-primary'})

    # def generate_csrf_token(self, csrf_context):
    #     return hidden_tag()
    


class DiscoverForm(FlaskForm):
    query = StringField('Search by Chef or Restaurant')
    location = StringField('Search by Location')
    star_count = RadioField('Michelin Stars', choices=[('', 'All Stars'), ('1', '1 Star'), ('2', '2 Stars'), ('3', '3 Stars')], default='')
    style = SelectField('Select Style', choices=[], coerce=str)  # Initialize with empty choices
    submit = SubmitField('Search')

    def __init__(self, *args, **kwargs):
        super(DiscoverForm, self).__init__(*args, **kwargs)
        self.style.choices = self.get_style_choices()  # Set choices dynamically during initialization

    def get_style_choices(self):
        # Fetch styles from the database or any other source
        available_styles = Restaurant.query.with_entities(Restaurant.style).distinct().all()
        # Format the styles into choices expected by SelectField
        choices = [('', 'Select Style')]  # Initial empty choice
        for style in available_styles:
            if style[0]:  # Check if the style is not empty
                choices.append((style[0], style[0]))
        return choices