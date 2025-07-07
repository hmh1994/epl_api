WITH latest_season AS (
    SELECT s.id
    FROM seasons_new s
    JOIN competitions_new c ON s.competition_id = c.id
    WHERE c.abbreviation = 'EN_PR'
    ORDER BY s.date_end DESC
    LIMIT 1
)
SELECT * FROM (
SELECT 
	RANK() OVER (ORDER BY ps.goals DESC) AS rank,
	ps.player_id,	
	p.display_name_en AS player_name_en,
	p.display_name_kr AS player_name_kr,
	p.photo_url as player_img,
	ps.team_id, 
	t.name_en AS team_name_en,
	t.name_kr AS team_name_kr, 
	t.icon_url AS team_icon,
	ps.goals,
    'goal' AS category
FROM player_stats_new ps
JOIN players_new p ON ps.player_id = p.id
JOIN teams_new t ON ps.team_id = t.id
WHERE ps.season_id = (SELECT id FROM latest_season)
LIMIT 5) as goal_ranks

UNION ALL
select * from (
SELECT 
	RANK() OVER (ORDER BY ps.assists DESC) AS rank,
	ps.player_id,	
	p.display_name_en AS player_name_en,
	p.display_name_kr AS player_name_kr,
	p.photo_url as player_img,
	ps.team_id, 
	t.name_en AS team_name_en,
	t.name_kr AS team_name_kr, 
	t.icon_url AS team_icon,
	ps.assists,
    'assist' AS category
FROM player_stats_new ps
JOIN players_new p ON ps.player_id = p.id
JOIN teams_new t ON ps.team_id = t.id
WHERE ps.season_id = (SELECT id FROM latest_season)
LIMIT 5
) as assist_ranks