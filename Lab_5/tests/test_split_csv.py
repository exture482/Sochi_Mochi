import unittest
import pandas as pd
import os
from unittest.mock import patch
import shutil
from datetime import datetime, timedelta

from split_csv import split_csv, split_by_week, split_by_year

class TestSplitCSV(unittest.TestCase):
    def setUp(self):
        self.valid_data = pd.DataFrame({
            'Дата': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-02-01', '2025-01-01'],
            'Температура': [20, 22, 21, 23, 22],
            'Влажность': [50, 55, 52, 53, 51]
        })
        
        # Создаем тестовый DataFrame с некорректными датами
        self.invalid_data = pd.DataFrame({
            'Дата': ['not-a-date', '2024-01-02', '2024-01-03'],
            'Температура': [20, 22, 21],
            'Влажность': [50, 55, 52]
        })
        
        # Создаем тестовые файлы
        self.valid_csv = "valid_test.csv"
        self.invalid_csv = "invalid_test.csv"
        self.nonexistent_csv = "nonexistent.csv"
        
        self.valid_data.to_csv(self.valid_csv, index=False)
        self.invalid_data.to_csv(self.invalid_csv, index=False)

    def tearDown(self):
        """Очистка после тестов"""
        # Удаляем тестовые файлы
        for file in [self.valid_csv, self.invalid_csv]:
            if os.path.exists(file):
                os.remove(file)
        
        # Удаляем созданные директории
        for dir_name in ['dataset']:
            if os.path.exists(dir_name):
                shutil.rmtree(dir_name)

    # ТЕСТЫ ДЛЯ split_csv
    def test_split_csv_success(self):
        """Тест успешного разделения CSV на X и Y"""
        with patch('builtins.print') as mock_print:
            split_csv(self.valid_csv)
            
            # Проверяем создание директории
            output_dir = os.path.join('dataset', 'split_csv', 'valid_test')
            self.assertTrue(os.path.exists(output_dir))
            
            # Проверяем создание файлов X.csv и Y.csv
            self.assertTrue(os.path.exists(os.path.join(output_dir, 'X.csv')))
            self.assertTrue(os.path.exists(os.path.join(output_dir, 'Y.csv')))
            
            # Проверяем сообщение об успехе
            mock_print.assert_called_with(
                f"Файлы X.csv и Y.csv успешно созданы в папке {output_dir}."
            )

    def test_split_csv_nonexistent_file(self):
        """Тест обработки несуществующего файла"""
        with patch('builtins.print') as mock_print:
            split_csv(self.nonexistent_csv)
            mock_print.assert_called_with(
                f"Файл {self.nonexistent_csv} не найден."
            )

    def test_split_csv_invalid_dates(self):
        """Тест обработки файла с некорректными датами"""
        with patch('builtins.print') as mock_print:
            split_csv(self.invalid_csv)
            mock_print.assert_called_with(
                "Первый столбец не содержит корректные даты в формате ISO 8601."
            )

    # ТЕСТЫ ДЛЯ split_by_week
    def test_split_by_week_success(self):
        """Тест успешного разделения по неделям"""
        with patch('builtins.print') as mock_print:
            split_by_week(self.valid_csv)
            
            # Проверяем создание директории
            output_dir = os.path.join('dataset', 'weekly_data', 'valid_test')
            self.assertTrue(os.path.exists(output_dir))
            
            # Проверяем создание файлов для каждой недели
            files = os.listdir(output_dir)
            self.assertTrue(len(files) > 0)
            self.assertTrue(all(f.endswith('.csv') for f in files))

    def test_split_by_week_nonexistent_file(self):
        """Тест обработки несуществующего файла при разделении по неделям"""
        with patch('builtins.print') as mock_print:
            split_by_week(self.nonexistent_csv)
            mock_print.assert_called_with(
                f"Файл {self.nonexistent_csv} не найден."
            )

    # ТЕСТЫ ДЛЯ split_by_year
    def test_split_by_year_success(self):
        """Тест успешного разделения по годам"""
        with patch('builtins.print') as mock_print:
            split_by_year(self.valid_csv)
            
            # Проверяем создание директории
            output_dir = os.path.join('dataset', 'yearly_data', 'valid_test')
            self.assertTrue(os.path.exists(output_dir))
            
            # Проверяем создание файлов для каждого года
            files = os.listdir(output_dir)
            self.assertEqual(len(files), 2)  # Должно быть 2 файла (2024 и 2025)

    def test_split_by_year_nonexistent_file(self):
        """Тест обработки несуществующего файла при разделении по годам"""
        with patch('builtins.print') as mock_print:
            split_by_year(self.nonexistent_csv)
            mock_print.assert_called_with(
                f"Файл {self.nonexistent_csv} не найден."
            )

    # ПРОВЕРКА СОДЕРЖИМОГО ФАЙЛОВ
    def test_split_csv_content(self):
        """Тест правильности разделения данных"""
        split_csv(self.valid_csv)
        output_dir = os.path.join('dataset', 'split_csv', 'valid_test')
        
        # Проверяем X.csv
        x_df = pd.read_csv(os.path.join(output_dir, 'X.csv'))
        self.assertEqual(list(x_df.columns), ['Date'])
        self.assertEqual(len(x_df), len(self.valid_data))
        
        # Проверяем Y.csv
        y_df = pd.read_csv(os.path.join(output_dir, 'Y.csv'))
        self.assertEqual(list(y_df.columns), ['Температура', 'Влажность'])
        self.assertEqual(len(y_df), len(self.valid_data))

    # ТЕСТ ОБРАБОТКИ ОШИБОК
    @patch('os.makedirs')
    def test_file_write_error(self, mock_makedirs):
        """Тест обработки ошибки при записи файла"""
        # Настраиваем мок для создания директории
        mock_makedirs.side_effect = PermissionError("Permission denied")

        with patch('builtins.print') as mock_print:
            try:
                split_csv(self.valid_csv)
            except PermissionError:
                # Проверяем, что была попытка создать директорию
                mock_makedirs.assert_called()
                self.assertTrue(True, "Ожидаемая ошибка доступа")
                return
        
            self.fail("Должна была возникнуть PermissionError")

   
    def test_invalid_csv_format(self):
        """Тест обработки файла с некорректным форматом CSV"""
        # Создаем файл с неправильной структурой
        invalid_df = pd.DataFrame({
            'НеДата': ['not a date'],
            'Значение': [1]
        })
        invalid_csv = "invalid_format.csv"
        invalid_df.to_csv(invalid_csv, index=False)

        try:
            with patch('builtins.print') as mock_print:
                split_csv(invalid_csv)
            
                # Проверяем, что был вызов print с сообщением о проблеме с датами
                calls = [call.args[0] for call in mock_print.call_args_list]
                self.assertTrue(
                    any("Первый столбец не содержит корректные даты" in str(call) 
                        for call in calls),
                    "Должно быть сообщение о некорректных датах"
                )
        finally:
            if os.path.exists(invalid_csv):
                os.remove(invalid_csv)


    def test_special_characters_in_filename(self):
        """Тест обработки специальных символов в имени файла"""
        special_name = "test@#$%^.csv"
        self.valid_data.to_csv(special_name, index=False)
    
        split_csv(special_name)
    
        # Проверяем, что файлы созданы с корректными именами
        base_name = os.path.splitext(special_name)[0]
        output_dir = os.path.join('dataset', 'split_csv', base_name)
        self.assertTrue(os.path.exists(output_dir))
    
        os.remove(special_name)

    def tearDown(self):
        """Очистка после каждого теста"""
        super().tearDown()
        # Дополнительная очистка тестовых файлов
        test_files = [
            'empty_test.csv',
            'invalid_format.csv',
            self.valid_csv,
            self.invalid_csv
        ]
        for file in test_files:
            if os.path.exists(file):
                try:
                    os.remove(file)
                except:
                    pass

        # Очистка созданных директорий
        for dir_path in ['dataset']:
            if os.path.exists(dir_path):
                try:
                    shutil.rmtree(dir_path)
                except:
                    pass

if __name__ == '__main__':
    unittest.main(verbosity=2)
