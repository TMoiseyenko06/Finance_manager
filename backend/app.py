from flask import Flask
from schema import ma
from Routes.authBP import auth_blueprint


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(f'config.{config_name}')
    ma.init_app(app)
    blue_print_config(app)
    return app

def blue_print_config(app):
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

app = create_app('DevelopmentConfig')

if __name__ == "__main__":
    app.run(debug=True)