from sqlalchemy import Column, Integer, String, DateTime
from database import Base

class Competition(Base):
    __tablename__ = "competitions"

    competitionId = Column("id", Integer, primary_key=True, index=True)
    abbreviation = Column(String, nullable=True)
    descriptionEn = Column("description_en", String, nullable=True)
    descriptionKr = Column("description_kr", String, nullable=True)
    iconUrl = Column("icon_url", String, nullable=True)
    nameEn = Column("name_en", String, nullable=True)
    nameKr = Column("name_kr", String, nullable=True)
    source = Column(String, nullable=True)
    sourceId = Column("source_id", String, nullable=True)

# --------------------
# Fixtures
# --------------------
class Fixture(Base):
    __tablename__ = "fixtures"

    fixtureId = Column("id", Integer, primary_key=True, index=True)
    awayTeamId = Column("away_team_id", Integer, nullable=True)
    awayTeamScore = Column("away_team_score", Integer, nullable=True)
    attendance = Column(Integer, nullable=True)
    clock = Column(String, nullable=True)
    gameWeek = Column("game_week", Integer, nullable=True)
    groundId = Column("ground_id", Integer, nullable=True)
    homeTeamId = Column("home_team_id", Integer, nullable=True)
    homeTeamScore = Column("home_team_score", Integer, nullable=True)
    neutralGround = Column("neutral_ground", Boolean, nullable=True)
    kickoffTime = Column("kickoff_time", DateTime, nullable=True)
    seasonId = Column("season_id", String, nullable=True)
    source = Column(String, nullable=True)
    sourceId = Column("source_id", String, nullable=True)

# --------------------
# Grounds
# --------------------
class Ground(Base):
    __tablename__ = "grounds"

    groundId = Column("id", Integer, primary_key=True, index=True)
    capacity = Column(Integer, nullable=True)
    cityNameEn = Column("city_name_en", String, nullable=True)
    cityNameKr = Column("city_name_kr", String, nullable=True)
    locationLatitude = Column("location_latitude", Float, nullable=True)
    locationLongitude = Column("location_longitude", Float, nullable=True)
    nameEn = Column("name_en", String, nullable=True)
    nameKr = Column("name_kr", String, nullable=True)
    source = Column(String, nullable=True)
    sourceId = Column("source_id", String, nullable=True)

# --------------------
# Seasons
# --------------------
class Season(Base):
    __tablename__ = "seasons"

    seasonId = Column("id", String, primary_key=True, index=True)
    abbreviation = Column(String, nullable=True)
    competitionId = Column("competition_id", Integer, nullable=True)
    dateStart = Column("date_start", Date, nullable=True)
    dateEnd = Column("date_end", Date, nullable=True)
    yearStart = Column("year_start", Integer, nullable=True)
    yearEnd = Column("year_end", Integer, nullable=True)
    source = Column(String, nullable=True)
    sourceId = Column("source_id", String, nullable=True)

# --------------------
# Teams
# --------------------
class Team(Base):
    __tablename__ = "teams"

    teamId = Column("id", Integer, primary_key=True, index=True)
    abbreviation = Column(String, nullable=True)
    groundId = Column("ground_id", Integer, nullable=True)
    iconUrl = Column("icon_url", String, nullable=True)
    nameEn = Column("name_en", String, nullable=True)
    nameKr = Column("name_kr", String, nullable=True)
    shortNameEn = Column("short_name_en", String, nullable=True)
    shortNameKr = Column("short_name_kr", String, nullable=True)
    source = Column(String, nullable=True)
    sourceId = Column("source_id", String, nullable=True)


class News(Base):
    __tablename__ = "news"

    newsId = Column("id", Integer, primary_key=True, index=True)
    titleEn = Column("title_en", String)
    titleKo = Column("title_kr", String)
    contentEn = Column("content_en", String)
    contentKo = Column("content_kr", String)
    newsLink = Column("url", String)
    newsImg = Column("thumbnail_url", String)
    source = Column("source", String)
    type = Column("type", String)
    publishDate = Column("publish_date", DateTime)