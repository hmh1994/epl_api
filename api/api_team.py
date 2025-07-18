from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import text 
from lib.lib_database import get_db
from lib.lib_camel import dict_to_camel_case
from lib.lib_camel import dict_to_camel_case_obj
from lib.lib_sql import load_sql

router = APIRouter(prefix="/api/v1/teams", tags=["Teams"])

@router.get("/rank")
def teamrank(db : Session = Depends(get_db)):
    sql = load_sql("team_rank.sql")
    query = text(sql)   
    result = db.execute(query).fetchall()
    return {"TeamRank" : [dict_to_camel_case(row._mapping) for row in result]}


@router.get("/rank/detail")
def teamrank_detail(db : Session = Depends(get_db)):
    sql = load_sql("team_rank_detail.sql")
    query = text(sql)   
    result = db.execute(query).fetchall()
    return {"TeamRankDetail" : [dict_to_camel_case(row._mapping) for row in result]}



@router.get("/info/{team_id}")
def teaminfo(team_id: str, db: Session = Depends(get_db)):
    sql = """WITH latest_season AS (
    SELECT s.id
    FROM seasons_new s
    JOIN competitions_new c ON s.competition_id = c.id
    WHERE c.abbreviation = 'EN_PR'
    ORDER BY s.date_end DESC
    LIMIT 1
),
team_with_stats AS (
    SELECT 
        t.id,
        t.name_en,
        t.name_kr,
        t.short_name_en,
        t.short_name_kr,
        t.icon_url AS team_logo,
        ts.overall_matches AS played,
        ts.overall_matches_won AS won,
        ts.overall_matches_drawn AS drawn,
        ts.overall_matches_lost AS lost,
        ts.overall_goals_difference AS gd,
        ts.overall_points AS points
    FROM teams_new t
    LEFT JOIN team_stats_new ts
        ON ts.team_id = t.id
       AND ts.season_id = (SELECT id FROM latest_season)
    WHERE t.id = :team_id
),
championships AS (
    SELECT 
        tca.team_id,
        ARRAY_AGG(s.abbreviation ORDER BY s.date_end) AS championship_seasons
    FROM team_championship_association tca
    JOIN seasons_new s ON s.id = tca.season_id
    GROUP BY tca.team_id
),
players AS (
    SELECT 
        ps.team_id,
        JSON_AGG(
            JSON_BUILD_OBJECT(
                'player_id', ps.player_id,
                'number', ps.number,
                'display_name_en', p.display_name_en,
                'display_name_kr', p.display_name_kr,
                'position', p.position,
                'national_team', p.national_team,
                'age', DATE_PART('year', AGE(NOW(), p.birth_date)),
                'birth_country_en', p.birth_country_en,
                'birth_country_flag_icon_url', p.birth_country_flag_icon_url,
                'photo_url', p.photo_url
            )
            ORDER BY ps.number
        ) AS squad
    FROM player_stats_new ps
    JOIN players_new p ON ps.player_id = p.id
    WHERE ps.season_id = (SELECT id FROM latest_season)
      AND ps.team_id = :team_id
    GROUP BY ps.team_id
),
recent_fixtures AS (
    SELECT 
        f.id,
        f.kickoff_time,
        f.home_team_id,
        ht.name_en AS home_team_name_en,
        ht.name_kr AS home_team_name_kr,
        f.away_team_id,
        at.name_en AS away_team_name_en,
        at.name_kr AS away_team_name_kr,
        f.home_team_score,
        f.away_team_score,
        CASE 
            WHEN f.home_team_id = :team_id THEN 'home'
            ELSE 'away'
        END AS side
    FROM fixtures_new f
    LEFT JOIN teams_new ht ON f.home_team_id = ht.id
    LEFT JOIN teams_new at ON f.away_team_id = at.id
    WHERE f.season_id = (SELECT id FROM latest_season)
      AND (f.home_team_id = :team_id OR f.away_team_id = :team_id)
      AND f.kickoff_time < NOW()
      AND f.home_team_score IS NOT NULL
      AND f.away_team_score IS NOT NULL
    ORDER BY f.kickoff_time DESC
    LIMIT 3
),
upcoming_fixtures AS (
    SELECT 
        f.id,
        f.kickoff_time,
        f.home_team_id,
        ht.name_en AS home_team_name_en,
        ht.name_kr AS home_team_name_kr,
        f.away_team_id,
        at.name_en AS away_team_name_en,
        at.name_kr AS away_team_name_kr,
        f.home_team_score,
        f.away_team_score,
        CASE 
            WHEN f.home_team_id = :team_id THEN 'home'
            ELSE 'away'
        END AS side
    FROM fixtures_new f
    LEFT JOIN teams_new ht ON f.home_team_id = ht.id
    LEFT JOIN teams_new at ON f.away_team_id = at.id
    WHERE f.season_id = (SELECT id FROM latest_season)
      AND (f.home_team_id = :team_id OR f.away_team_id = :team_id)
      AND f.kickoff_time > NOW()
    ORDER BY f.kickoff_time
    LIMIT 3
)

SELECT 
    tws.id,
    tws.name_en,
    tws.name_kr,
    tws.short_name_en,
    tws.short_name_kr,
    tws.team_logo,
    tws.played,
    tws.won,
    tws.drawn,
    tws.lost,
    tws.gd,
    tws.points,
    c.championship_seasons,
    p.squad,
    rf.recent_matches,
    uf.upcoming_matches
FROM team_with_stats tws
LEFT JOIN championships c ON c.team_id = tws.id
LEFT JOIN players p ON p.team_id = tws.id
LEFT JOIN LATERAL (
    SELECT JSON_AGG(rf ORDER BY rf.kickoff_time DESC) AS recent_matches
    FROM recent_fixtures rf
) rf ON TRUE
LEFT JOIN LATERAL (
    SELECT JSON_AGG(uf ORDER BY uf.kickoff_time ASC) AS upcoming_matches
    FROM upcoming_fixtures uf
) uf ON TRUE;
 """
    query = text(sql)
    result = db.execute(query, {"team_id": team_id}).fetchone() 

    if not result:
        return {}  

    raw_data = dict(result._mapping)
    camel_data = dict_to_camel_case_obj(raw_data)
    return camel_data