from flask import Blueprint
from Controllers import authController
from Services import authServices

auth_blueprint = Blueprint('auth_blueprint',__name__)
auth_blueprint.route('/register',methods=['POST'])(authController.register)
auth_blueprint.route('/login',methods=['GET'])(authController.login)
auth_blueprint.route('/api/create_link_token', methods=['POST'])(authServices.plaid_link_token)
auth_blueprint.route('/api/info',methods=['POST'])(authServices.info)
auth_blueprint.route('/api/exchange_public_token',methods=['POST'])(authController.excange_token)
