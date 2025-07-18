                WITH latest_season AS (
    SELECT s.id
    FROM seasons_new s
    JOIN competitions_new c ON s.competition_id = c.id
    WHERE c.abbreviation = 'EN_PR'
    ORDER BY s.date_end DESC
    LIMIT 1
),
ranked_teams AS (
    SELECT
        RANK() OVER (
            ORDER BY ts.overall_points DESC, ts.overall_goals_difference DESC
        ) AS rank,
        t.short_name_en,
        ts.team_id,
        ts.overall_matches,
        ts.overall_matches_won,
        ts.overall_matches_drawn,
        ts.overall_matches_lost,
        ts.overall_goals_for,
        ts.overall_goals_against,
        ts.overall_goals_difference,
        ts.overall_points,
        t.icon_url AS team_logo
    FROM team_stats_new ts
    JOIN teams_new t ON ts.team_id = t.id
    WHERE ts.season_id = (SELECT id FROM latest_season)
),
recent_results AS (
    SELECT
        CASE
            WHEN f.home_team_id = t.id THEN f.home_team_id
            WHEN f.away_team_id = t.id THEN f.away_team_id
        END AS team_id,
        f.kickoff_time AS match_time,
        CASE
            WHEN (f.home_team_id = t.id AND f.home_team_score > f.away_team_score)
              OR (f.away_team_id = t.id AND f.away_team_score > f.home_team_score) THEN 'W'
            WHEN f.home_team_score = f.away_team_score THEN 'D'
            ELSE 'L'
        END AS result
    FROM fixtures_new f
    JOIN teams_new t ON t.id IN (f.home_team_id, f.away_team_id)
    WHERE f.season_id = (SELECT id FROM latest_season)
      AND f.home_team_score IS NOT NULL
      AND f.away_team_score IS NOT NULL
),
recent_5_results AS (
    SELECT
        team_id,
        ARRAY_AGG(result ORDER BY match_time DESC) AS recent_results
    FROM (
        SELECT
            r.*,
            ROW_NUMBER() OVER (PARTITION BY team_id ORDER BY match_time DESC) AS rn
        FROM recent_results r
    ) sub
    WHERE rn <= 5
    GROUP BY team_id
)

SELECT 
    rt.rank,
    rt.short_name_en,
    rt.team_id,
    rt.team_logo,
    rt.overall_matches,
    rt.overall_matches_won,
    rt.overall_matches_drawn,
    rt.overall_matches_lost,
    rt.overall_goals_for,
    rt.overall_goals_against,
    rt.overall_goals_difference,
    rt.overall_points,
    COALESCE(r5.recent_results, '') AS recent_5_results
FROM ranked_teams rt
LEFT JOIN recent_5_results r5 ON rt.team_id = r5.team_id
ORDER BY rt.rank