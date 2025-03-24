from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, PasswordField, EmailField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, length, NumberRange, ValidationError
from flask_wtf.file import FileField, FileRequired

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length, ValidationError, Regexp


# Custom Email Validator
def dut4life_email_validator(form, field):
    email = field.data.lower()
    if not (email.endswith('@dut4life.ac.za') or email.endswith('@dut.ac.za')):
        raise ValidationError("Only DUT student emails (@dut4life.ac.za or @dut.ac.za) are allowed.")


# Strong Password Validator
password_regex = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{7,}$'


class SignUpForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), dut4life_email_validator])
    username = StringField('Username', validators=[DataRequired(), length(min=2)])
    department = SelectField('Department', choices=[
        ('Select Option', 'Select Option'),
        ('Information Technology', 'Information Technology'),
        ('Engineering', 'Engineering'),
        ('Hospitality', 'Hospitality'),
        ('Nursing', 'Nursing'),
        ('Agriculture', 'Agriculture'),
        ('Information Management', 'Information Management'),
        ('Education', 'Education'),
        ('Food Science', 'Food Science'),
        ('Accounting', 'Accounting'),
        ('General', 'General')
    ], validators=[DataRequired()])
    password1 = PasswordField('Enter Your Password', validators=[DataRequired(),
length(min=6)])
    password2 = PasswordField('Confirm Your Password', validators=[DataRequired(),
length(min=6)])
    submit = SubmitField('Sign Up')

    # Custom validator for password match
    def validate_password2(self, field):
        if self.password1.data != field.data:
            raise ValidationError("Passwords do not match.")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class PasswordChangeForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired(), length(min=6)])
    new_password = PasswordField('New Password', validators=[DataRequired(), length(min=6)])
    confirm_new_password = PasswordField('Confirm New Password', validators=[DataRequired(), length(min=6)])
    change_password = SubmitField('Change Password')


class ShopItemsForm(FlaskForm):
    product_name = StringField('Name of Product', validators=[DataRequired()])
    current_price = FloatField('Current Price', validators=[DataRequired()])
    previous_price = FloatField('Previous Price', validators=[DataRequired()])
    in_stock = IntegerField('In Stock', validators=[DataRequired(), NumberRange(min=0)])
    product_picture = FileField('Product Picture', validators=[DataRequired()])
    flash_sale = BooleanField('Flash Sale')

    department = SelectField('Department', choices=[
        ('Select', 'Select') ,
        ('Information Technology', 'Information Technology'),
        ('Engineering', 'Engineering'),
        ('Hospitality', 'Hospitality'),
        ('Nursing', 'Nursing'),
        ('Agriculture', 'Agriculture'),
        ('Information Management', 'Information Management'),
        ('Education', 'Education'),
        ('Food Science', 'Food Science'),
        ('Accounting', 'Accounting'),
        ('General', 'General')

    ], validators=[DataRequired()])



    add_product = SubmitField('Add Product')
    update_product = SubmitField('Update')


class OrderForm(FlaskForm):
    order_status = SelectField(
        'Order Status',
        choices=[
            ('Pending', 'Pending'),
            ('Accepted', 'Accepted'),
            ('Out for delivery', 'Out for delivery'),
            ('Delivered', 'Delivered'),
            ('Canceled', 'Canceled')

        ]
    )
    update = SubmitField('Update Status')








