from flask import Flask, render_template, jsonify, request
from flask_pymongo import PyMongo
import openai
import os
from dotenv import load_dotenv
import jwt
import datetime
from functools import wraps

load_dotenv()

app = Flask(__name__)
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
openai.api_key = os.environ.get("OPENAI_API_KEY")
mongo = PyMongo(app)

@app.route("/")
def home():
    chats = mongo.db.chats.find({})
    # print(chats)
    myChats = [chat for chat in chats]
    # print(myChats)
    return render_template("index.html", myChats=myChats)

@app.route("/signup")
def signup():
    return render_template("register.html")

@app.route("/api", methods=["GET", "POST"])
def qa():
    if request.method == "POST":
        print(request.json)
        question = request.json.get("question")
        chat = mongo.db.chats.find_one({"question": question})
        # print(chat)
        if chat:
            data = {"question": question, "answer": f"{chat['answer']}"}
            return jsonify(data)
        else:
            userMessage = {"role": "user", "content": question}

            response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages= [userMessage],
                    temperature=0.7,
                    max_tokens=256,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0
                    )
            # print(response)
            data = {"question": question, "answer": response.choices[0].message.content.strip()}
            mongo.db.chats.insert_one({"question": question, "answer": response.choices[0].message.content.strip()})
            return jsonify(data)
    data = {"result": "Thank you! I'm just a machine learning model designed to respond to questions and generate text based on my training data. Is there anything specific you'd like to ask or discuss? "}
        
    return jsonify(data)






# Add a secret key for JWT encoding
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

# Login route
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    # Check if the username exists
    user = mongo.db.users.find_one({"email": username})
    if not user:
        return jsonify({"error": "Invalid username or password"}), 401

    # Verify the password
    hashed_password = user["password"].encode("utf-8")
    if not bcrypt.checkpw(password.encode("utf-8"), hashed_password):
        return jsonify({"error": "Invalid username or password"}), 401

    # Generate an access token
    token = jwt.encode({
        "user": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)  # Token expiration time
    }, app.config["SECRET_KEY"])

    return jsonify({"token": token.decode("utf-8")}), 200

# Decorator for token verification
def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]

        if not token:
            return jsonify({"error": "Token is missing"}), 401

        try:
            data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user = data["user"]
        except:
            return jsonify({"error": "Token is invalid"}), 401

        return func(current_user, *args, **kwargs)
    return decorated

# Protected route (example)
@app.route("/protected", methods=["GET"])
@token_required
def protected(current_user):
    return jsonify({"message": f"Hello, {current_user}!"})
app.run(debug=True)