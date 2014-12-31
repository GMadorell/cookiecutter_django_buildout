
from aldjemy.core import get_engine
from sqlalchemy.orm import sessionmaker


def AldjemySession():
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()
