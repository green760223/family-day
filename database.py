import databases
import sqlalchemy

from config import config

metadata = sqlalchemy.MetaData()

employee_table = sqlalchemy.Table(
    "employee",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("mobile", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("department", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("company", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("family_employee", sqlalchemy.Integer, default=1),
    sqlalchemy.Column("family_infant", sqlalchemy.Integer, nullable=True),
    sqlalchemy.Column("family_child", sqlalchemy.Integer, nullable=True),
    sqlalchemy.Column("family_adult", sqlalchemy.Integer, nullable=True),
    sqlalchemy.Column("family_elderly", sqlalchemy.Integer, nullable=True),
    sqlalchemy.Column("group", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("is_checked", sqlalchemy.Boolean, default=False),
    # sqlalchemy.Column("checked_in_time", sqlalchemy.DateTime, nullable=True),
    sqlalchemy.Column("checked_in_time", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("is_deleted", sqlalchemy.Boolean, default=False),
)

notifications_table = sqlalchemy.Table(
    "notification",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("title", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("message", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("created_at", sqlalchemy.String, nullable=False),
)

connect_args = {"check_same_thread": False} if "sqlite" in config.DATABASE_URL else {}
engine = sqlalchemy.create_engine(config.DATABASE_URL, connect_args=connect_args)

metadata.create_all(engine)

db_args = {"min_size": 5, "max_size": 30} if "postgres" in config.DATABASE_URL else {}
database = databases.Database(
    config.DATABASE_URL, force_rollback=config.DB_FORCE_ROLLBACK, **db_args
)
