from data_api.api import depends
from sqlalchemy.orm import Session


def test_get_db():
    """Get an instance of a database session from dependency generator."""

    sess = next(depends.get_db())
    assert isinstance(sess, Session)
