SELECT
            n.id AS news_id,
            n.title_en,
            n.title_kr,
            n.content_en,
            n.content_kr,
            n.thumbnail_url AS news_img,
            n.url AS news_url,
            n.author_en,
            n.author_kr,
            ARRAY_AGG(DISTINCT t.abbreviation) AS team,
            n.type,
            n.publish_date
        FROM news_new n
        LEFT JOIN news_team_association nta ON nta.news_id = n.id
        LEFT JOIN teams_new t ON t.id = nta.team_id
        GROUP BY 
        n.id, n.title_en, n.title_kr, n.content_en, n.content_kr,
        n.thumbnail_url, n.url, n.author_en, n.author_kr, n.type, n.publish_date
        ORDER BY n.publish_date DESC