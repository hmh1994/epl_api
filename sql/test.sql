    WITH base AS (
        SELECT fx.id AS fixture_id, fx.home_team_score, fx.away_team_score, ma.id AS match_id,
               fx.home_team_id, fx.away_team_id
        FROM fixtures_new fx
        JOIN matches_new ma ON fx.id = ma.fixture_id
        WHERE fx.id = :fixture_id
    ),
    static_data AS (
        SELECT
            ms.team_id,
            MAX(ms.possession) AS possession,
            MAX(ms.shots_total) AS shots_total,
            MAX(ms.shots_on_target) AS shots_on_target,
            MAX(ms.fouls_committed) AS fouls_committed,
            MAX(ms.passes_total) AS passes_total,
            MAX(ms.passes_accurate) AS passes_accurate,
            b.home_team_id,
            b.away_team_id
        FROM match_stats_new ms
        JOIN base b ON ms.match_id = b.match_id
        GROUP BY ms.team_id, b.home_team_id, b.away_team_id
    ),
    goals AS (
        SELECT
            'home' AS team_side,
            mhg.clock,
            p.display_name_en,
            p.display_name_kr
        FROM match_home_team_goal_association mhg
        JOIN base b ON mhg.match_id = b.match_id
        JOIN players_new p ON mhg.player_id = p.id
        UNION ALL
        SELECT
            'away' AS team_side,
            mag.clock,
            p.display_name_en,
            p.display_name_kr
        FROM match_away_team_goal_association mag
        JOIN base b ON mag.match_id = b.match_id
        JOIN players_new p ON mag.player_id = p.id
    ),
    cards AS (
        SELECT 'home' AS team_side, mhc.clock, p.display_name_en, p.display_name_kr, mhc.card_type
        FROM match_home_team_card_association mhc
        JOIN base b ON mhc.match_id = b.match_id
        JOIN players_new p ON mhc.player_id = p.id
        UNION ALL
        SELECT 'away' AS team_side, mac.clock, p.display_name_en, p.display_name_kr, mac.card_type
        FROM match_away_team_card_association mac
        JOIN base b ON mac.match_id = b.match_id
        JOIN players_new p ON mac.player_id = p.id
    )
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
        htl.home_lineup,
        atl.away_lineup,
        hts.home_substitutes,
        ats.away_substitutes,
        recent_home.home_team_recent_form,
        recent_away.away_team_recent_form,
        b.home_team_score,
        b.away_team_score,
        -- game_stat 분리 (home, away 각각 static, timeline)
        CASE WHEN b.home_team_score IS NOT NULL AND b.away_team_score IS NOT NULL THEN
            json_build_object(
                'static', json_build_object(
                    'home', json_build_object(
                        'possession', (SELECT possession FROM static_data sd WHERE sd.team_id = b.home_team_id LIMIT 1),
                        'shotsTotal', (SELECT shots_total FROM static_data sd WHERE sd.team_id = b.home_team_id LIMIT 1),
                        'shotsOnTarget', (SELECT shots_on_target FROM static_data sd WHERE sd.team_id = b.home_team_id LIMIT 1),
                        'foulsCommitted', (SELECT fouls_committed FROM static_data sd WHERE sd.team_id = b.home_team_id LIMIT 1),
                        'passesTotal', (SELECT passes_total FROM static_data sd WHERE sd.team_id = b.home_team_id LIMIT 1),
                        'passesAccurate', (SELECT passes_accurate FROM static_data sd WHERE sd.team_id = b.home_team_id LIMIT 1)
                    ),
                    'away', json_build_object(
                        'possession', (SELECT possession FROM static_data sd WHERE sd.team_id = b.away_team_id LIMIT 1),
                        'shotsTotal', (SELECT shots_total FROM static_data sd WHERE sd.team_id = b.away_team_id LIMIT 1),
                        'shotsOnTarget', (SELECT shots_on_target FROM static_data sd WHERE sd.team_id = b.away_team_id LIMIT 1),
                        'foulsCommitted', (SELECT fouls_committed FROM static_data sd WHERE sd.team_id = b.away_team_id LIMIT 1),
                        'passesTotal', (SELECT passes_total FROM static_data sd WHERE sd.team_id = b.away_team_id LIMIT 1),
                        'passesAccurate', (SELECT passes_accurate FROM static_data sd WHERE sd.team_id = b.away_team_id LIMIT 1)
                    )
                ),
                'timeline', json_build_object(
                    'goals', (SELECT json_agg(json_build_object(
                        'teamSide', team_side,
                        'clock', clock,
                        'playerDisplayNameEn', display_name_en,
                        'playerDisplayNameKr', display_name_kr
                    ) ORDER BY clock) FROM goals),
                    'cards', (SELECT json_agg(json_build_object(
                        'teamSide', team_side,
                        'clock', clock,
                        'playerDisplayNameEn', display_name_en,
                        'playerDisplayNameKr', display_name_kr,
                        'cardType', card_type
                    ) ORDER BY clock) FROM cards)
                )
            )
        ELSE NULL END AS game_stat
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
                'column', mht.column,
                'display_name_en', p.display_name_en,
                'display_name_kr', p.display_name_kr
            ) ORDER BY mht.shirt_number
        ) AS home_lineup
        FROM match_home_team_lineup_association mht
        JOIN players_new p ON p.id = mht.player_id
        WHERE mht.match_id = ma.id
    ) AS htl ON TRUE

    LEFT JOIN LATERAL (
        SELECT JSON_AGG(
            JSON_BUILD_OBJECT(
                'player_id', mat.player_id,
                'shirt_number', mat.shirt_number,
                'row', mat.row,
                'column', mat.column,
                'display_name_en', p.display_name_en,
                'display_name_kr', p.display_name_kr
            ) ORDER BY mat.shirt_number
        ) AS away_lineup
        FROM match_away_team_lineup_association mat
        JOIN players_new p ON p.id = mat.player_id
        WHERE mat.match_id = ma.id
    ) AS atl ON TRUE

    LEFT JOIN LATERAL (
        SELECT JSON_AGG(
            JSON_BUILD_OBJECT(
                'player_id', mhs.player_id,
                'shirt_number', mhs.shirt_number,
                'display_name_en', p.display_name_en,
                'display_name_kr', p.display_name_kr
            ) ORDER BY mhs.shirt_number
        ) AS home_substitutes
        FROM match_home_team_substitute_association mhs
        JOIN players_new p ON p.id = mhs.player_id
        WHERE mhs.match_id = ma.id
    ) AS hts ON TRUE

    LEFT JOIN LATERAL (
        SELECT JSON_AGG(
            JSON_BUILD_OBJECT(
                'player_id', mas.player_id,
                'shirt_number', mas.shirt_number,
                'display_name_en', p.display_name_en,
                'display_name_kr', p.display_name_kr
            ) ORDER BY mas.shirt_number
        ) AS away_substitutes
        FROM match_away_team_substitute_association mas
        JOIN players_new p ON p.id = mas.player_id
        WHERE mas.match_id = ma.id
    ) AS ats ON TRUE

    LEFT JOIN LATERAL (
        SELECT JSON_AGG(result ORDER BY kickoff_time DESC) AS home_team_recent_form
        FROM (
            SELECT 
                CASE 
                    WHEN f.home_team_id = fx.home_team_id THEN 
                        CASE 
                            WHEN f.home_team_score > f.away_team_score THEN 'W'
                            WHEN f.home_team_score = f.away_team_score THEN 'D'
                            ELSE 'L'
                        END
                    WHEN f.away_team_id = fx.home_team_id THEN 
                        CASE 
                            WHEN f.away_team_score > f.home_team_score THEN 'W'
                            WHEN f.away_team_score = f.home_team_score THEN 'D'
                            ELSE 'L'
                        END
                END AS result,
                f.kickoff_time
            FROM fixtures_new f
            WHERE (f.home_team_id = fx.home_team_id OR f.away_team_id = fx.home_team_id)
              AND f.kickoff_time < fx.kickoff_time
            ORDER BY f.kickoff_time DESC
            LIMIT 5
        ) AS recent
    ) AS recent_home ON TRUE

    LEFT JOIN LATERAL (
        SELECT JSON_AGG(result ORDER BY kickoff_time DESC) AS away_team_recent_form
        FROM (
            SELECT 
                CASE 
                    WHEN f.home_team_id = fx.away_team_id THEN 
                        CASE 
                            WHEN f.home_team_score > f.away_team_score THEN 'W'
                            WHEN f.home_team_score = f.away_team_score THEN 'D'
                            ELSE 'L'
                        END
                    WHEN f.away_team_id = fx.away_team_id THEN 
                        CASE 
                            WHEN f.away_team_score > f.home_team_score THEN 'W'
                            WHEN f.away_team_score = f.home_team_score THEN 'D'
                            ELSE 'L'
                        END
                END AS result,
                f.kickoff_time
            FROM fixtures_new f
            WHERE (f.home_team_id = fx.away_team_id OR f.away_team_id = fx.away_team_id)
              AND f.kickoff_time < fx.kickoff_time
            ORDER BY f.kickoff_time DESC
            LIMIT 5
        ) AS recent
    ) AS recent_away ON TRUE

    JOIN base b ON b.fixture_id = fx.id
    LEFT JOIN static_data sd ON (sd.team_id = b.home_team_id OR sd.team_id = b.away_team_id)
    LEFT JOIN goals ON true
    LEFT JOIN cards ON true

    WHERE fx.id = :fixture_id;