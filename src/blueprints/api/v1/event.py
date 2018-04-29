from datetime import date
from flask import Blueprint, request, jsonify
from werkzeug.exceptions import NotFound, Unauthorized, BadRequest, Forbidden, RequestEntityTooLarge
from models.event import Event, EventSchema
from models.ag import AG
from models.date import Date
from models.associations import DateEvent
from app import db

bp = Blueprint("event_api", __name__)

event_schema = EventSchema()
events_schema = EventSchema(many=True)


@bp.route("/", methods=["POST"])
def add_event():

    try:
        if not g.session.authenticated:
            return Unauthorized()
    except NameError:
        return Unauthorized()

    try:
        name = request.values["name"]
        if db.session.query(Event).filter_by(name=name).scalar() is not None:
            return BadRequest(description='Eventname already exists')
        ag = request.values["ag"]
        if db.session.query(AG).filter_by(name=ag).scalar() is None:
            return NotFound(description='AG not found')
        if len(request.values["displayname"]) > 48:
            return RequestEntityTooLarge('Maximum length of 48 characters')
        if len(request.values["description"]) > 280:
            return RequestEntityTooLarge('Maximum length of 280 characters')
        dates = request.values["dates"]


        event = Event()
        event.name = name
        event.display_name = request.values["displayname"]
        event.description = request.values["description"]
        event.ag = ag
        event.date = ""

        db.session.add(event)
        db.session.commit()

        for d in dates:

            d = d.replace('-', '')
            d = date(int(d[:4]), int(d[4:6]), int(d[6:]))

            if db.session.query(Date).filter_by(day=d) is None:
                date_obj = Date()
                date_obj.day = d

                db.session.merge(date_obj)
                db.session.commit()

            else:
                date_obj = db.session.query(Date).filter_by(day=d)

            date_event = DateEvent()
            date_event.dtid = date_obj.id
            date_event.evid = event.id

            db.session.merge(date_event)
            db.session.commit()

        return jsonify({"redirect": f"/event/{name}/invite"}), 200
    except:
        return BadRequest()


@bp.route("/dates", methods=["POST"])
def add_dates():

    try:
        if not g.session.authenticated:
            return Unauthorized()
    except NameError:
        return Unauthorized()

    try:
        name = request.values["name"]
        if db.session.query(Event).filter_by(name=name).scalar() is None:
            return NotFound(description='Eventname not found')
        dates = request.values["dates"]

        event = db.session.query(Event).filter_by(name=name).scalar()

        for d in dates:

            d = d.replace('-', '')
            d = date(int(d[:4]), int(d[4:6]), int(d[6:]))

            if db.session.query(Date).filter_by(day=d) is None:
                date_obj = Date()
                date_obj.day = obj_date

                db.session.merge(date_obj)
                db.session.commit()

            else:
                date_obj = db.session.query(Date).filter_by(day=d)

            date_event = DateEvent()
            date_event.dtid = date_obj.id
            date_event.evid = event.id

            db.session.merge(date_event)
            db.session.commit()

        return jsonify({"redirect": f"/event/{name}/invite"}), 200
    except:
        return BadRequest()


@bp.route("/id/<evid>", methods=["GET"])
def get_event_by_id(evid):
    event = Event.query.get(evid)
    return event_schema.jsonify(event)


@bp.route("/name/<name>", methods=["GET"])
def get_event_by_name(name):
    event = Event.query.filter_by(name=name).scalar()
    return event_schema.jsonify(event)

@bp.route("/month/<month>", methods=["GET"])
def get_events_by_month(month):

    events = Date.query.all()
    for event in events:
        if event.events is None:
            del events

    return event_schema.jsonify(event)


@bp.route("/", methods=["GET"])
def get_all_events():
    all_events = Event.query.all()
    result = event_schema.dump(all_events)
    return jsonify(result)