from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET', 'POST'])
def messages():

    if request.method == 'GET':
        messages = Message.query.order_by(db.asc(Message.created_at)).all()

        msgs_serialized = [message.to_dict() for message in messages]

        response = make_response(
            jsonify(msgs_serialized),
            200
        )

        return response

    elif request.method == 'POST':
        attr_new_msg = {attr : request.json.get(attr) for attr in request.json if hasattr(Message, attr)}
        new_msg = Message(**attr_new_msg)

        db.session.add(new_msg)
        db.session.commit()

        msgs_serialized = new_msg.to_dict()

        response = make_response(
            jsonify(msgs_serialized),
            200
        )

        return response

@app.route('/messages/<int:id>', methods=['PATCH', 'DELETE'])
def messages_by_id(id):

    msg = Message.query.filter(Message.id == id).first()

    if msg == None:
        response_body = "<h1>404, message not found</h1>"
        response = make_response(response_body, 404)
        return response

    if request.method == "PATCH":

        [setattr(msg, attr, request.json.get(attr)) for attr in request.json if hasattr(Message, attr)]
               

        db.session.add(msg)
        db.session.commit()

        msgs_serialized = msg.to_dict()

        response = make_response(
            msgs_serialized,
            201,
        )
        return response
    
    elif request.method == "DELETE":

        db.session.delete(msg)
        db.session.commit()



        response_body = {"message": "Message deleted"}
        response = make_response(
            response_body,
            200
        )
        return response

if __name__ == '__main__':
    app.run(port=5555, debug=True)
