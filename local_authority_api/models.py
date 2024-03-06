from local_authority_api.extensions import db
from geoalchemy2 import Geometry
from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION, JSONB


class Boundaries(db.Model):
    __tablename__ = 'boundaries'
    gid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    area_code = db.Column(db.String)
    descriptio = db.Column(db.String)
    file_name = db.Column(db.String)
    number = db.Column(DOUBLE_PRECISION)
    number0 = db.Column(DOUBLE_PRECISION)
    polygon_id = db.Column(DOUBLE_PRECISION)
    unit_id = db.Column(DOUBLE_PRECISION)
    code = db.Column(db.String)
    hectares = db.Column(DOUBLE_PRECISION)
    area = db.Column(DOUBLE_PRECISION)
    type_code = db.Column(db.String)
    descript0 = db.Column(db.String)
    type_cod0 = db.Column(db.String)
    descript1 = db.Column(db.String)
    geom = db.Column(Geometry(srid=27700))
    organisation = db.relationship("Organisation", back_populates="boundary")


class Organisation(db.Model):
    __tablename__ = 'organisation'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    migrated = db.Column(db.Boolean)
    notice = db.Column(db.Boolean)
    maintenance = db.Column(db.Boolean)
    scottish = db.Column(db.Boolean)
    type_id = db.Column(db.Integer)
    historic_names = db.Column(JSONB, nullable=False)
    boundary = db.relationship("Boundaries", back_populates="organisation")
    source_information = db.relationship("SourceInformation", back_populates="organisation")
    boundaries_gid = db.Column(db.Integer, db.ForeignKey('boundaries.gid'), nullable=True)
    last_updated = db.Column(db.DateTime, nullable=True)

    def __init__(self, title, migrated, type_id, notice, scottish, maintenance, historic_names, last_updated):
        self.title = title
        self.migrated = migrated
        self.type_id = type_id
        self.notice = notice
        self.scottish = scottish
        self.maintenance = maintenance
        self.historic_names = historic_names
        self.last_updated = last_updated


class SourceInformation(db.Model):
    __tablename__ = 'source_information'
    id = db.Column(db.Integer, primary_key=True)
    source_information = db.Column(db.String, nullable=False)
    organisation_id = db.Column(db.String, db.ForeignKey('organisation.id'), nullable=False)

    organisation = db.relationship("Organisation", back_populates="source_information")


# Only allow migrated status to be updated
UPDATE_ORGANISATION_SCHEMA = {
    "type": "object",
    "properties": {
        "migrated": {"type": "boolean"},
    },
    "additionalProperties": False
}

# Only allow notice status to be updated
UPDATE_ORGANISATION_NOTICE_SCHEMA = {
    "type": "object",
    "properties": {
        "notice": {"type": "boolean"},
    },
    "additionalProperties": False
}

# Only allow maintenance status to be updated
UPDATE_ORGANISATION_MAINTENANCE_SCHEMA = {
    "type": "object",
    "properties": {
        "maintenance": {"type": "boolean"},
    },
    "additionalProperties": False
}

ORGANISATION_SOURCE_INFORMATION_SCHEMA = {
    "type": "object",
    "properties": {
        "source-information": {"type": "string"},
    },
    "required": ["source-information"],
    "additionalProperties": False
}
