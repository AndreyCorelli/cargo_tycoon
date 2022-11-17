from sqlalchemy import PrimaryKeyConstraint, Column, DateTime, Integer
from sqlalchemy.orm import declarative_base
from geoalchemy2 import Geometry

Base = declarative_base()


class GeoLocation(Base):
    __tablename__ = "tracking_trackedgeolocation"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="tracking_gpsposition_pkey"),
    )

    id = Column(Integer)
    coordinates = Column(Geometry('POINT', 4326))
    time = Column(DateTime)
    tracker_id = Column(Integer)
