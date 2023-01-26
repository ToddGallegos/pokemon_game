from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo

class PokemonCatcherForm(FlaskForm):
    pokemon_name = StringField("Pokemon Name", validators = [DataRequired()], render_kw={'autofocus': True})
    submit = SubmitField()
    
class SignUpForm(FlaskForm):
    user_name = StringField("User Name", validators= [DataRequired()], render_kw={'autofocus': True})
    email = StringField("Email", validators = [DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password')])
    first_name = StringField("First Name", validators= [DataRequired()])
    last_name = StringField("Last Name", validators= [DataRequired()])
    submit = SubmitField()
    
class SignInForm(FlaskForm):
    user_name = StringField("User Name", validators= [DataRequired()], render_kw={'autofocus': True})
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField()
    
class AttackForm(FlaskForm):
    attacker = StringField("Attacker", validators=[DataRequired()], render_kw={'autofocus': True})
    defender = StringField("Defender", validators=[DataRequired()])
    submit = SubmitField()
    
class UserAttackForm(FlaskForm):
    opponent = StringField("Opponent username", validators=[DataRequired()], render_kw={'autofocus': True})
    submit_user = SubmitField()