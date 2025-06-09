from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Date
from sqlalchemy.dialects.postgresql import ARRAY
from lib.lib_database import Base

# ------------------------------------------------------------
# News Mapper
# ------------------------------------------------------------
class News(Base):
    __tablename__ = "news"

    authorEn = Column("author_en", String, nullable=True)
    authorKr = Column("author_kr", String, nullable=True)
    contentEn = Column("content_en", String, nullable=True)
    contentKo = Column("content_kr", String, nullable=True)
    publishDate = Column("publish_date", DateTime, nullable=True)
    newsLink = Column("url", String, nullable=True)
    source = Column("source", String, nullable=True)
    teams = Column("teams", String, nullable=True)
    newsImg = Column("thumbnail_url", String, nullable=True)
    titleEn = Column("title_en", String, nullable=True)
    titleKo = Column("title_kr", String, nullable=True)
    newsType = Column("type", String, nullable=True)
    newsId = Column("id", String, primary_key=True, index=True)
    sourceId = Column("source_id", String, nullable=True)

# ------------------------------------------------------------
# Competition Mapper
# ------------------------------------------------------------
class Competition(Base):
    __tablename__ = "competitions"

    abbr = Column("abbreviation", String, nullable=True)
    descriptEn = Column("description_en", String, nullable=True)
    descriptKr = Column("description_kr", String, nullable=True)
    leagueImg = Column("icon_url", String, nullable=True)
    leaguenameEn = Column("name_en", String, nullable=True)
    leaguenameKr = Column("name_kr", String, nullable=True)
    leaueId = Column("id", primary_key=True, index=True)
    source = Column("source", String, nullable=True)
    sourceId = Column("source_id", String, nullable=True)
    

# ------------------------------------------------------------
# Fixtures Mapper
# ------------------------------------------------------------
class Fixture(Base):
    __tablename__ = "fixtures"      

    awayId = Column("away_team_id", Integer, nullable=True)
    awayScore = Column("away_team_score", Integer, nullable=True)
    attendance = Column("attendance", Integer, nullable=True)
    clock = Column("clock", Integer, nullable=True)
    gameWeek = Column("game_week", Integer, nullable=True)
    groundId = Column("ground_id", String, nullable=True)
    homeId = Column("home_team_id", String, nullable=True)
    homeScore = Column("home_team_score", Integer, nullable=True)
    neutralGround = Column("neutral_ground", String, nullable=True)
    kickoff = Column("kickoff_time", DateTime, nullable=True)
    seasonId = Column("season_id", String, nullable=True)
    fixtureId = Column("id", String, primary_key=True, index=True)    
    source = Column("source", String, nullable=True)
    sourceId = Column("source_id", String, nullable=True)  

# ------------------------------------------------------------
# Grounds Mapper
# ------------------------------------------------------------
class Ground(Base):
    __tablename__ = "grounds"
    
    capacity = Column("capacity", Integer, nullable=True)
    cityEn = Column("city_name_en", String, nullable=True)
    cityKr = Column("city_name_kr", String, nullable=True)
    latitude = Column("location_latitude", Float, nullable=True)
    longitude = Column("location_longitude", Float, nullable=True)
    groundEn = Column("name_en", String, nullable=True)
    groundKr = Column("name_kr", String, nullable=True)
    groundId = Column("id", String, primary_key=True, index=True)
    source = Column("source", String, nullable=True)
    sourceId = Column("source_id", String, nullable=True)

# ------------------------------------------------------------
# player_stats Mapper
# ------------------------------------------------------------
class Player_stats(Base):
    __tablename__ = "player_stats"

    appear = Column("appearances", Integer, nullable = True)
    assist = Column("assists", Integer, nullable = True)
    cleansheet = Column("clean_sheets", Integer, nullable = True)
    goals = Column("goals", Integer, nullable = True)
    goalsConced = Column("goals_conceded", Integer, nullable = True)
    keyPass = Column("key_passes", Integer, nullable = True)
    num = Column("number", Integer, nullable = True)
    playerId = Column("player_id", String, nullable = True)
    save  = Column("saves", Integer, nullable = True)
    seasonId = Column("season_id", String, nullable = True)
    shot = Column("shots", Integer, nullable = True)
    tackle = Column("tackles", Integer, nullable = True)
    teamId = Column("team_id", String, nullable = True)
    statId = Column("id", String, primary_key=True, index=True)
    source = Column("source", String, nullable = True)
    sourceId = Column("source_id", String, nullable = True)

