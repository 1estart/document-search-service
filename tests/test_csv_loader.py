import pytest
import csv
import ast
from datetime import datetime
from io import StringIO

SAMPLE_CSV_DATA = """text,created_date,rubrics
"Слив информации на пассивки:
• Булл (Блокировка боли)
• Джесси (Массовый шок)
Включай уведомления чтобы не пропускать много полезной информации! ✅",2019-07-25 12:42:13,"['VK-1603736028819866', 'VK-11879320040', 'VK-63192684938']"
"🎁 Конкурс на НОВЫЙ СКИН ‼️
Условия:
- Like ❤
- Репост 📣",2019-05-31 17:18:42,"['VK-1603736028819866', 'VK-95883495386']"
"""

@pytest.fixture
def parsed_posts():
    f = StringIO(SAMPLE_CSV_DATA)
    reader = csv.DictReader(f)
    
    posts = []
    for row in reader:
        try:
            rubrics = ast.literal_eval(row['rubrics'])
        except (ValueError, SyntaxError):
            rubrics = []
            
        created_date = datetime.strptime(row['created_date'], '%Y-%m-%d %H:%M:%S')
        
        posts.append({
            'text': row['text'],
            'created_date': created_date,
            'rubrics': rubrics
        })
        
    return posts

@pytest.fixture
def mock_database():
    class MockDB:
        def __init__(self):
            self.storage = []
            
        def add_post(self, post_data):
            self.storage.append(post_data)
            
        def count(self):
            return len(self.storage)

    db = MockDB()
    yield db
    db.storage.clear()

def test_add_posts_to_database(parsed_posts, mock_database):
    for post in parsed_posts:
        mock_database.add_post(post)
        
    assert mock_database.count() == 2
    assert isinstance(mock_database.storage[0]['rubrics'], list)
    assert 'VK-1603736028819866' in mock_database.storage[0]['rubrics']
    assert "Булл" in mock_database.storage[0]['text']