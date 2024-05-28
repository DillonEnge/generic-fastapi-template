from ..session import engine, metadata

metadata.reflect(bind=engine)
