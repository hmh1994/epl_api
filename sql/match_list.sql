WITH latest_season AS (
    SELECT s.id
    FROM seasons_new s
    JOIN competitions_new c ON s.competition_id = c.id
    WHERE c.abbreviation = 'EN_PR'
    ORDER BY s.date_end DESC
    LIMIT 1
)
SELECT 
	fx.id,
	fx.kickoff_time,
	ht.id as home_team_id, 
	ht.name_en as home_team_en,
	ht.name_kr as home_team_kr,
	ht.short_name_en as short_home_team_en,
	ht.short_name_kr as short_home_team_kr,
	ht.icon_url as home_team_img,
	fx.home_team_score,
	at.id as away_team_id, 
	at.name_en as away_team_en,
	at.name_kr as away_team_kr,
	at.short_name_en as short_away_team_en,
	at.short_name_kr as short_away_team_kr,
	at.icon_url as away_team_img,	
	fx.away_team_score		
	
FROM fixtures_new fx
JOIN teams_new ht ON fx.home_team_id = ht.id
JOIN teams_new at ON fx.away_team_id = at.id
WHERE fx.season_id = (SELECT id FROM latest_season)
ORDER BY fx.kickoff_time DESC