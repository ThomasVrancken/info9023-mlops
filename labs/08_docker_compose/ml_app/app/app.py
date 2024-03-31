from flask import Flask, render_template, request, redirect, url_for
from models import predict_sentiment
from ../app/database import add_sentence, get_past_sentences
from sqlalchemy import create_engine

app = Flask(__name__)

# Database connection details (adjust connection string and credentials)
DATABASE_URL = "postgresql://user:password@database:5432/sentiment_db"

def connect_to_database():
    engine = create_engine(DATABASE_URL)
    return engine

@app.route("/", methods=["GET", "POST"])
def analyze_sentiment():
  if request.method == "POST":
    txt1 = request.form["txt1"]
    sentiment = predict_sentiment(txt1)
    add_sentence(txt1, sentiment)  # Save to database
    return redirect(url_for("analyze_sentiment"))  # Redirect to avoid duplicate form submission
  else:
    past_sentences = get_past_sentences()  # Get past requests from database
    return render_template("index.html", sentiment="", past_sentences=past_sentences)

if __name__ == "__main__":
  app.run(debug=True)