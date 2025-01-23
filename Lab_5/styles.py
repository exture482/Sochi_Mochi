def get_styles():
    return """
    QMainWindow, QWidget, QDialog, QMessageBox {
        background-color: #FFFFFF;
        color: #2C3E50;
    }
    
    QPushButton {
        background-color: #3498DB;
        color: white;
        padding: 6px 14px;
        font-size: 13px;
        border: none;
        border-radius: 6px;
        min-width: 140px;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-weight: 500;
    }
    
    QPushButton:hover {
        background-color: #2980B9;
    }
    
    QPushButton:disabled {
        background-color: #BDC3C7;
        color: #7F8C8D;
    }
    
    QGroupBox {
        border: 1px solid #ECF0F1;
        border-radius: 6px;
        margin-top: 1.2em;
        padding-top: 1.2em;
        padding: 8px;
        background-color: #FFFFFF;
    }
    
    QGroupBox::title {
        color: #2C3E50;
        font-weight: 600;
        font-size: 13px;
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 8px;
        background-color: transparent;
    }
    
    QTableWidget {
        background-color: #FFFFFF;
        gridline-color: #ECF0F1;
        border: 1px solid #ECF0F1;
        color: #2C3E50;
        border-radius: 6px;
    }
    
    QHeaderView::section {
        background-color: #F8F9FA;
        padding: 8px;
        border: 1px solid #ECF0F1;
        font-weight: 600;
        font-family: 'Segoe UI', Arial, sans-serif;
        color: #2C3E50;
    }
    
    QLabel {
        color: #2C3E50;
        font-size: 13px;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-weight: 400;
    }
    
    QLineEdit {
        border: 1px solid #E0E0E0;
        border-radius: 4px;
        padding: 6px;
        font-family: 'Segoe UI', Arial, sans-serif;
        background-color: #FFFFFF;
        color: #2C3E50;
    }
    
    QLineEdit:focus {
        border-color: #3498DB;
    }
    
    QProgressBar {
        border: none;
        border-radius: 4px;
        text-align: center;
        background-color: #ECF0F1;
        height: 8px;
        color: #2C3E50;
    }
    
    QProgressBar::chunk {
        background-color: #3498DB;
        border-radius: 4px;
    }
    
    QTabWidget::pane {
        border: 1px solid #ECF0F1;
        background-color: #FFFFFF;
        border-radius: 6px;
    }
    
    QTabBar::tab {
        background-color: #F8F9FA;
        color: #2C3E50;
        padding: 8px 16px;
        border: 1px solid #ECF0F1;
        border-bottom: none;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        font-weight: 500;
        font-size: 13px;
    }
    
    QTabBar::tab:selected {
        background-color: #FFFFFF;
        border-bottom: 2px solid #3498DB;
    }
    
    QComboBox {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 4px;
        padding: 6px;
        color: #2C3E50;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 13px;
    }
    
    QComboBox:hover {
        border-color: #3498DB;
    }
    
    QComboBox::drop-down {
        border: none;
        width: 16px;
    }
    
    QComboBox::down-arrow {
        image: url(down_arrow.png);
        width: 10px;
        height: 10px;
    }
    
    QDialog QTableWidget {
        border: 1px solid #ECF0F1;
        background-color: #FFFFFF;
        color: #2C3E50;
        gridline-color: #ECF0F1;
    }
    
    QDialog QHeaderView::section {
        background-color: #F8F9FA;
        color: #2C3E50;
        padding: 8px;
        border: 1px solid #ECF0F1;
    }
    
    QMessageBox {
    background-color: #FFFFFF;
    }
    QMessageBox QPushButton {
        background-color: #3498DB;
        color: white;
        padding: 6px 14px;
        border: none;
        border-radius: 6px;
        min-width: 100px;
    }
    QMessageBox QLabel {
        color: #2C3E50;
    }
    
    QDialog QPushButton {
        min-width: 100px;
        background-color: #3498DB;
        color: white;
    }
    
    QDialog QLabel {
        color: #2C3E50;
        font-size: 13px;
    }
    
    QScrollBar:vertical {
        border: none;
        background-color: #F8F9FA;
        width: 10px;
        margin: 0;
        border-radius: 5px;
    }
    
    QScrollBar::handle:vertical {
        background-color: #BDC3C7;
        min-height: 20px;
        border-radius: 5px;
    }
    
    QScrollBar::handle:vertical:hover {
        background-color: #95A5A6;
    }
    
    QScrollBar:horizontal {
        border: none;
        background-color: #F8F9FA;
        height: 10px;
        margin: 0;
        border-radius: 5px;
    }
    
    QScrollBar::handle:horizontal {
        background-color: #BDC3C7;
        min-width: 20px;
        border-radius: 5px;
    }
    
    QScrollBar::handle:horizontal:hover {
        background-color: #95A5A6;
    }
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        border: none;
        background: none;
    }
    
    /* Стили для StatsDialog и DateFilterDialog */
    StatsDialog, DateFilterDialog {
        background-color: #FFFFFF;
    }
    
    StatsDialog QTableWidget, DateFilterDialog QTableWidget {
        border: 1px solid #ECF0F1;
        background-color: #FFFFFF;
    }
    
    /* Стили для окна скрапера */
    QWidget#scraper_dialog {
        background-color: #FFFFFF;
    }
    
    QWidget#scraper_dialog QLabel {
        color: #2C3E50;
    }
    
    QWidget#scraper_dialog QPushButton {
        background-color: #3498DB;
        color: white;
    }
    
    QWidget#scraper_dialog QProgressBar {
        text-align: center;
        background-color: #ECF0F1;
        border-radius: 4px;
        color: #2C3E50;
    }
    
    QWidget#scraper_dialog QProgressBar::chunk {
        background-color: #3498DB;
        border-radius: 4px;
    }
    """