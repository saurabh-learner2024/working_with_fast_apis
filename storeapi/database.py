import databases
import sqlalchemy
from storeapi.config import config

# Define SQLAlchemy metadata instance to hold table definitions
metadata = sqlalchemy.MetaData()

# Define the posts table
post_table = sqlalchemy.Table(
    "posts",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),  # Primary key column
    sqlalchemy.Column("body", sqlalchemy.String)  # Body column for post content
)


user_table = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("email", sqlalchemy.String, unique=True),
    sqlalchemy.Column("password", sqlalchemy.String)
)


# Define the comments table
comment_table = sqlalchemy.Table(
    "comments",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),  # Primary key column
    sqlalchemy.Column("body", sqlalchemy.String),  # Body column for comment content
    sqlalchemy.Column("post_id", sqlalchemy.ForeignKey("posts.id"), nullable=False)  # Foreign key referencing posts table
)

# Create an SQLAlchemy engine using the database URL from the configuration
engine = sqlalchemy.create_engine(
    config.DATABASE_URL, connect_args={"check_same_thread": False}  # Only relevant for SQLite
)

# Create all tables in the database using the metadata
metadata.create_all(engine)

# Create a databases.Database instance for database interactions
database = databases.Database(
    config.DATABASE_URL, force_rollback=config.DB_FORCE_ROLL_BACK  # Rollback changes if DB_FORCE_ROLL_BACK is True
)
