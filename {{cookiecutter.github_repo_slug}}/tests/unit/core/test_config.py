from data_api.core import config


def test_settings_sqlalchemy_database_uri_validator_from_string() -> None:
    """Postgres DSN is specified directly via config."""

    s = config.Settings(
        postgres_host="test-host",
        postgres_port="1234",
        postgres_user="test-user",
        postgres_password="test-pw",
        postgres_db="testdb",
        sqlalchemy_database_uri="postgresql://foo:bar@127.0.0.1:9999/dbname",
    )

    assert s.sqlalchemy_database_uri == "postgresql://foo:bar@127.0.0.1:9999/dbname"


def test_settings_sqlalchemy_database_uri_validator_build_dsn() -> None:
    """Postgres DSN is built via other config parameters."""

    s = config.Settings(
        postgres_host="test-host",
        postgres_port="1234",
        postgres_user="test-user",
        postgres_password="test-pw",
        postgres_db="testdb",
    )

    assert s.sqlalchemy_database_uri == "postgresql://test-user:test-pw@test-host:1234/testdb"
