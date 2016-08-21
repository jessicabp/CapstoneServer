from sqlalchemy import Column, ForeignKey, Integer, String, TIMESTAMP, Boolean, Float
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
    name = Column(String(80), unique=True)
    password_hashed = Column(String(100))
    traps = relationship("Trap", back_populates="line")
    
    def __init__(self, name, password):
        self.name = name
        self.password_hashed = password
        
    def __repr__(self):
        return "<Line: %s>" % self.id
        
class Trap(Base):
    __tablename__ = "Trap"
    id = Column(Integer, primary_key=True)
    rebait_time = Column(TIMESTAMP)
    lat = Column(Float)
    long = Column(Float)
    line_id = Column(Integer, ForeignKey("line.id"))
    line = relationship("Line", back_populates="traps")
    line_order = Column(Integer)
    path_side = Column(Integer)
    broken = Column(Boolean)
    moved = Column(Boolean)
    catches = relationship("Catch", back_populates="trap")

    def __init__(self, rebait_time, location, line_id, line_order, path_side, broken, moved):
        self.rebait_time = rebait_time
        self.location = location
        self.line_id = line_id
        self.line_order = line_order
        self.path_side = path_side
        self.broken = broken
        self.moved = moved

    def __repr__(self):
        return "<Trap: %s>" % self.id


class Catch(Base):
    __tablename__ = "Catch"
    id = Column(Integer, primary_key=True)
    trap_id = Column(Integer, ForeignKey("trap.id"))
    trap = relationship("Trap", back_populates="catches")
    animal_id = Column(Integer, ForeignKey("animal.id"))
    animal = relationship("Animal", back_populates="catches")
    time = Column(TIMESTAMP)
    image_id = Column(Integer)
    image = relationship("Image", back_populates="catches")

    def __init__(self):
        pass

    def __repr__(self):
        return "<Catch: %s>" % self.id


class Animal(Base):
    __tablename__ = "Animal"
    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    catches = relationship("Catch", back_populates="animal")

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Animal: %s>" % self.id

class Image(Base):
    __tablename__ = "Image"
    id = Column(Integer, primary_key=True)
    url = Column(String(100))
    catches = relationship("Catch", back_populates="image")

    def __init__(self, url):
        self.url = url

    def __repr__(self):
        return "<Image: %s>" % self.id


# End Object defs

engine = create_engine(SQLALCHEMY_DATABASE_URI)

session = sessionmaker()
session.configure(bind=engine)
Base.metadata.create_all(engine)

def get_session():
    return session()
