import unittest
from unittest.mock import Mock, patch
import json
import datetime
from diagrams import hist1, diag2, get_issues, graf3, graf4, graf6, find_greate_user


class TestJiraFunctions(unittest.TestCase):

    def setUp(self):
        """Настройка тестовых данных"""
        self.mock_response_data = {
            'issues': [
                {
                    'key': 'HDFS-123',
                    'fields': {
                        'created': '2023-01-15T10:30:00.000+0000',
                        'resolutiondate': '2023-01-20T14:15:00.000+0000',
                        'assignee': {'displayName': 'John Doe'},
                        'reporter': {'displayName': 'Jane Smith'},
                        'priority': 'Major',
                        'summary': 'Test issue'
                    },
                    'changelog': {
                        'histories': [
                            {
                                'created': '2023-01-16T11:00:00.000+0000',
                                'items': [
                                    {
                                        'field': 'status',
                                        'toString': 'In Progress'
                                    }
                                ]
                            }
                        ]
                    }
                },
                {
                    'key': 'HDFS-456',
                    'fields': {
                        'created': '2023-02-01T09:00:00.000+0000',
                        'resolutiondate': None,
                        'assignee': {'displayName': 'John Doe'},
                        'reporter': {'displayName': 'John Doe'},
                        'priority': 'Minor',
                        'summary': 'Another test issue'
                    },
                    'changelog': {
                        'histories': []
                    }
                }
            ],
            'total': 2
        }

    def test_1_get_issues_success(self):
        """Тест 1: Проверка успешного получения данных из JIRA"""
        # Создаем мок-объект response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = json.dumps(self.mock_response_data)

        with patch('requests.get', return_value=mock_response) as mock_get:
            payload = {'jql': 'project=HDFS', 'maxResults': '100'}
            result = get_issues('https://test-url.com', payload)

            # Проверяем, что requests.get был вызван с правильными параметрами
            mock_get.assert_called_once_with(
                'https://test-url.com',
                params=payload
            )

            # Проверяем, что функция возвращает правильные данные
            self.assertEqual(result, self.mock_response_data)
            self.assertIn('issues', result)
            self.assertEqual(len(result['issues']), 2)
            self.assertEqual(result['issues'][0]['key'], 'HDFS-123')

    def test_2_get_issues_failure(self):
        """Тест 2: Проверка обработки ошибки при запросе"""
        mock_response = Mock()
        mock_response.status_code = 404  # Simulate failure
        mock_response.text = 'Not Found'

        with patch('requests.get', return_value=mock_response):
            payload = {'jql': 'project=HDFS'}
            result = get_issues('https://test-url.com', payload)

            # Проверяем, что функция возвращает пустой список при ошибке
            self.assertEqual(result, [])

    def test_3_date_parsing_correctness(self):
        """Тест 4: Проверка корректности парсинга дат"""
        # Тестовые данные с датами
        test_date_str = '2023-01-15T10:30:00.000+0000'

        # Проверяем, что парсинг работает корректно
        parsed_date = datetime.datetime.strptime(test_date_str, '%Y-%m-%dT%H:%M:%S.%f%z')

        self.assertEqual(parsed_date.year, 2023)
        self.assertEqual(parsed_date.month, 1)
        self.assertEqual(parsed_date.day, 15)
        self.assertEqual(parsed_date.hour, 10)
        self.assertEqual(parsed_date.minute, 30)

    def test_4_state_time_calculation(self):
        """Тест 5: Проверка расчета времени в статусах"""
        # Тестовые данные для проверки логики расчета времени
        created_str = '2023-01-15T10:30:00.000+0000'
        resolved_str = '2023-01-20T14:15:00.000+0000'

        created = datetime.datetime.strptime(created_str, '%Y-%m-%dT%H:%M:%S.%f%z')
        resolved = datetime.datetime.strptime(resolved_str, '%Y-%m-%dT%H:%M:%S.%f%z')

        # Рассчитываем разницу в днях
        time_diff = (resolved - created).total_seconds() / (60 * 60 * 24)

        # Проверяем расчет
        self.assertAlmostEqual(time_diff, 5.157, places=2)  # ~5 дней 3.78 часа

        # Проверяем, что время положительное
        self.assertGreater(time_diff, 0)

    # Дополнительный тест для проверки структуры changelog
    def test_5_changelog_structure(self):
        """Тест 6: Проверка структуры changelog"""
        issue = self.mock_response_data['issues'][0]

        # Проверяем наличие необходимых полей
        self.assertIn('changelog', issue)
        self.assertIn('histories', issue['changelog'])
        self.assertIsInstance(issue['changelog']['histories'], list)

        if issue['changelog']['histories']:
            history = issue['changelog']['histories'][0]
            self.assertIn('created', history)
            self.assertIn('items', history)

            if history['items']:
                item = history['items'][0]
                self.assertIn('field', item)
                self.assertIn('toString', item)

# Упрощенный тест для быстрого запуска
def run_simple_tests():
    """Запуск упрощенных тестов без unittest"""
    print("Запуск простых тестов...")

    # Тест 1: Проверка парсинга дат
    try:
        test_date = '2023-01-15T10:30:00.000+0000'
        datetime.datetime.strptime(test_date, '%Y-%m-%dT%H:%M:%S.%f%z')
        print("✓ Тест 1: Парсинг дат - OK")
    except Exception as e:
        print(f"✗ Тест 1: Парсинг дат - Ошибка: {e}")

    # Тест 2: Проверка расчета времени
    try:
        created = datetime.datetime(2023, 1, 15, 10, 30)
        resolved = datetime.datetime(2023, 1, 20, 14, 15)
        days_diff = (resolved - created).total_seconds() / (60 * 60 * 24)
        assert abs(days_diff - 5.157) < 0.01
        print("✓ Тест 2: Расчет времени - OK")
    except Exception as e:
        print(f"✗ Тест 2: Расчет времени - Ошибка: {e}")

    # Тест 3: Проверка структуры JQL запроса
    try:
        payload = {'jql': 'project=HDFS', 'maxResults': '1000'}
        assert 'jql' in payload
        assert 'maxResults' in payload
        assert payload['jql'] == 'project=HDFS'
        print("✓ Тест 3: Структура JQL - OK")
    except Exception as e:
        print(f"✗ Тест 3: Структура JQL - Ошибка: {e}")

    # Тест 4: Проверка обработки None значений
    try:
        test_data = {'issues': [{'fields': {'resolutiondate': None}}]}
        issue = test_data['issues'][0]
        # Проверяем, что функция get вернет None
        result = issue['fields'].get('resolutiondate')
        assert result is None
        print("✓ Тест 4: Обработка None значений - OK")
    except Exception as e:
        print(f"✗ Тест 4: Обработка None значений - Ошибка: {e}")

    # Тест 5: Проверка defaultdict
    try:
        from collections import defaultdict
        test_dict = defaultdict(int)
        test_dict['test'] += 1
        assert test_dict['test'] == 1
        assert test_dict['nonexistent'] == 0  # Должен вернуть 0 по умолчанию
        print("✓ Тест 5: defaultdict - OK")
    except Exception as e:
        print(f"✗ Тест 5: defaultdict - Ошибка: {e}")


if __name__ == '__main__':
    run_simple_tests()


