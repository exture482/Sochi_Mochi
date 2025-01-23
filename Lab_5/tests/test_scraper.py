import unittest
from unittest.mock import Mock, patch, MagicMock
import os
import pandas as pd
from bs4 import BeautifulSoup
import requests
from datetime import datetime

from scraper import WeatherScraper, CLOUDINESS

class TestWeatherScraper(unittest.TestCase):
    def setUp(self):
        self.scraper = WeatherScraper()
        import pandas as pd
        self.pd = pd
        
        # Создаем тестовый HTML
        self.test_html = '''
        <table align="center" valign="top" border="0">
            <tr></tr>
            <tr></tr>
            <tr>
                <td>01</td>
                <td>20</td>
                <td>750</td>
                <td><img class="screen_icon" src="/icons/sun.png"></td>
                <td></td>
                <td>С 5 м/с</td>
                <td>15</td>
                <td>755</td>
                <td><img class="screen_icon" src="/icons/sunc.png"></td>
                <td></td>
                <td>ЮЗ 3 м/с</td>
            </tr>
        </table>
        '''
        
    def tearDown(self):
        """Очистка после тестов"""
        # Удаляем созданные файлы и директории
        for dir_name in ['dataset', 'missing_data_logs']:
            if os.path.exists(dir_name):
                import shutil
                shutil.rmtree(dir_name)
            
        # Удаляем лог-файлы
        for file in os.listdir():
            if file.endswith('.log'):
                os.remove(file)

    def test_get_cloudiness(self):
        """Тест определения облачности по изображению"""
        # Создаем тестовый HTML с изображением
        html = '<td><img class="screen_icon" src="/icons/sun.png"></td>'
        soup = BeautifulSoup(html, 'html.parser')
        cell = soup.find('td')
        
        # Проверяем распознавание разных типов облачности
        self.assertEqual(self.scraper.get_cloudiness(cell), 'Ясно')
        
        # Проверяем случай с отсутствующим изображением
        html_no_img = '<td></td>'
        soup_no_img = BeautifulSoup(html_no_img, 'html.parser')
        cell_no_img = soup_no_img.find('td')
        self.assertEqual(self.scraper.get_cloudiness(cell_no_img), 'Нет данных')

    @patch('requests.get')
    def test_get_weather_data_success(self, mock_get):
        """Тест успешного получения данных о погоде"""
        # Настраиваем мок для успешного ответа
        mock_response = Mock()
        mock_response.content = self.test_html
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        data = self.scraper.get_weather_data(2023, 1)
        
        self.assertTrue(len(data) > 0)
        self.assertEqual(len(data[0]), 9)  # Проверяем количество полей
        self.assertEqual(data[0][0], '2023-01-01')  # Проверяем дату
        self.assertEqual(data[0][1], '20')  # Проверяем температуру

    @patch('requests.get')
    def test_get_weather_data_network_error(self, mock_get):
        """Тест обработки сетевой ошибки"""
        mock_get.side_effect = requests.RequestException("Network error")
        data = self.scraper.get_weather_data(2023, 1)
        self.assertEqual(data, [])

    @patch('requests.get')
    def test_get_weather_data_invalid_html(self, mock_get):
        """Тест обработки некорректного HTML"""
        mock_response = Mock()
        mock_response.content = "<html>Invalid table</html>"
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        data = self.scraper.get_weather_data(2023, 1)
        self.assertEqual(data, [])

    def test_save_to_csv(self):
        """Тест сохранения данных в CSV"""
        test_data = [
            ['2023-01-01', '20', '750', 'Ясно', 'С 5', '15', '755', 'Малооблачно', 'ЮЗ 3']
        ]
        filename = 'test_weather.csv'
        
        self.scraper.save_to_csv(test_data, filename)
        
        # Проверяем, что файл создан
        filepath = os.path.join('dataset', filename)
        self.assertTrue(os.path.exists(filepath))
        
        # Проверяем содержимое файла
        df = pd.read_csv(filepath)
        self.assertEqual(len(df), 1)
        self.assertEqual(len(df.columns), 9)

    @patch('requests.get')
    def test_run_scraper(self, mock_get):
        """Тест полного процесса сбора данных"""
        # Настраиваем мок для ответа
        mock_response = Mock()
        mock_response.content = self.test_html
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Создаем моки для callback-функций
        progress_callback = Mock()
        status_callback = Mock()
        
        # Запускаем сбор данных
        filename = self.scraper.run(
            "01.2023", 
            "02.2023",
            progress_callback,
            status_callback
        )
        
        # Проверяем результаты
        self.assertTrue(filename.endswith('.csv'))
        self.assertTrue(os.path.exists(os.path.join('dataset', filename)))
        progress_callback.emit.assert_called()
        status_callback.emit.assert_called()

   

if __name__ == '__main__':
    unittest.main(verbosity=2)
