"""
Uploads a bunch of junk test data to the orm database
"""
import traptracker.orm as orm
from traptracker.orm import Line, Trap, Catch, Animal, User, create_hashed_line


def pushData(bits):
    sess = orm.get_session()
    dataList = []  # A list of all objects to add to the database

    if bits[0] == "1":
        dataList.extend([create_hashed_line("Manatawu Gorge", "password", "!s0meth@ng", 3, 2, 4),
                         User(1, 1), User(1, 2),
                         create_hashed_line("Kaimais", "UPPERCASE", "whatsup?", 1, 2, 3),
                         User(2, 1), User(2, 2)])

    if bits[1] == "1":
        dataList.extend([Trap(-40.311121, 175.777068, 1, 1, 1),
                         Trap(-40.311694, 175.778506, 1, 2, 0),
                         Trap(-37.801914, 175.998381, 2, 1, 0),
                         Trap(-40.312443, 175.779098, 1, 3, 0),
                         Trap(-40.312435, 175.780965, 1, 4, 1),
                         Trap(-37.799744, 175.997491, 2, 2, 0)])

    if bits[2] == "1":
        dataList.extend([Catch(1, 1, 1474533347),
                         Catch(6, 3, 1474544443),
                         Catch(3, 1, 1474533375),
                         Catch(2, 4, 1474533379),
                         Catch(3, 2, 1475798405),
                         Catch(6, 2, 1475798405),
                         Catch(6, 4, 1476059954)])

    if bits[3] == "1":
        empty = Animal("Empty")
        empty.id = 0

        dataList.extend([empty,
                         Animal("Rat"),
                         Animal("Stoat"),
                         Animal("Hedgehog"),
                         Animal("Cat")])

    for ob in dataList:
        sess.add(ob)
    sess.commit()


def wipeDatabase(bits="1111"):
    sess = orm.get_session()

    if bits[0] == "1":
        sess.query(Line).delete()
        sess.query(User).delete()

    if bits[0] == "1":
        sess.query(Trap).delete()

    if bits[0] == "1":
        sess.query(Catch).delete()

    if bits[0] == "1":
        sess.query(Animal).delete()

    sess.commit()
    sess.close()


if __name__ == '__main__':
    pushData("1111")
