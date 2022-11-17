from typing import List

import sqlalchemy

from sqlalchemy import PrimaryKeyConstraint, Column, DateTime, Integer, String, Boolean, select
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()
Base2 = declarative_base()


class UserModelMan(Base):
    __tablename__ = "user"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="user_pkey"),
    )

    id = Column(UUID)
    mothership_id = Column(Integer)
    email = Column(String)
    active = Column(Boolean)
    tenant = Column(String)
    permissions = Column(String)
    auth0_id = Column(String)
    name = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class UserModelAssign(Base2):
    __tablename__ = "user"
    __table_args__ = (
        PrimaryKeyConstraint("user_id", name="user_pkey"),
    )

    user_id = Column(UUID)
    mothership_id = Column(Integer)
    email = Column(String)
    active = Column(Boolean)
    roles = Column(String)  # new
    type = Column(String)  # new
    tenant = Column(String)
    name = Column(String)
    created = Column(DateTime)
    updated = Column(DateTime)
    consumed_entity_modified = Column(DateTime)  # new


class UserMapper:
    @classmethod
    def transform_user(cls, usr: UserModelMan) -> UserModelAssign:
        return UserModelAssign(
            user_id=usr.id,
            mothership_id=usr.mothership_id,
            email=usr.email,
            active=usr.active,
            roles=usr.permissions,
            type="",
            tenant=usr.tenant,
            name=usr.name,
            created=usr.created_at,
            updated=usr.updated_at,
            consumed_entity_modified=usr.updated_at
        )


class UserMigration:
    def __init__(self):
        self.users: List[UserModelMan] = []

    def migrate(self):
        self.read_users()
        self.update_missing()

    def read_users(self):
        engine = self.get_user_management_engine()
        print(f"Source DB connection established")
        query = select(UserModelMan)
        result = engine.execute(query)

        row: UserModelMan
        self.users = list(result.fetchall())

        print(f"{len(self.users)} users read")

    def update_missing(self):
        engine = self.get_carrier_assign_engine()
        query = select(UserModelAssign.user_id)
        result = engine.execute(query)
        exist_ids = {u[0] for u in result.fetchall()}
        missing_users = [u for u in self.users if u.id not in exist_ids]
        print(f"{len(missing_users)} user records are missing")

        Session = sessionmaker(engine)
        with Session() as session:
            for u in missing_users:
                new_user = UserMapper.transform_user(u)
                session.add(new_user)
            session.commit()
        print(f"Users are inserted")

    @classmethod
    def get_user_management_engine(cls):
        db_user = "usermanagement"
        db_name = "usermanagementprod"
        db_host = "usermanagementprod-postgres-prod.c8lztmzdldqw.eu-central-1.rds.amazonaws.com"
        pwrd = "JgB1FhmwXJSXrJTfoULv88IItYOLFki"
        db_uri = f"postgresql://{db_user}:{pwrd}@{db_host}:5432/{db_name}"
        engine = sqlalchemy.create_engine(db_uri)
        return engine

    @classmethod
    def get_carrier_assign_engine(cls):
        db_user = "carrierassign"
        db_name = "carrierassignprod"
        db_host = "carrierassignprod-postgres-prod.c8lztmzdldqw.eu-central-1.rds.amazonaws.com"
        pwrd = "ktNax46j9sQHWoeJDa5M:2fa"
        db_uri = f"postgresql://{db_user}:{pwrd}@{db_host}:5432/{db_name}"
        engine = sqlalchemy.create_engine(db_uri)
        return engine


if __name__ == '__main__':
    m = UserMigration()
    m.migrate()
