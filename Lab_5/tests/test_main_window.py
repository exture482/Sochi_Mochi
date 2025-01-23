import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from datetime import datetime


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main_window import MainWindow, ScraperThread

class TestWeather_Sochi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Создает экземпляр приложения для всех тестов"""
        cls.app = QApplication([])
        
    def setUp(self):
        """Создает новое окно для каждого теста"""
        self.window = MainWindow()
        self.test_df = pd.DataFrame({
            'Дата': pd.date_range(start='2024-01-01', periods=5),
            'Температура': [20, 22, 21, 23, 22],
            'Влажность': [50, 55, 52, 53, 51]
        })
        self.test_csv = os.path.join(os.getcwd(), "test_data.csv")
        self.test_df.to_csv(self.test_csv, index=False)

    def tearDown(self):
        """Очищает после каждого теста"""
        if os.path.exists(self.test_csv):
            os.remove(self.test_csv)
        if os.path.exists('dataset'):
            import shutil
            shutil.rmtree('dataset')
        self.window.close()

    # ТЕСТЫ БАЗОВОЙ ФУНКЦИОНАЛЬНОСТИ
    def test_initial_state(self):
        """Тест начального состояния приложения"""
        self.assertIsNone(self.window.current_file)
        self.assertIsNone(self.window.preprocessed_data)
        self.assertEqual(self.window.info_label.text(), "Выберите файл для начала работы")
        self.assertEqual(self.window.windowTitle(), "Weather_Sochi")

    def test_file_selection_success(self):
        """Тест успешного выбора файла"""
        with patch('PyQt6.QtWidgets.QFileDialog.getOpenFileName') as mock_dialog:
            mock_dialog.return_value = (self.test_csv, 'CSV Files (*.csv)')
            self.window.select_file()
            self.assertEqual(self.window.current_file, self.test_csv)
            self.assertIsNotNone(self.window.data_preview.rowCount())

    @patch('main_window.preprocess_data')
    @patch('PyQt6.QtWidgets.QFileDialog.getSaveFileName')
    def test_preprocess_data_success(self, mock_save_dialog, mock_preprocess):
        """Тест успешной предобработки данных"""
        # Настраиваем моки
        mock_preprocess.return_value = self.test_df
        mock_save_dialog.return_value = ("test.csv", "CSV Files (*.csv)")
        
        # Выполняем предобработку
        self.window.current_file = self.test_csv
        self.window.preprocess_data()
        
        # Проверяем, что предобработка была вызвана
        mock_preprocess.assert_called_once_with(self.test_csv)
        # Проверяем, что был вызван диалог сохранения
        mock_save_dialog.assert_called_once()

    def test_preprocess_without_file(self):
        """Тест предобработки без выбранного файла"""
        self.window.current_file = None
        self.window.preprocess_data()
        self.assertEqual(self.window.info_label.text(), "Сначала выберите файл")

    # ТЕСТЫ СКРАПЕРА
    def test_scraper_dialog_creation(self):
        """Тест создания диалога скрапера"""
        self.window.show_scraper_dialog()
        self.assertTrue(hasattr(self.window, 'scraper_dialog'))
        self.assertIsNotNone(self.window.start_date_input)
        self.assertIsNotNone(self.window.end_date_input)

    @patch('main_window.WeatherScraper')
    @patch('main_window.ScraperThread')
    def test_scraper_execution(self, mock_scraper_thread, mock_scraper):
        """Тест выполнения скрапера"""
        # Настраиваем окно скрапера
        self.window.show_scraper_dialog()
        self.window.start_date_input.setText("01.2024")
        self.window.end_date_input.setText("02.2024")

        # Запускаем скрапинг
        self.window.start_scraping()

        # Проверяем, что поток скрапера был создан с правильными параметрами
        mock_scraper_thread.assert_called_once_with("01.2024", "02.2024")
        # Проверяем, что поток был запущен
        self.assertTrue(mock_scraper_thread.return_value.start.called)

    # ТЕСТЫ РАЗДЕЛЕНИЯ ФАЙЛОВ
    @patch('main_window.split_csv')
    def test_split_csv_success(self, mock_split):
        """Тест успешного разделения CSV"""
        mock_split.return_value = "output_folder"
        self.window.current_file = self.test_csv
        self.window.split_csv()
        mock_split.assert_called_once_with(self.test_csv)
        self.assertIn("Данные разделены на X и Y", self.window.info_label.text())

    def test_split_csv_error(self):
        """Тест ошибки при разделении CSV"""
        self.window.current_file = None
        self.window.split_csv()
        self.assertEqual(self.window.info_label.text(), "Сначала выберите файл")

    # ТЕСТЫ РАБОТЫ С ДАТАМИ
    def test_valid_date_input(self):
        """Тест ввода корректной даты"""
        self.window.current_file = self.test_csv
        self.window.date_input.setText('2024-01-01')
        self.window.get_data_for_date()
        self.assertIn('2024-01-01', self.window.info_label.text())

    def test_invalid_date_format(self):
        """Тест ввода даты в неверном формате"""
        self.window.current_file = self.test_csv
        self.window.date_input.setText('invalid-date')
        self.window.get_data_for_date()
        self.assertIn("Ошибка в формате даты", self.window.info_label.text())

    def test_date_out_of_range(self):
        """Тест ввода даты вне диапазона данных"""
        self.window.current_file = self.test_csv
        self.window.date_input.setText('2025-12-31')
        self.window.get_data_for_date()
        self.assertIn("находится вне диапазона данных", self.window.info_label.text())

    # ТЕСТЫ ИНТЕРФЕЙСА
    def test_tab_widget_structure(self):
        """Тест структуры вкладок"""
        self.assertEqual(self.window.tab_widget.count(), 2)
        self.assertEqual(self.window.tab_widget.tabText(0), "Основные операции")
        self.assertEqual(self.window.tab_widget.tabText(1), "Анализ данных")

    def test_table_widget_initialization(self):
        """Тест инициализации таблицы"""
        self.assertIsNotNone(self.window.data_preview)
        self.assertEqual(self.window.data_preview.rowCount(), 0)
        self.assertEqual(self.window.data_preview.columnCount(), 0)

    # НОВЫЕ ТЕСТЫ ДЛЯ СКРАПЕРА
    def test_scraper_progress_update(self):
        """Тест обновления прогресса скрапера"""
        self.window.show_scraper_dialog()
        self.window.progress_bar.setValue(0)
        self.window.update_progress_bar(50)
        self.assertEqual(self.window.progress_bar.value(), 50)

    def test_scraper_status_update(self):
        """Тест обновления статуса скрапера"""
        self.window.show_scraper_dialog()
        test_status = "Обработка данных..."
        self.window.update_status_label(test_status)
        self.assertEqual(self.window.status_label.text(), test_status)

    @patch('PyQt6.QtWidgets.QMessageBox.information')
    def test_scraping_finished_success(self, mock_msg):
        """Тест успешного завершения скрапинга"""
        test_file = "test_output.csv"
        self.window.show_scraper_dialog()
        self.window.scraping_finished(test_file)
        mock_msg.assert_called_once()
        self.assertEqual(self.window.current_file, 
                        os.path.join(os.getcwd(), 'dataset', test_file))

    @patch('PyQt6.QtWidgets.QMessageBox.warning')
    def test_scraping_finished_failure(self, mock_msg):
        """Тест неудачного завершения скрапинга"""
        self.window.show_scraper_dialog()
        self.window.scraping_finished("")
        mock_msg.assert_called_once()

    # ТЕСТЫ ВАЛИДАЦИИ ДАННЫХ
    def test_invalid_date_range_scraper(self):
        """Тест валидации диапазона дат в скрапере"""
        self.window.show_scraper_dialog()
        self.window.start_date_input.setText("12.2024")
        self.window.end_date_input.setText("01.2024")
        
        with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning:
            self.window.start_scraping()
            mock_warning.assert_called_once()

    def test_invalid_date_format_scraper(self):
        """Тест некорректного формата даты в скрапере"""
        self.window.show_scraper_dialog()
        self.window.start_date_input.setText("invalid")
        self.window.end_date_input.setText("02.2024")
        
        with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning:
            self.window.start_scraping()
            mock_warning.assert_called_once()

    # ТЕСТЫ СОХРАНЕНИЯ И ЗАГРУЗКИ
    @patch('pandas.DataFrame.to_csv')
    @patch('PyQt6.QtWidgets.QFileDialog.getSaveFileName')
    def test_save_preprocessed_data_error(self, mock_save_dialog, mock_to_csv):
        """Тест ошибки при сохранении предобработанных данных"""
        # Настраиваем диалоговое окно
        mock_save_dialog.return_value = ("test.csv", "CSV Files (*.csv)")
    
        # Создаем тестовый DataFrame
        test_df = pd.DataFrame({
            'Дата': ['2024-01-01'],
            'Значение': [1]
        })
    
        # Настраиваем, чтобы to_csv вызывал исключение
        mock_to_csv.side_effect = IOError("Ошибка сохранения")
    
        # Устанавливаем тестовые данные
        self.window.preprocessed_data = test_df
    
        # Сохраняем исходный текст метки
        original_text = self.window.info_label.text()
    
        # Пробуем сохранить данные
        self.window.save_preprocessed_data()
    
        # Проверяем, что текст метки изменился
        self.assertNotEqual(self.window.info_label.text(), original_text)
        # Проверяем, что текст метки не содержит успешного сообщения
        self.assertNotIn("Предобработанные данные сохранены", self.window.info_label.text())
        # Проверяем, что current_file не изменился
        self.assertEqual(self.window.current_file, None)

    @patch('pandas.read_csv')
    def test_load_data_with_parse_error(self, mock_read_csv):
        """Тест ошибки парсинга при загрузке данных"""
        mock_read_csv.side_effect = pd.errors.ParserError("Ошибка парсинга")
        self.window.load_data("invalid.csv")
        self.assertIn("Ошибка при чтении файла", self.window.info_label.text())

    # ТЕСТЫ АНАЛИЗА ДАННЫХ
    def test_analysis_tab_data_loading(self):
        """Тест загрузки данных во вкладку анализа"""
        self.window.current_file = self.test_csv
        with patch.object(self.window.analysis_tab, 'load_data') as mock_load:
            self.window.load_data(self.test_csv)
            mock_load.assert_called_once()

    # ТЕСТЫ РАЗДЕЛЕНИЯ ДАННЫХ
    @patch('main_window.split_by_year')
    def test_split_by_year(self, mock_split):
        """Тест разделения данных по годам"""
        mock_split.return_value = "year_folder"
        self.window.current_file = self.test_csv
        self.window.split_by_year()
        mock_split.assert_called_once_with(self.test_csv)
        self.assertIn("Данные разделены по годам", self.window.info_label.text())

    @patch('main_window.split_by_week')
    def test_split_by_week(self, mock_split):
        """Тест разделения данных по неделям"""
        mock_split.return_value = "week_folder"
        self.window.current_file = self.test_csv
        self.window.split_by_week()
        mock_split.assert_called_once_with(self.test_csv)
        self.assertIn("Данные разделены по неделям", self.window.info_label.text())

    # ТЕСТЫ ОБРАБОТКИ ИСКЛЮЧЕНИЙ
    def test_get_data_empty_date(self):
        """Тест получения данных с пустой датой"""
        self.window.current_file = self.test_csv
        self.window.date_input.setText("")
        self.window.get_data_for_date()
        error_text = self.window.info_label.text()
        self.assertTrue(
            "Ошибка при получении данных" in error_text or
            "Ошибка в формате даты" in error_text,
            f"Unexpected error message: {error_text}"
        )

    @patch('PyQt6.QtWidgets.QFileDialog.getSaveFileName')
    def test_save_preprocessed_data_error(self, mock_save_dialog):
        """Тест ошибки при сохранении предобработанных данных"""
        mock_save_dialog.return_value = ("test.csv", "CSV Files (*.csv)")
        
        # Создаем мок DataFrame, который вызывает ошибку при сохранении
        mock_df = Mock()
        mock_df.to_csv.side_effect = Exception("Ошибка сохранения")
        
        self.window.preprocessed_data = mock_df
        self.window.save_preprocessed_data()
        
        # Проверяем, что метка содержит сообщение об ошибке
        self.assertTrue(
            any(error_text in self.window.info_label.text() 
                for error_text in ["Ошибка", "ошибка", "Error", "error"]),
            f"Unexpected label text: {self.window.info_label.text()}"
        )

    # Новые тесты для улучшения покрытия
    def test_create_button(self):
        """Тест создания кнопки"""
        test_text = "Test Button"
        test_callback = lambda: None
        button = self.window.create_button(test_text, test_callback, 220)
        self.assertEqual(button.text(), test_text)
        self.assertEqual(button.width(), 220)

    def test_load_styles(self):
            """Тест загрузки стилей"""
            with patch('main_window.get_styles') as mock_get_styles:  # Изменён путь для патча
                # Подготавливаем тестовые стили
                test_styles = "QMainWindow { background: white; }"
                mock_get_styles.return_value = test_styles
            
                # Загружаем стили
                self.window.load_styles()
            
                # Проверяем, что функция get_styles была вызвана
                mock_get_styles.assert_called_once()
            
                # Проверяем, что стили были установлены
                self.assertEqual(self.window.styleSheet(), test_styles)

    @patch('PyQt6.QtWidgets.QMessageBox.warning')
    def test_invalid_month_scraper(self, mock_warning):
        """Тест некорректного месяца в скрапере"""
        self.window.show_scraper_dialog()
        self.window.start_date_input.setText("13.2024")  # Некорректный месяц
        self.window.end_date_input.setText("01.2024")
        self.window.start_scraping()
        mock_warning.assert_called_once()

    def test_empty_data_preview(self):
        """Тест очистки предпросмотра данных"""
        self.window.data_preview.clear()
        self.assertEqual(self.window.data_preview.rowCount(), 0)
        self.assertEqual(self.window.data_preview.columnCount(), 0)

    @patch('pandas.read_csv')
    def test_load_data_unicode_error(self, mock_read_csv):
        """Тест ошибки кодировки при загрузке данных"""
        mock_read_csv.side_effect = UnicodeDecodeError('utf-8', b'', 0, 1, 'invalid start byte')
        self.window.load_data("encoded.csv")
        self.assertIn("Ошибка при чтении файла", self.window.info_label.text())

    def test_get_data_for_date_no_data(self):
        """Тест получения данных для даты, отсутствующей в датасете"""
        self.window.current_file = self.test_csv
        self.window.date_input.setText("2023-01-01")  # Дата вне диапазона тестовых данных
        self.window.get_data_for_date()
        self.assertTrue(
            "находится вне диапазона данных" in self.window.info_label.text() or
            "Нет данных" in self.window.info_label.text()
        )

if __name__ == '__main__':
    unittest.main(verbosity=2)
