from finance_managment_app.backend.schema import ma
from marshmallow import fields

class User(ma.Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)

    class Meta():
        fields = ('username', 'password')

user_auth_schema = User() 
