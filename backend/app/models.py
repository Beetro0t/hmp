from sqlalchemy import Column, Date, Float, Integer, String

from app.db import Base


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(String, unique=True, index=True)
    sale_date = Column(Date, index=True)
    price = Column(Float)
    address = Column(String)
    suburb = Column(String, index=True)
    postcode = Column(String, index=True)
    property_type = Column(String)
    beds = Column(Integer)
    baths = Column(Integer)
    parking = Column(Integer)
    land_size_sqm = Column(Float)
    internal_size_sqm = Column(Float, nullable=True)
    lat = Column(Float, nullable=True)
    lon = Column(Float, nullable=True)
    condition = Column(String, nullable=True)
    features = Column(String, nullable=True)
