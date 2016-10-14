import traptracker.orm as orm
from traptracker.orm import Line

import hashlib
import binascii


AUTH_NONE = 0
AUTH_CATCH = 1
AUTH_LINE = 2


def authenticate(line_id, password):
    """
    Authenticate an inputed password by comparing the line_id hashed password against given password

    Args:
        line_id -- Line id to compared hashed password stored in database to
        password -- Password to compared hashed password against

    Returned:
        Integer: level of authorisation, AUTH_NONE < AUTH_CATCH < AUTH_LINE
    """
    sess = orm.get_session()
    line = sess.query(Line).filter_by(id=line_id).first()
    if line is None:
        return False

    sess.close()

    hash_compare = hashlib.pbkdf2_hmac('sha1', str.encode(password), binascii.unhexlify(line.salt), 100000)

    if binascii.hexlify(hash_compare).decode("utf-8") == line.admin_password_hashed:
        return AUTH_LINE
    if binascii.hexlify(hash_compare).decode("utf-8") == line.password_hashed:
        return AUTH_CATCH
    return AUTH_NONE
