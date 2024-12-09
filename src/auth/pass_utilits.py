from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    """
    Verifies password
    
    :param plain_password: Plain password
    :type plain_password: str
    :param hashed_password: Hashed password
    :type hashed_password: str
    :return: Password verification result
    :rtype: bool
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """
    Hashes password
    
    :param password: Password
    :type password: str
    :return: Hashed password
    :rtype: str
    """
    
    return pwd_context.hash(password) 