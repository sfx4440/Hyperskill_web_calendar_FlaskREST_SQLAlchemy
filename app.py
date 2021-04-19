import datetime
from dotenv import load_dotenv
from flask import Flask, abort
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource, reqparse, inputs, fields, marshal_with
import sys

load_dotenv()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///name.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
api = Api(app)
parser = reqparse.RequestParser()
db = SQLAlchemy(app)

class Car(db.Model):
    __tablename__ = 'table_name'
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String(80), nullable=False)
    date = db.Column(db.Date, nullable=False)



resource_fields = {
    "id": fields.Integer,
    "event": fields.String,
    "date": fields.DateTime(dt_format='iso8601')
}

db.create_all()


class EventByID(Resource):
    @marshal_with(resource_fields)
    def get(self, event_id):
        event = Car.query.filter(Car.id == event_id).first()
        if event is None:
            abort(404, "The event doesn't exist!")
        return event


    def delete(self, event_id):
        event = Car.query.filter(Car.id == event_id).first()
        if event is None:
            abort(404, "The event doesn't exist!")
        else:
            db.session.delete(event)
            db.session.commit()
            return {"message": "The event has been deleted!"}


class EventResource(Resource):
    @marshal_with(resource_fields)
    def get(self):
        if not Car.query.filter(Car.date == datetime.date.today()).all():
            return {"data": "There are no events for today!"}
        else:
            return Car.query.filter(Car.date == datetime.date.today()).all()


class PostEvent(Resource):
    @marshal_with(resource_fields)
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('start_time')
        parser.add_argument('end_time')
        args = parser.parse_args()
        try:
            if not Car.query.filter(Car.date >= datetime.datetime.strptime(args['start_time'], '%Y-%m-%d'),
                                Car.date <= datetime.datetime.strptime(args['end_time'], '%Y-%m-%d')).all():
                return {"data": "There are no events for that period!"}
            else:
                return Car.query.filter(Car.date >= datetime.datetime.strptime(args['start_time'], '%Y-%m-%d'),
                                Car.date <= datetime.datetime.strptime(args['end_time'], '%Y-%m-%d')).all()
        except TypeError:
            return Car.query.all()



    def post(self):
        parser.add_argument(
            'date',
            type=inputs.date,
            help="The event date with the correct format is required! The correct format is YYYY-MM-DD!",
            required=True
        )
        parser.add_argument(
            'event',
            type=str,
            help="The event name is required!",
            required=True
        )
        args = parser.parse_args()
        car = Car(event=args['event'], date=args['date'])
        db.session.add(car)
        db.session.commit()
        return {"message": "The event has been added!",
                "event": args['event'],
                "date": str(args['date'].date())
                }


api.add_resource(EventResource, '/event/today')

api.add_resource(PostEvent, '/event')

api.add_resource(EventByID, '/event/<int:event_id>')

# do not change the way you run the program
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
