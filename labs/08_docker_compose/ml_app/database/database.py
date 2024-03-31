from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configure your database connection string
engine = create_engine("sqlite:///sentiment.db")  # Replace with your engine
Base = declarative_base()

class PastSentence(Base):
  __tablename__ = "past_sentences"
  id = Column(Integer, primary_key=True)
  sentence = Column(String)
  sentiment = Column(String)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

def add_sentence(sentence, sentiment):
  new_sentence = PastSentence(sentence=sentence, sentiment=sentiment)
  session.add(new_sentence)
  session.commit()

def get_past_sentences():
  return session.query(PastSentence).all()
