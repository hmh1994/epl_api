# sample_data.py

# sample_data.py

# 대회 정보
competitions = [
    {"id": 1, "name": "English Premier League", "country": "England"}
]

# 시즌 정보
seasons = [
    {"id": 1, "year": "92/93"},
    {"id": 2, "year": "24/25"}
]

# 경기장 정보
grounds = [
    {"id": 1, "name": "Old Trafford", "city": "Manchester"},
    {"id": 2, "name": "Anfield", "city": "Liverpool"}
]

# 팀 정보
teams = [
    {"id": 1, "name": "Manchester United", "ground_id": 1},
    {"id": 2, "name": "Liverpool", "ground_id": 2}
]

# 선수 정보
players = [
    {"id": 1, "name": "Marcus Rashford", "team_id": 1},
    {"id": 2, "name": "Mohamed Salah", "team_id": 2}
]

# 경기 정보
fixtures = [
    {"id": 1, "home_team_id": 1, "away_team_id": 2, "date": "2024-05-01", "score": None}
]

# 골 기록
goals = [
    {"id": 1, "fixture_id": 1, "player_id": 1, "minute": 34},
    {"id": 2, "fixture_id": 1, "player_id": 2, "minute": 78}
]

# 순위 정보
standings = [
    {"id": 1, "round": 1, "team_id": 1, "position": 1, "points": 3},
    {"id": 2, "round": 1, "team_id": 2, "position": 2, "points": 0}
]

