from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "Welcome to the Simple Flask App!"

@app.route("/health")
def health():
    return {"status": "healthy"}
