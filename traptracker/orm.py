from sqlalchemy import Column, ForeignKey, Integer, String, BigInteger, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URI = "sqlite:///traptracker.db"

Base = declarative_base()

# Object defs

class Line(Base):
    __tablename__ = 'line'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True)
    animal_1 = Column(Integer, ForeignKey("animal.id"))
    animal_2 = Column(Integer, ForeignKey("animal.id"))
    animal_3 = Column(Integer, ForeignKey("animal.id"))
    password_hashed = Column(String(40))
    admin_password_hashed = Column(String(40))
    salt = Column(String(40))

    def __init__(self, name, password, admin_password, salt, animal_1, animal_2, animal_3):
        self.name = name
        self.password_hashed = password
        self.admin_password_hashed = admin_password
        self.salt = salt
        self.animal_1 = animal_1
        self.animal_2 = animal_2
        self.animal_3 = animal_3

    def __repr__(self):
        return "<Line id:{} name:{}>".format(self.id, self.name)

    def getDict(self):
        return {'id': self.id,
                'name': self.name,
                'animal1': self.animal_1,
                'animal2': self.animal_2,
                'animal3': self.animal_3}


class Trap(Base):
    __tablename__ = "trap"
    id = Column(Integer, primary_key=True)
    rebait_time = Column(BigInteger)
    lat = Column(Float)
    long = Column(Float)
    line_id = Column(Integer, ForeignKey("line.id"))
    line_order = Column(Integer)
    path_side = Column(Boolean)
    broken = Column(Boolean)
    moved = Column(Boolean)

    def __init__(self, rebait_time, lat, long, line_id, line_order, path_side):
        self.rebait_time = rebait_time
        self.lat = lat
        self.long = long
        self.line_id = line_id
        self.line_order = line_order
        self.path_side = path_side
        self.broken = False
        self.moved = False

    def __repr__(self):
        return "<Trap id:{} lat:{} long:{} line_id:{} line_order:{} path_side:{}>".format(
            self.id, self.lat, self.long, self.line_id, self.line_order, self.path_side)

    def getDict(self):
        return {'id': self.id,
                'rebaitTime': self.rebait_time,
                'latitude': self.lat,
                'longitude': self.long,
                'lineId': self.line_id,
                'number': self.line_order,
                'side': self.path_side,
                'broken': self.broken,
                'moved': self.moved}


class Catch(Base):
    __tablename__ = "catch"
    id = Column(Integer, primary_key=True)
    trap_id = Column(Integer, ForeignKey("trap.id"))
    animal_id = Column(Integer, ForeignKey("animal.id"))
    animal = relationship("Animal")
    time = Column(BigInteger)

    def __init__(self, trap_id, animal_id, time):
        self.trap_id = trap_id
        self.animal_id = animal_id
        self.time = time

    def __repr__(self):
        return "<Catch id:{} trap_id:{} animal_id:{} time:{}>".format(
            self.id, self.trap_id, self.animal_id, self.time)

    def getDict(self):
        return {'id': self.id,
                'trapId': self.trap_id,
                'animalId': self.animal_id,
                'time': self.time}


class Animal(Base):
    __tablename__ = "animal"
    id = Column(Integer, primary_key=True)
    name = Column(String(30))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Animal id:{} name:{}".format(self.id, self.name)

    def getDict(self):
        return {"id": self.id, "name": self.name}


class Image(Base):
    __tablename__ = "image"
    id = Column(Integer, primary_key=True)
    catch_id = Column(Integer, ForeignKey("catch.id"))
    url = Column(String(100))

    def __init__(self, url):
        self.url = url

    def __repr__(self):
        return "<Image id:{} catch_id:{} url:{}>".format(self.id, self.catch_id, self.url)


# End Object defs

engine = create_engine(SQLALCHEMY_DATABASE_URI)

session = sessionmaker()
session.configure(bind=engine)
Base.metadata.create_all(engine)

def get_session():
    return session()
