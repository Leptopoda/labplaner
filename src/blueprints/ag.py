from flask import Blueprint, g, redirect, render_template, url_for
from sqlalchemy.sql import exists
from werkzeug.exceptions import NotFound, Unauthorized
from models.associations import UserAG
from models.ag import AG, AGSchema
from app import db

bp = Blueprint("ag", __name__)

ag_schema = AGSchema()
ags_schema = AGSchema(many=True)


@bp.route("/add", methods=["GET"])
def create_ag():
    if not g.session.authenticated:
        return redirect(url_for("auth.login"))

    return render_template('ag/add.html')


@bp.route("/<ag_name>", methods=["GET"])
def ag_dashboard(ag_name):
    if not g.session.authenticated:
        return Unauthorized()

    if db.session.query(exists().where(AG.name == ag_name)).scalar():
        ag: AG = AG.query.filter_by(name=ag_name).scalar()
        if db.session.query(exists().where(UserAG.uid == g.session.uid and UserAG.ag_id == ag.id)).scalar():
            user_ag = UserAG.query.filter_by(uid=g.session.uid, ag_id=ag.id).scalar()
            if user_ag.role != "NONE":
                schema = AGSchema()
                schema.context = {"ag_id": ag.id}
                return render_template('ag/dashboard.html', ag=schema.dump(ag))

        return Unauthorized()

    else:
        return NotFound()


@bp.route("/<ag_name>/invite", methods=["GET"])
def invite_ag(ag_name):
    if not g.session.authenticated:
        return Unauthorized()

    if db.session.query(exists().where(AG.name == ag_name)).scalar():
        ag: AG = AG.query.filter_by(name=ag_name).scalar()
        if db.session.query(exists().where(UserAG.uid == g.session.uid and UserAG.ag_id == ag.id)).scalar():
            user_ag = UserAG.query.filter_by(uid=g.session.uid, ag_id=ag.id).scalar()
            if user_ag.role == "MENTOR":
                return render_template('ag/invite.html', ag=ag_schema.dump(ag))

        return Unauthorized()

    else:
        return NotFound()
