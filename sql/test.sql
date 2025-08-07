SELECT 
    fx.id, 
    g.name_en AS ground_name_en,
    g.name_kr AS ground_name_kr,
    g.city_name_en,
    g.city_name_kr,
    g.capacity,
    fx.kickoff_time,
    of.display_name_en AS official_name_en,
    of.display_name_kr AS official_name_kr,
    fx.home_team_id,
    s1.display_name_en AS home_team_manager_en,
    s1.display_name_kr AS home_team_manager_kr,
    ma.home_team_formation,
    fx.away_team_id,
    s2.display_name_en AS away_team_manager_en,
    s2.display_name_kr AS away_team_manager_kr,
    ma.away_team_formation,
    htl.home_lineup
FROM fixtures_new fx
JOIN matches_new ma ON fx.id = ma.fixture_id
LEFT JOIN staffs_new s1 ON ma.home_team_manager = s1.id
LEFT JOIN staffs_new s2 ON ma.away_team_manager = s2.id
LEFT JOIN grounds_new g ON fx.ground_id = g.id
LEFT JOIN officials_new of ON ma.official_main_referee_id = of.id
LEFT JOIN LATERAL (
    SELECT JSON_AGG(
        JSON_BUILD_OBJECT(
            'player_id', mht.player_id,
            'shirt_number', mht.shirt_number,
            'row', mht.row,
            'column', mht.column
        ) ORDER BY mht.shirt_number
    ) AS home_lineup
    FROM match_home_team_lineup_association mht
    WHERE mht.match_id = ma.id
) AS htl ON TRUE
WHERE fx.id = '33e09323-9d46-45e1-a734-1b2bb968afb3';
