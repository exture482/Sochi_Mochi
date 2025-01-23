import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import numpy as np
from PyQt6.QtWidgets import QApplication,QTableWidget, QDialog
from PyQt6.QtCore import Qt


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_analysis import DataAnalysisTab, StatsDialog, DateFilterDialog

class TestDataAnalysis(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Инициализация приложения PyQt"""
        cls.app = QApplication([])

    def setUp(self):
        """Создание тестовых данных и инициализация"""
        self.analysis_tab = DataAnalysisTab()
        
        # Создаем тестовый DataFrame
        self.test_data = pd.DataFrame({
            'date': pd.date_range(start='2024-01-01', periods=5),
            'temperature_day': [20, 22, 21, 23, 22],
            'temperature_day_fahrenheit': [68, 71.6, 69.8, 73.4, 71.6],
            'pressure_day': [750, 755, 753, 752, 751]
        })
        self.test_csv = "test_weather_data.csv"
        self.test_data.to_csv(self.test_csv, index=False)

    def tearDown(self):
        """Очистка после тестов"""
        self.analysis_tab.close()
        if os.path.exists(self.test_csv):
            os.remove(self.test_csv)
        # Удаляем созданные директории с результатами
        for dir_name in ['analysis_data', 'filtered_data', 'average_temperature', 'temperature_plots']:
            if os.path.exists(dir_name):
                import shutil
                shutil.rmtree(dir_name)

    def test_initial_state(self):
        """Тест начального состояния"""
        self.assertIsNone(self.analysis_tab.df)
        self.assertIsNone(self.analysis_tab.current_file)
        self.assertEqual(self.analysis_tab.info_label.text(), 
                        "Загрузите данные для начала анализа")
        self.assertFalse(self.analysis_tab.process_data_btn.isEnabled())
        self.assertFalse(self.analysis_tab.show_stats_btn.isEnabled())

    def test_load_data(self):
        """Тест загрузки данных"""
        self.analysis_tab.load_data(self.test_data, self.test_csv)
        self.assertIsNotNone(self.analysis_tab.df)
        self.assertEqual(self.analysis_tab.current_file, self.test_csv)
        self.assertTrue(self.analysis_tab.process_data_btn.isEnabled())

    @patch('pandas.DataFrame.to_csv')
    def test_process_data(self, mock_to_csv):
        """Тест обработки данных"""
        self.analysis_tab.load_data(self.test_data, self.test_csv)
        self.analysis_tab.process_data()
        mock_to_csv.assert_called_once()
        self.assertTrue(self.analysis_tab.show_stats_btn.isEnabled())
        self.assertTrue(self.analysis_tab.apply_filter_btn.isEnabled())

    def test_temperature_filter(self):
        """Тест фильтрации по температуре"""
        # Загружаем данные
        self.analysis_tab.load_data(self.test_data, self.test_csv)
        self.analysis_tab.process_data()
    
        # Сохраняем исходное количество записей
        original_count = len(self.test_data)
    
        # Устанавливаем фильтр температуры
        self.analysis_tab.temp_filter.setText("21")
    
        # Применяем фильтр
        with patch('PyQt6.QtWidgets.QMessageBox.information'):
            self.analysis_tab.apply_filters()
    
        # Проверяем, что количество записей уменьшилось
        current_count = self.analysis_tab.data_preview.rowCount()
        self.assertLess(current_count, original_count)
    
        # Проверяем текст информационной метки
        info_text = self.analysis_tab.info_label.text()
        self.assertIn("Отфильтрованные данные", info_text)

    def test_temperature_filter_with_boundary(self):
        """Тест фильтрации по температуре с граничными значениями"""
        # Создаем тестовые данные с граничными значениями
        test_data = pd.DataFrame({
            'date': pd.date_range(start='2024-01-01', periods=5),
            'temperature_day': [19.9, 20.0, 20.1, 21.0, 21.1],
            'temperature_day_fahrenheit': [67.8, 68.0, 68.2, 69.8, 70.0],
            'pressure_day': [750, 755, 753, 752, 751]
        })
    
        # Загружаем данные
        self.analysis_tab.load_data(test_data, self.test_csv)
        self.analysis_tab.process_data()
    
        # Сохраняем исходное количество записей
        original_count = len(test_data)
    
        # Устанавливаем фильтр температуры
        self.analysis_tab.temp_filter.setText("20")
    
        # Применяем фильтр
        with patch('PyQt6.QtWidgets.QMessageBox.information'):
            self.analysis_tab.apply_filters()
    
        # Проверяем, что отображается правильное количество записей
        filtered_count = self.analysis_tab.data_preview.rowCount()
        self.assertEqual(filtered_count, 4)  # Должно остаться 4 записи >= 20
    
        # Проверяем текст информационной метки
        info_text = self.analysis_tab.info_label.text()
        self.assertIn(str(filtered_count), info_text)

    def test_temperature_filter_save_results(self):
        """Тест сохранения отфильтрованных данных"""
        self.analysis_tab.load_data(self.test_data, self.test_csv)
        self.analysis_tab.process_data()
    
        # Устанавливаем фильтр температуры
        self.analysis_tab.temp_filter.setText("21")
    
        # Мокаем создание директории и сохранение файла
        with patch('os.makedirs') as mock_makedirs, \
             patch('pandas.DataFrame.to_csv') as mock_to_csv, \
             patch('PyQt6.QtWidgets.QMessageBox.information') as mock_info:
        
            self.analysis_tab.apply_filters()
        
            # Проверяем, что была создана директория
            mock_makedirs.assert_called_once()
            # Проверяем, что данные были сохранены
            mock_to_csv.assert_called_once()
            # Проверяем, что было показано сообщение
            mock_info.assert_called_once()

        def test_date_filter(self):
            """Тест фильтрации по датам"""
            self.analysis_tab.load_data(self.test_data, self.test_csv)
            self.analysis_tab.start_date.setText("2024-01-02")
            self.analysis_tab.end_date.setText("2024-01-04")
            self.analysis_tab.apply_filters()
            self.assertTrue(self.analysis_tab.show_date_filter_btn.isEnabled())

    @patch('matplotlib.pyplot.show')
    def test_plot_temperature_changes(self, mock_show):
        """Тест построения графика температуры"""
        self.analysis_tab.load_data(self.test_data, self.test_csv)
        self.analysis_tab.process_data()
        self.analysis_tab.plot_temperature_changes()
        mock_show.assert_called_once()
        self.assertTrue(os.path.exists('temperature_plots'))

    def test_monthly_averages(self):
        """Тест расчета средних температур по месяцам"""
        self.analysis_tab.load_data(self.test_data, self.test_csv)
        self.analysis_tab.process_data()
        with patch('PyQt6.QtWidgets.QDialog.exec'):
            self.analysis_tab.show_monthly_averages()
        self.assertTrue(os.path.exists('average_temperature'))

    def test_invalid_temperature_filter(self):
        """Тест некорректного значения температуры"""
        self.analysis_tab.load_data(self.test_data, self.test_csv)
        self.analysis_tab.temp_filter.setText("invalid")
        with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning:
            self.analysis_tab.apply_filters()
            mock_warning.assert_called_once()

    def test_invalid_date_filter(self):
        """Тест некорректных дат"""
        self.analysis_tab.load_data(self.test_data, self.test_csv)
        self.analysis_tab.start_date.setText("invalid")
        self.analysis_tab.end_date.setText("2024-01-04")
        with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning:
            self.analysis_tab.apply_filters()
            mock_warning.assert_called_once()

    def test_plot_monthly_temperature(self):
        """Тест построения графика температуры за конкретный месяц"""
        # Подготовка тестовых данных за несколько месяцев
        test_dates = pd.date_range(start='2024-01-01', end='2024-02-29', freq='D')
        test_data = pd.DataFrame({
            'date': test_dates,
            'temperature_day': np.random.uniform(15, 25, len(test_dates)),
            'temperature_day_fahrenheit': np.random.uniform(60, 80, len(test_dates)),
            'pressure_day': np.random.uniform(740, 760, len(test_dates))
        })
    
        # Загружаем данные
        self.analysis_tab.load_data(test_data, self.test_csv)
        self.analysis_tab.process_data()
    
        # Устанавливаем месяц и год
        self.analysis_tab.month_combo.setCurrentText('1')  # Январь
        self.analysis_tab.year_combo.setCurrentText('2024')
    
        # Проверяем создание графика
        with patch('matplotlib.pyplot.show') as mock_show, \
             patch('matplotlib.pyplot.savefig') as mock_savefig, \
             patch('PyQt6.QtWidgets.QMessageBox.information') as mock_info:
        
            self.analysis_tab.plot_monthly_temperature()
        
            # Проверяем, что график был показан и сохранён
            mock_show.assert_called_once()
            mock_savefig.assert_called_once()
            mock_info.assert_called_once()
        
            # Проверяем создание директории для графиков
            self.assertTrue(os.path.exists('temperature_plots'))

    def test_directory_creation(self):
        """Тест создания директорий для результатов"""
        # Подготовка
        test_data = pd.DataFrame({
            'date': pd.date_range(start='2024-01-01', periods=5),
            'temperature_day': [20, 22, 21, 23, 22],
            'temperature_day_fahrenheit': [68, 71.6, 69.8, 73.4, 71.6],
            'pressure_day': [750, 755, 753, 752, 751]
        })
    
        self.analysis_tab.load_data(test_data, self.test_csv)
    
        # Тестируем создание директорий при различных операциях
        with patch('PyQt6.QtWidgets.QMessageBox.information'):
            # Проверяем создание директории при обработке данных
            self.analysis_tab.process_data()
            self.assertTrue(os.path.exists('analysis_data'))
        
            # Проверяем создание директории при фильтрации
            self.analysis_tab.temp_filter.setText("21")
            self.analysis_tab.apply_filters()
            self.assertTrue(os.path.exists('filtered_data'))
        
            # Проверяем создание директории при построении графиков
            self.analysis_tab.plot_temperature_changes()
            self.assertTrue(os.path.exists('temperature_plots'))
        
            # Проверяем создание директории для средних значений
            self.analysis_tab.show_monthly_averages()
            self.assertTrue(os.path.exists('average_temperature'))

    def test_stats_dialog_content(self):
        """Подробный тест диалогового окна статистики"""
        # Подготовка данных
        self.analysis_tab.load_data(self.test_data, self.test_csv)
        self.analysis_tab.process_data()
    
        # Создаем и проверяем диалог статистики
        with patch('PyQt6.QtWidgets.QDialog.exec'):
            # Получаем диалог, но не показываем его
            self.analysis_tab.show_temperature_stats()
        
            # Находим последний созданный диалог
            dialog = [child for child in self.analysis_tab.children() 
                     if isinstance(child, StatsDialog)][-1]
        
            # Проверяем заголовок
            self.assertEqual(dialog.windowTitle(), "Статистическая информация")
        
            # Проверяем размеры
            self.assertGreaterEqual(dialog.width(), 600)
            self.assertGreaterEqual(dialog.height(), 400)
        
            # Находим таблицу в диалоге
            table = [child for child in dialog.children() 
                    if isinstance(child, QTableWidget)][0]
        
            # Проверяем содержимое таблицы
            self.assertGreater(table.rowCount(), 0)
            self.assertGreater(table.columnCount(), 0)

    def test_date_filter_dialog_content(self):
        """Подробный тест диалогового окна фильтрации по датам"""
        # Подготовка
        self.analysis_tab.load_data(self.test_data, self.test_csv)
        self.analysis_tab.process_data()
    
        # Устанавливаем даты
        self.analysis_tab.start_date.setText("2024-01-01")
        self.analysis_tab.end_date.setText("2024-01-05")
    
        # Применяем фильтр и проверяем диалог
        with patch('PyQt6.QtWidgets.QDialog.exec'):
            self.analysis_tab.show_date_filtered_data()
        
            # Находим последний созданный диалог
            dialog = [child for child in self.analysis_tab.children() 
                     if isinstance(child, DateFilterDialog)][-1]
        
            # Проверяем заголовок
            self.assertIn("2024-01-01", dialog.windowTitle())
            self.assertIn("2024-01-05", dialog.windowTitle())
        
            # Находим таблицу
            table = [child for child in dialog.children() 
                    if isinstance(child, QTableWidget)][0]
        
            # Проверяем данные
            self.assertEqual(table.rowCount(), 5)  # Должно быть 5 дней
            self.assertGreater(table.columnCount(), 0)

    def test_dialog_error_handling(self):
        """Тест обработки ошибок в диалоговых окнах"""
        # Создаем патч для QMessageBox.warning
        warning_patcher = patch('data_analysis.QMessageBox.warning')
    
        # Тест 1: Некорректные даты
        with warning_patcher as mock_warning:
            self.analysis_tab.df = self.test_data
            self.analysis_tab.start_date.setText("invalid_date")
            self.analysis_tab.show_date_filtered_data()
            self.assertTrue(mock_warning.called)
            mock_warning.reset_mock()

        # Тест 2: Пустой DataFrame
        with warning_patcher as mock_warning:
            self.analysis_tab.df = pd.DataFrame()
            self.analysis_tab.show_temperature_stats()
            self.assertTrue(mock_warning.called)
            mock_warning.reset_mock()

        # Тест 3: DataFrame без температуры
        with warning_patcher as mock_warning:
            self.analysis_tab.df = pd.DataFrame({'pressure': [1, 2, 3]})
            self.analysis_tab.show_temperature_stats()
            self.assertTrue(mock_warning.called)
            mock_warning.reset_mock()

        # Тест 4: Неправильный диапазон дат
        with warning_patcher as mock_warning:
            self.analysis_tab.df = self.test_data
            self.analysis_tab.start_date.setText("2024-01-05")
            self.analysis_tab.end_date.setText("2024-01-01")
            self.analysis_tab.show_date_filtered_data()
            self.assertTrue(mock_warning.called)

        # Проверяем диалоги
        # Тест 5: StatsDialog с пустыми данными
        with warning_patcher as mock_warning:
            stats_dialog = StatsDialog(pd.DataFrame(), self.analysis_tab)
            self.assertTrue(mock_warning.called)
            mock_warning.reset_mock()

        # Тест 6: DateFilterDialog с пустыми данными
        with warning_patcher as mock_warning:
            date_filter_dialog = DateFilterDialog(
                pd.DataFrame(), 
                "2024-01-01", 
                "2024-01-02", 
                self.analysis_tab
            )
            self.assertTrue(mock_warning.called)

    @patch('PyQt6.QtWidgets.QDialog.exec')
    def test_stats_dialog(self, mock_exec):
        """Тест диалога статистики"""
        self.analysis_tab.load_data(self.test_data, self.test_csv)
        self.analysis_tab.process_data()
        self.analysis_tab.show_temperature_stats()
        mock_exec.assert_called_once()

    def test_translate_columns(self):
        """Тест перевода названий колонок"""
        translations = self.analysis_tab.translate_columns()
        self.assertIn('температура_(день)', translations)
        self.assertEqual(translations['температура_(день)'], 'temperature_day')

if __name__ == '__main__':
    unittest.main(verbosity=2)
