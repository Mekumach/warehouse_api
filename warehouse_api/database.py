from sqlmodel import create_engine, Session, SQLModel

postgres_url = "postgresql://postgres:Fy.nf@db:5432/postgres"
engine = create_engine(postgres_url, echo=False)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
