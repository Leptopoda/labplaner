from flask import Blueprint, request, jsonify
from models.user import User, UserSchema
from app import db

bp = Blueprint("user_api", __name__)

user_schema = UserSchema()
users_schema = UserSchema(many=True)


@bp.route("/", methods=["POST"])
def add_user():
    try:
        username = request.values["username"]
        if db.session.query(User).filter_by(username=username).scalar() is not None:
            return jsonify({"Status": "Failed", "reason": "username"}), 406
        email = request.values["email"]
        if db.session.query(User).filter_by(email=email).scalar() is not None:
            return jsonify({"Status": "Failed", "reason": "email"}), 406
        password = request.values["password"]
        if len(password) < 8:
            return jsonify({"Status": "Failed", "reason": "password"}), 406
        user = User()
        user.username = request.values["username"]
        user.email = request.values["email"]
        user.set_password(request.values["password"])

        db.session.add(user)
        db.session.commit()

        return user_schema.jsonify(user), 200
    except:
        return jsonify({"Status": "Failed"}), 406


@bp.route("/id/<uid>", methods=["GET"])
def get_user_by_id(uid):
    user = User.query.get(uid)
    return user_schema.jsonify(user)


@bp.route("/username/<username>", methods=["GET"])
def get_user_by_username(username):
    user = User.query.filter_by(username=username).scalar()
    return user_schema.jsonify(user)


@bp.route("/", methods=["GET"])
def get_all_users():
    all_users = User.query.all()
    result = users_schema.dump(all_users)
    return jsonify(result)
