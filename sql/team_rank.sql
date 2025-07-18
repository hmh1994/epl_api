WITH latest_season AS (
    SELECT s.id
    FROM seasons_new s
    JOIN competitions_new c ON s.competition_id = c.id
    WHERE c.abbreviation = 'EN_PR'
    ORDER BY s.date_end DESC
    LIMIT 1
)
SELECT 
    RANK() OVER (
        ORDER BY ts.overall_points DESC, ts.overall_goals_difference DESC
    ) AS rank,
    t.name_en,
    t.name_kr,
    t.short_name_en,
    t.short_name_kr,
    ts.team_id,
    ts.overall_matches AS matches,
    ts.overall_matches_won AS won,
    ts.overall_matches_drawn AS drawn,
    ts.overall_matches_lost AS lost,
    ts.overall_goals_difference AS gd,
    ts.overall_points AS points,
    t.icon_url AS team_logo
FROM team_stats_new ts
JOIN teams_new t ON ts.team_id = t.id
WHERE ts.season_id = (SELECT id FROM latest_season)
ORDER BY ts.overall_points DESC, ts.overall_goals_difference DESC