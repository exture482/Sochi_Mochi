import pandas as pd
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt6.QtCore import Qt
from typing import Any, Optional

class OptimizedTableWidget(QTableWidget):
   
    def __init__(self, *args: Any, **kwargs: Any) -> None:
       
        super().__init__(*args, **kwargs)
        self.chunk_size: int = 100
        self.current_chunk: int = 0
        self.total_rows: int = 0
        self.df: Optional[pd.DataFrame] = None
        self.is_transposed: bool = False

    def load_data(self, df: pd.DataFrame, transpose: bool = False) -> None:
       
        if transpose:
           
            self.df = df.T.reset_index()
            self.df.columns = ['Параметр', 'Значение']
        
            if 'Дата' in df.columns:
                date_value = df['Дата'].iloc[0]
                if pd.notna(date_value):
                    if isinstance(date_value, pd.Timestamp):
                        self.df.loc[self.df['Параметр'] == 'Дата', 'Значение'] = date_value.strftime('%Y-%m-%d')
            self.is_transposed = True
        else:
            self.df = df
            self.is_transposed = False

        self.total_rows = len(self.df)
        self.setRowCount(self.total_rows)
        self.setColumnCount(len(self.df.columns))
        self.setHorizontalHeaderLabels(self.df.columns)
        self.current_chunk = 0
        self.load_chunk()
        self.resizeColumnsToContents()
        if self.is_transposed:
            self.setColumnWidth(0, 200)

    def load_chunk(self) -> None:
       
        if self.df is None:
            return

        start: int = self.current_chunk * self.chunk_size
        end: int = min(start + self.chunk_size, self.total_rows)
        
        for row in range(start, end):
            for col in range(len(self.df.columns)):
                value = self.df.iloc[row, col]
                if pd.isna(value):
                    formatted_value = ''
                elif isinstance(value, (int, float)):
                    formatted_value = f"{value:g}" 
                else:
                    formatted_value = str(value)
                    
                item = QTableWidgetItem(formatted_value)
                if self.is_transposed and col == 0:
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.setItem(row, col, item)
        
        self.current_chunk += 1

    def clear(self) -> None:
        """
        Очищает таблицу и сбрасывает все связанные переменные.
        """
        self.setRowCount(0)
        self.setColumnCount(0)
        self.df = None
        self.total_rows = 0
        self.current_chunk = 0

    def scrollContentsBy(self, dx: int, dy: int) -> None:
        """
        Обрабатывает событие прокрутки и загружает новые данные при необходимости.

        """
        super().scrollContentsBy(dx, dy)
        if self.verticalScrollBar().value() == self.verticalScrollBar().maximum():
            if self.current_chunk * self.chunk_size < self.total_rows:
                self.load_chunk()


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    table = OptimizedTableWidget()
    
    # Пример использования
    df = pd.DataFrame({'A': range(1000), 'B': range(1000, 2000)})
    table.load_data(df)
    table.show()
    
    sys.exit(app.exec())