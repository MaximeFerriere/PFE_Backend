from flask import Blueprint, jsonify, request, make_response
from flask_cors import cross_origin

from src.dto.CoachDTO import *
from src.data.CoachToDatabase import *
import uuid
import bcrypt

coachs_bp = Blueprint("coachs", __name__, url_prefix="/coachs")

# generate a new id


def generate_id():
    return str(uuid.uuid4())


@coachs_bp.route("", methods=["GET"])
def get_all_coachs():
    id = request.args.get("id", default=1, type=int)
    if (id == 1):
        return fetch_all_coachs()
    return fetch_coach(id)


@coachs_bp.route("/register", methods=["POST"])
@cross_origin()
def register():
    # Get the values from the request

    password = request.json.get('password')
    byte_pwd = password.encode('UTF-8')
    pwd_hash = bcrypt.hashpw(byte_pwd, bcrypt.gensalt())  # hashed pwd
    age = 0
    firstname = request.json.get('firstname')
    lastname = request.json.get('lastname')
    email = request.json.get('email')
    coach = CoachDTO(generate_id(), firstname, lastname, age, email, pwd_hash)
    return create_coach(coach)