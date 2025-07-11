WITH latest_season AS (
		SELECT s.id
		FROM seasons_new s
		JOIN competitions_new c ON s.competition_id = c.id
		WHERE c.abbreviation = 'EN_PR'
		ORDER BY s.date_end DESC
		LIMIT 1
	)
	select
	p.id,
	p.display_name_en as player_name_en,
	p.display_name_kr as player_name_kr,
	p.full_name,
	p.position,
	p.position_info_en,
	p.position_info_kr,
	ps.number AS shirt_number,
	p.national_team,
	DATE_PART('year', AGE(NOW(), p.birth_date)) AS age,
	p.birth_date,
	p.birth_country_en,
	p.birth_country_kr,	
	p.height,
	p.weight,
	p.photo_url as playerImg,
	t.name_en as team_en,
	t.name_kr as team_kr,
	t.short_name_en as short_team_en,
	t.short_name_kr as short_team_kr,
	ps.appearances,
	ps.goals,
	ps.assists,
	s.abbreviation	
	from players_new p
	JOIN player_stats_new ps ON p.id = ps.player_id 
	JOIN latest_season ls ON ps.season_id = ls.id
	JOIN teams_new t ON ps.team_id = t.id
	JOIN seasons_new s ON ls.id = s.id
	WHERE p.id = '9cc8acc8-e101-4b34-8f36-42497193b789'