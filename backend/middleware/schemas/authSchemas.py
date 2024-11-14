from schema import ma
from marshmallow import fields

class User(ma.Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)

    class Meta():
        fields = ('username', 'password')

user_auth_schema = User() 

class exchange(ma.Schema):
    public_token = fields.String(required=True)
    test = fields.String(required=False)
    class Meta():
        fields = ('public_token','test')

exchange_schema = exchange()