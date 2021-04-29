"""
REST for interacting with web clients
"""

from flask import Blueprint, request

api = Blueprint('api', __name__, url_prefix='/vnet')


@api.route('/ofswitch', methods=['POST'])
def add_ofswitch():
    payload = request.json
