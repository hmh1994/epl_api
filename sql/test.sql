WITH latest_season AS (
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
    WHERE t.id = 'd7dbc5ae-ee12-46ee-80d7-4b95e49c7294'
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
      AND ps.team_id = 'd7dbc5ae-ee12-46ee-80d7-4b95e49c7294'
    GROUP BY ps.team_id
)

SELECT 
    tws.*,
    COALESCE(c.championship_seasons, ARRAY[]::text[]) AS championships,
    COALESCE(p.squad, '[]'::json) AS players
FROM team_with_stats tws
LEFT JOIN championships c ON c.team_id = tws.id
LEFT JOIN players p ON p.team_id = tws.id