# ------------------------------------------------------------
# players Mapper
# ------------------------------------------------------------
class Player(Base):
    __tablename__ = "players"

    playerId = Column("id", String, primary_key=True, index=True)
    fullName = Column("full_name", String, nullable=True)
    nameEn = Column("display_name_en", String, nullable=True)
    nameKr = Column("display_name_kr", String, nullable=True)
    birthDate = Column("birth_date", DateTime, nullable=True)
    birthPlace = Column("birth_place", String, nullable=True)
    CountryEn = Column("birth_country_en", String, nullable=True)
    CountryKr = Column("birth_country_kr", String, nullable=True)
    CountryIconUrl = Column("birth_country_flag_icon_url", String, nullable=True)
    height = Column("height", Integer, nullable=True)
    weight = Column("weight", Integer, nullable=True)
    position = Column("position", String, nullable=True)
    positionInfoEn = Column("position_info_en", String, nullable=True)
    positionInfoKr = Column("position_info_kr", String, nullable=True)
    nationalTeam = Column("national_team", String, nullable=True)
    playerImg = Column("photo_url", String, nullable=True)
    source = Column("source", String, nullable=True)
    sourceId = Column("source_id", String, nullable=True) 

# ------------------------------------------------------------
# Seasons Mapper
# ------------------------------------------------------------
class Season(Base):
    __tablename__ = "seasons"

    abbr = Column("abbreviation", String, nullable=True)
    competitionId = Column("competition_id", String, nullable=True)
    dateEnd = Column("date_end", DateTime, nullable=True)
    dateStart = Column("date_start", DateTime, nullable=True)
    yearEnd = Column("year_end", Integer, nullable=True)
    yearStart = Column("year_start", Integer, nullable=True)
    seasonId = Column("id", String, primary_key=True, index=True)
    source = Column("source", String, nullable=True)
    sourceId = Column("source_id", String, nullable=True)

# ------------------------------------------------------------
# team_stats Mapper
# ------------------------------------------------------------

class TeamStats(Base):
    __tablename__ = "team_stats"

    awayCumulativePoints = Column("away_cumulative_points", ARRAY(Integer), nullable=True)
    awayFixtures = Column("away_fixtures", ARRAY(String), nullable=True)
    awayGoalsAgainst = Column("away_goals_against", Integer, nullable=True)
    awayGoalsFor = Column("away_goals_for", Integer, nullable=True)
    awayGoalsDifference = Column("away_goals_difference", Integer, nullable=True)
    awayMatches = Column("away_matches", Integer, nullable=True)
    awayMatchesDrawn = Column("away_matches_drawn", Integer, nullable=True)
    awayMatchesLost = Column("away_matches_lost", Integer, nullable=True)
    awayMatchesWon = Column("away_matches_won", Integer, nullable=True)
    awayPoints = Column("away_points", Integer, nullable=True)
    awayPositions = Column("away_positions", Integer, nullable=True)
    groundId = Column("ground_id", String, nullable=True)
    homeCumulativePoints = Column("home_cumulative_points", ARRAY(Integer), nullable=True)
    homeFixtures = Column("home_fixtures", ARRAY(String), nullable=True)
    homeGoalsAgainst = Column("home_goals_against", Integer, nullable=True)
    homeGoalsFor = Column("home_goals_for", Integer, nullable=True)
    homeGoalsDifference = Column("home_goals_difference", Integer, nullable=True)
    homeMatches = Column("home_matches", Integer, nullable=True)
    homeMatchesDrawn = Column("home_matches_drawn", Integer, nullable=True)
    homeMatchesLost = Column("home_matches_lost", Integer, nullable=True)
    homeMatchesWon = Column("home_matches_won", Integer, nullable=True)
    homePoints = Column("home_points", Integer, nullable=True)
    homePositions = Column("home_positions", Integer, nullable=True)
    CumulativePoints = Column("overall_cumulative_points", ARRAY(Integer), nullable=True)
    Fixtures = Column("overall_fixtures", ARRAY(String), nullable=True)
    GoalsAgainst = Column("overall_goals_against", Integer, nullable=True)
    GoalsFor = Column("overall_goals_for", Integer, nullable=True)
    GoalsDifference = Column("overall_goals_difference", Integer, nullable=True)
    Matches = Column("overall_matches", Integer, nullable=True)
    MatchesDrawn = Column("overall_matches_drawn", Integer, nullable=True)
    MatchesLost = Column("overall_matches_lost", Integer, nullable=True)
    MatchesWon = Column("overall_matches_won", Integer, nullable=True)
    Points = Column("overall_points", Integer, nullable=True)
    Position = Column("overall_position", Integer, nullable=True)
    seasonId = Column("season_id", String, nullable=True)
    teamId = Column("team_id", String, nullable=True)
    statId = Column("id", String, primary_key=True, index=True)
    source = Column("source", String, nullable=True)
    sourceId = Column("source_id", String, nullable=True)

# ------------------------------------------------------------
# teams Mapper
# ------------------------------------------------------------

class Team(Base):
    __tablename__ = "teams"

    abbr = Column("abbreviation", String, nullable=True)
    iconUrl = Column("icon_url", String, nullable=True)
    nameEn = Column("name_en", String, nullable=True)
    nameKr = Column("name_kr", String, nullable=True)
    shortNameEn = Column("short_name_en", String, nullable=True)
    shortNameKr = Column("short_name_kr", String, nullable=True)
    teamId = Column("id", String, primary_key=True, index=True)
    source = Column("source", String, nullable=True)
    sourceId = Column("source_id", String, nullable=True)
    