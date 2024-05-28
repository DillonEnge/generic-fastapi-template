from data_api.db import base
from sqlalchemy import Column, String  # type: ignore


def test_tablename_simple() -> None:
    """Check the tablename generated from simple class name."""

    class Test(base.Base):
        id = Column(String, primary_key=True)

    assert Test.__tablename__ == "test"


def test_tablename_complex() -> None:
    """Check the tablename generated from a more complex class name."""

    class ALongerTableName(base.Base):
        id = Column(String, primary_key=True)

    assert ALongerTableName.__tablename__ == "a_longer_table_name"
