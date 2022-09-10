from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=True)
    img_url = db.Column(db.String(500), nullable=True)
    location = db.Column(db.String(250), nullable=True)
    seats = db.Column(db.String(250), nullable=True)
    has_toilet = db.Column(db.Boolean, nullable=True)
    has_wifi = db.Column(db.Boolean, nullable=True)
    has_sockets = db.Column(db.Boolean, nullable=True)
    can_take_calls = db.Column(db.Boolean, nullable=True)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        dictionary = {}
        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self, column.name)
        return dictionary
        # return [column.name: getattr(self, column.name) for column in self.__table__.columns]


# db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/all")
def get_all_cafe():
    cafes = Cafe.query.all()
    return jsonify(cafes=[cafe.to_dict() for cafe in cafes])


## HTTP GET - Read Record
@app.route("/random")
def random_cafe():
    # cafes = db.session.query(Cafe).all()
    cafes = Cafe.query.all()
    cafe = random.choice(cafes)
    # return jsonify(cafe={
    #     "id": cafe.id,
    #     "name": cafe.name,
    #     "map_url": cafe.map_url,
    #     "img_url": cafe.img_url,
    #     "location": cafe.location,
    #     "seats": cafe.seats,
    #     "has_toilet": cafe.has_toilet,
    #     "has_wifi": cafe.has_wifi,
    #     "has_sockets": cafe.has_sockets,
    #     "can_take_calls": cafe.can_take_calls,
    #     "coffee_price": cafe.coffee_price
    # })
    return jsonify(cafe=cafe.to_dict())


@app.route("/search")
def search_cafe():
    query_location = request.args.get("loc")
    cafe = Cafe.query.filter_by(location=query_location).first()
    if cafe:
        return jsonify(cafe=cafe.to_dict())
    else:
        return jsonify(error={"Not found": "We don't have cafe at that location"})


## HTTP POST - Create Record
def str_to_bool(arg_from_url):
    if arg_from_url in ['True', ' true', 'T', 't', 'Yes', 'yes', 'y', '1']:
        return True
    else:
        return False


@app.route("/add", methods=["GET", "POST"])
def add_a_cafe():
    new_cafe = Cafe(name=request.args.get("name"),
                    map_url=request.args.get("map_url"),
                    img_url=request.args.get("img_url"),
                    location=request.args.get("location"),
                    seats=request.args.get("seats"),
                    has_toilet=str_to_bool(request.args.get("has_toilet")),
                    has_wifi=str_to_bool(request.args.get("has_wifi")),
                    has_sockets=str_to_bool(request.args.get("has_sockets")),
                    can_take_calls=str_to_bool(request.args.get("can_take_calls")),
                    coffee_price=request.args.get("coffee_price")
                    )
    db.session.add(new_cafe)
    db.session.commit()

    return jsonify(response={"success": "Successfully added the new cafe"})


## HTTP PUT/PATCH - Update Record
@app.route("/update-price/<int:cafe_id>", methods=['PATCH'])
def update_coffee_price(cafe_id):
    new_price = request.args.get("new_price")
    cafe_to_update = Cafe.query.get(cafe_id)
    if cafe_to_update:
        cafe_to_update.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"success": "Successfully update the price"}), 200
    else:
        return jsonify(error={"Not Found": "Sorry the coffee with that ID was no found in database"}), 400


## HTTP DELETE - Delete Record
@app.route("/report-closed/<int:cafe_id>", methods=['DELETE'])
def delete_cafe(cafe_id):
    api_key = request.args.get("api-key")
    if api_key == "TopSecretAPIKey":
        cafe_to_delete = Cafe.query.get(cafe_id)
        if cafe_to_delete:
            db.session.delete(cafe_to_delete)
            db.session.commit()
            return jsonify(response={"success": "Successfully deleted"}), 200
        else:
            return jsonify(error={"Not Found": "Sorry a cafe with that id was no found in the database."}), 404
    else:
        return jsonify(error={"Forbidden": "Sorry that's not allowed. Make sure you cafe correct api key."}), 403


if __name__ == '__main__':
    app.run(debug=True)
