"""
Uploads a bunch of junk test data to the orm database
"""
import traptracker.orm as orm
from traptracker.orm import Trap, Catch, Animal, User, create_hashed_line


def pushData(bitAdd):
    sess = orm.get_session()
    dataList = []  # A list of all objects to add to the database

    if len(bitAdd) != 4 or bitAdd == "0000":
        return None

    if bitAdd[0] == "1":
        dataList.extend([create_hashed_line("Manatawu Gorge", "password", "!s0meth@ng", 3, 2, 4),
                         User(1, 1), User(1, 2),
                         create_hashed_line("Kaimais", "UPPERCASE", "whatsup?", 1, 2, 3),
                         User(2, 1), User(2, 2)])

    if bitAdd[1] == "1":
        dataList.extend([Trap(1474530992, -40.311121, 175.777068, 1, 1, 1),
                         Trap(1474532872, -40.311694, 175.778506, 1, 2, 0),
                         Trap(1474533206, -37.801914, 175.998381, 2, 1, 0),
                         Trap(1474533196, -40.312443, 175.779098, 1, 3, 0),
                         Trap(1474533201, -40.312435, 175.780965, 1, 4, 1),
                         Trap(1474533212, -37.799744, 175.997491, 2, 2, 0)])

    if bitAdd[2] == "1":
        dataList.extend([Catch(1, 1, 1474533347),
                         Catch(6, 3, 1474544443),
                         Catch(3, 1, 1474533375),
                         Catch(2, 4, 1474533379),
                         Catch(3, 2, 1475798405),
                         Catch(6, 2, 1475798405),
                         Catch(6, 4, 1476059954)])

    if bitAdd[3] == "1":
        dataList.extend([Animal("Rat"),
                         Animal("Stoat"),
                         Animal("Hedgehog"),
                         Animal("Cat")])

    for ob in dataList:
        sess.add(ob)
    sess.commit()


if __name__ == '__main__':
    pushData("1111")
