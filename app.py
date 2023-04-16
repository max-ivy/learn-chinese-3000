from flask import Flask, jsonify, render_template, request
from flask_pymongo import PyMongo
from bson import ObjectId
from pymongo import MongoClient
import random
from werkzeug.utils import secure_filename
import os
import csv

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27019/mandarin"
client = MongoClient(app.config["MONGO_URI"])
mongo = PyMongo(app)
db = client["mandarin"]
cards_collection = db["words"]

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def process_csv(file_path):
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            card_data = {
                "word": row["word"],
                "translation": row["translation"],
                "pinyin": row["pinyin"],
                "type": row["type"],
                "category": row["category"]
            }
            cards_collection.insert_one(card_data)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload-csv', methods=['POST'])
def upload_csv():
    # Check if the request has a file
    if 'csv-file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['csv-file']

    # Check if the file has a valid name and extension
    if not file or file.filename == '' or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file"}), 400

    # Save the file to the server
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    # Process the file and insert data into MongoDB
    process_csv(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    return jsonify({"result": "CSV data imported successfully"}), 201

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get_random_card", methods=["GET"])
def get_random_card():
    category = request.args.get('category', 'all')
    if category == 'all':
        pipeline = [
            {"$sample": {"size": 1}},
            {"$project": {
                "_id": 1,
                "word": 1,
                "translation": 1,
                "pinyin": 1,
                "type": 1,
                "category": 1,
                "word_back": 1,
                "translation_back": 1,
                "pinyin_back": 1,
                "type_back": 1,
                "category_back": 1
            }}
        ]
    else:
        pipeline = [
            {"$match": {"category": category}},
            {"$sample": {"size": 1}},
            {"$project": {
                "_id": 1,
                "word": 1,
                "translation": 1,
                "pinyin": 1,
                "type": 1,
                "category": 1,
                "word_back": 1,
                "translation_back": 1,
                "pinyin_back": 1,
                "type_back": 1,
                "category_back": 1
            }}
        ]
    random_card = cards_collection.aggregate(pipeline).next()
    random_card["_id"] = str(random_card["_id"])
    return jsonify(random_card)


@app.route("/get_card_back")
def get_card_back():
    current_card_id = ObjectId(request.args.get("current_card_id"))
    card = cards_collection.find_one({"_id": current_card_id})
    if card is None:
        return jsonify({"error": "Card not found"}), 404
    card['_id'] = str(card['_id'])  # convert ObjectId to string
    return jsonify(card)

@app.route("/get_next_card")
def get_next_card():
    current_card_id = ObjectId(request.args.get("current_card_id"))
    randomize = request.args.get("randomize") == "true"
    category = request.args.get('category', 'all')

    print(f"Next card route called with current_card_id: {current_card_id}, randomize: {randomize}, category: {category}")
    if randomize:
        if category == 'all':
            pipeline = [
                {"$sample": {"size": 1}},
                {"$project": {
                    "_id": 1,
                    "word": 1,
                    "translation": 1,
                    "pinyin": 1,
                    "type": 1,
                    "category": 1,
                }}
            ]
        else:
            pipeline = [
                {"$match": {"category": category}},
                {"$sample": {"size": 1}},
                {"$project": {
                    "_id": 1,
                    "word": 1,
                    "translation": 1,
                    "pinyin": 1,
                    "type": 1,
                    "category": 1,
                }}
            ]
        next_card = cards_collection.aggregate(pipeline).next()
    else:
        query = {"_id": {"$gt": current_card_id}}
        if category != 'all':
            query["category"] = category
        next_card = cards_collection.find_one(query, sort=[("_id", 1)])
        if not next_card and category != 'all':
            query["_id"] = {"$gt": ObjectId('000000000000000000000000')}
            next_card = cards_collection.find_one(query, sort=[("_id", 1)])

    if not next_card:
        return jsonify({"error": "No cards found"}), 404

    next_card['_id'] = str(next_card['_id'])
    return jsonify(next_card)

@app.route("/get_prev_card")
def get_prev_card():
    current_card_id = ObjectId(request.args.get("current_card_id"))
    randomize = request.args.get("randomize") == "true"
    category = request.args.get('category', 'all')

    print(f"Prev card route called with current_card_id: {current_card_id}, randomize: {randomize}, category: {category}")

    if randomize:
        if category == 'all':
            pipeline = [
                {"$sample": {"size": 1}},
                {"$project": {
                    "_id": 1,
                    "word": 1,
                    "translation": 1,
                    "pinyin": 1,
                    "type": 1,
                    "category": 1,
                }}
            ]
        else:
            pipeline = [
                {"$match": {"category": category}},
                {"$sample": {"size": 1}},
                {"$project": {
                    "_id": 1,
                    "word": 1,
                    "translation": 1,
                    "pinyin": 1,
                    "type": 1,
                    "category": 1,
                }}
            ]
        prev_card = cards_collection.aggregate(pipeline).next()
    else:
        query = {"_id": {"$lt": current_card_id}}
        if category != 'all':
            query["category"] = category
        prev_card = cards_collection.find_one(query, sort=[("_id", -1)])
        if not prev_card and category != 'all':
            query["_id"] = {"$lt": ObjectId('ffffffffffffffffffffffff')}
            prev_card = cards_collection.find_one(query, sort=[("_id", -1)])

    if not prev_card:
        return jsonify({"error": "No cards found"}), 404

    prev_card['_id'] = str(prev_card['_id'])
    return jsonify(prev_card)


@app.route("/set_randomize", methods=["POST"])
def set_randomize():
    randomize = request.json.get("randomize")
    mongo.db.settings.update_one({"name": "randomize"}, {"$set": {"value": randomize}})
    return jsonify({"success": True})

@app.route("/get_all_cards", methods=["GET"])
def get_all_cards():
    cards = cards_collection.find({}, {"_id": 1, "word": 1, "translation": 1, "pinyin": 1, "type": 1, "category": 1})
    all_cards = []

    for card in cards:
        card["_id"] = str(card["_id"])
        all_cards.append(card)

    return jsonify(all_cards)

@app.route("/add_card", methods=["POST"])
def add_card():
    card_data = request.json
    print("Request data:", request.data)
    print("Received card data:", card_data)

    new_card = {
        "word": card_data["word_input"],
        "translation": card_data["translation_input"],
        "pinyin": card_data["pinyin_input"],
        "type": card_data["type_input"],
        "category": card_data["category_input"]
    }

    cards_collection.insert_one(new_card)
    return jsonify({"result": "Card added successfully"}), 201

@app.route("/delete_card/<card_id>", methods=["DELETE"])
def delete_card(card_id):
    card_id_obj = ObjectId(card_id)
    result = cards_collection.delete_one({"_id": card_id_obj})

    if result.deleted_count == 1:
        return jsonify({"success": True})
    else:
        return jsonify({"error": "Card not found"}), 404


if __name__ == "__main__":
    app.run(debug=True, port=4991)
