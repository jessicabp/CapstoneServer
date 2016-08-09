from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="traptracker",
    password="capstone",
    hostname="traptracker.mysql.pythonanywhere-services.com",
    databasename="traptracker$traptracker",
)

Base = declarative_base()

# Object defs

class Line(Base):
    __tablename__ = 'line'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))

# End Object defs

engine = create_engine(SQLALCHEMY_DATABASE_URI)

session = sessionmaker()
session.configure(bind=engine)
Base.metadata.create_all(engine)

def get_session():
    return session()
