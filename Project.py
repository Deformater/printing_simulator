import sys
import sqlite3
from random import randint


from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5 import uic  # Импортируем uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QFileDialog
import datetime as dt


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initui()

        # Переменные и надстройки
        self.text_color = QColor(100, 100, 100)
        self.text_font_size = 144
        
        # Задание размера текста и цвета
        self.textEdit.setTextColor(self.text_color)
        self.textEdit.setFontPointSize(self.text_font_size)
        
        self.current_pos = 0
        self.keys = 0
        self.error_keys = 0
        self.text = ''
        self.comboBox.setStyleSheet("color: white;"
                                    "background-color: rgba(100, 149, 237, 255);"
                                    "selection-color: black;"
                                    "selection-background-color: white")
        self.comboBox_result.setStyleSheet("color: white;"
                                        "background-color: rgba(100, 149, 237, 255);"
                                        "selection-color: black;"
                                        "selection-background-color: white")

    def initui(self):
        # Загружаем дизайн
        uic.loadUi('trenazer.ui', self)

        # Свой текст
        self.newtext = ''
        self.pushButton.clicked.connect(self.new_text)
        self.pushButton.setStyleSheet("color: white; background-color: rgba(100, 149, 237, 255)")

        # Кнопки начать/закончить
        self.beginButton.setStyleSheet("color: white; background-color: rgba(100, 149, 237, 255)")
        self.beginButton.clicked.connect(self.begin)
        self.endButton.setStyleSheet("color: black; background-color: rgba(255, 255, 255, 255)")
        self.endButton.clicked.connect(self.end)
        self.endButton.setEnabled(False)

        # Сохранение результатов
        self.pushButtonSave.clicked.connect(self.save)
        self.pushButtonSave.setStyleSheet("color: red; background-color: rgba(255, 255, 255, 255)")
        self.pushButtonSave.setEnabled(False)

        # Подключение БД результатов
        self.connection = sqlite3.connect("results.sqlite")

        # Подключение БД текстов и вывода данных в listWidget
        self.connection_text = sqlite3.connect("Texts.sqlite")
        self.res = self.connection_text.cursor().execute("""SELECT * FROM ENG_TEXT""").fetchall()
        self.listWidget.addItems(map(lambda x: x[1], self.res))
        self.comboBox.currentTextChanged.connect(self.text_list_vivod)

        #
        self.selectButton.clicked.connect(self.select)
        self.listWidget.currentRowChanged.connect(lambda: self.selectButton.setEnabled(True))

        #
        self.randomButton.clicked.connect(self.random_text)

        # Подключение триггера для вывода таблицы результатов
        self.tabWidget.tabBarClicked.connect(self.select_data)
        self.comboBox_result.currentTextChanged.connect(self.select_data)

    def changing_text(self):
        self.text = ' '.join(self.text.split())

    def select(self):

        self.text = self.res[self.listWidget.currentRow()][0]
        self.changing_text()

        self.beginButton.setText('Начать')

        self.current_pos = 0
        self.keys = 0
        self.error_keys = 0

    def random_text(self):  #
        self.listWidget.setCurrentRow(randint(0, len(self.res) - 1))

    def text_list_vivod(self):  # Функция вывода названий текстов из БД текстов
        self.listWidget.clear()
        self.res = self.connection_text.cursor().execute("""SELECT * FROM RUS_TEXT""").fetchall()
        self.selectButton.setEnabled(False)

        # Вывод нужных названий текстов
        if self.comboBox.currentText() == 'АБВ':
            self.res = self.connection_text.cursor().execute("""SELECT * FROM RUS_TEXT""").fetchall()
            self.listWidget.addItems(map(lambda x: x[1], self.res))
        else:
            self.res = self.connection_text.cursor().execute("""SELECT * FROM ENG_TEXT""").fetchall()
            self.listWidget.addItems(map(lambda x: x[1], self.res))

    def select_data(self):  # Результаты
        # Работа с комбобоксом
        if self.comboBox_result.currentText() == 'За час':
            self.selected_time = dt.timedelta(hours=1)
        elif self.comboBox_result.currentText() == 'За день':
            self.selected_time = dt.timedelta(days=1)
        elif self.comboBox_result.currentText() == 'За неделю':
            self.selected_time = dt.timedelta(weeks=1)
        elif self.comboBox_result.currentText() == 'За месяц':
            self.selected_time = dt.timedelta(days=31)

        res = self.connection.cursor().execute("""SELECT * FROM result""").fetchall()
        res.reverse()

        # Размер таблицы
        now_time = dt.datetime.now()
        self.tableWidget.setRowCount(0)

        # Вывод
        i = 0
        for row in res:
            if now_time - dt.datetime.strptime(row[0], '%Y:%m:%d %H:%M:%S') <= self.selected_time:
                self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
                for j, elem in enumerate(row):
                    self.tableWidget.setItem(i, j, QTableWidgetItem(str(elem)))
                i += 1

    def save(self):  # Сохранение результатов
        try:
            self.connection.cursor().execute("INSERT INTO result VALUES(?, ?)",
                                            (self.beginTime.strftime('%Y:%m:%d %H:%M:%S'), self.results))
            self.connection.commit()

            self.pushButtonSave.setEnabled(False)
        except AttributeError:
            self.errorText.setText('Вы ещё не начали')

    def keyPressEvent(self, event):  # Работа с клавиатурой
        if self.endButton.isEnabled():
            if self.current_pos < len(self.text) - 1:
                # Сравнение введённой клавиши с правильной
                if event.text() == self.text[self.current_pos]:
                    self.current_pos += 1
                    self.keys += 1

                    # Вывод текста
                    self.textEdit.setStyleSheet("QTextEdit {background-color:rgba(255, 255, 255, 255)}")
                    self.textEdit.setText(self.text[self.current_pos:])
                # Проверка вспомогательных клавиш (shift, control)
                elif event.key() not in (Qt.Key_Shift, Qt.Key_Control):
                    # Маркирование ошибки при введении текста
                    self.error_keys += 1
                    self.textEdit.setStyleSheet("QTextEdit {background-color:rgba(255, 0, 0, 120)}")
            else:
                # Если текст закончится
                self.textEdit.setText('Текст закончился')
                self.beginButton.setText('Начать')
                self.end()
                self.current_pos = 0


            self.scoreinfLabel.setText(f'Cимволов: верных: {self.keys} неверных: {self.error_keys}')

    def begin(self):    # Кнопка начать
        # Проверка текста на пустоту
        if not self.text:
            self.errorText.setText('Вы не выбрали текст')
            return None

        # Отчистка поля с результатом  и запуск таймера
        self.errorText.setText('')
        if self.beginButton.text() == 'Начать':
            self.beginTime = dt.datetime.now()

        # Вывод текста заново если позиция курсора равна 0
        if self.current_pos == 0:
            self.textEdit.setText(self.text)
            self.keys = 0
            self.error_keys = 0

        # Выключение кнопок и смена цветов
        self.comboBox.setEnabled(False)

        self.pushButtonSave.setEnabled(False)

        self.endButton.setEnabled(True)
        self.endButton.setStyleSheet("color: white; background-color: rgba(100, 149, 237, 255)")

        self.beginButton.setStyleSheet("color: black; background-color: rgba(255, 255, 255, 255)")
        self.beginButton.setEnabled(False)
        self.beginButton.setText('Продолжить')

        # Убрать фокус
        self.setFocus()

    def end(self):     # Кнопка закончить
        self.results = self.result()

        self.textEdit.setStyleSheet('color:black')
        self.errorText.setText(str(self.results) + ' знаков в минут')

        # Выключение кнопок и смена цветов
        self.comboBox.setEnabled(True)

        self.pushButtonSave.setEnabled(True)

        self.beginButton.setEnabled(True)
        self.beginButton.setStyleSheet("color: white; background-color: rgba(100, 149, 237, 255)")

        self.endButton.setStyleSheet("color: black; background-color: rgba(255, 255, 255, 255)")
        self.endButton.setEnabled(False)

    def result(self):   # Вычисление скорости печати
        delta = dt.datetime.now() - self.beginTime
        return round(self.keys / (delta.total_seconds() / 60))

    def new_text(self):      # Пользовательский текст
        try:
            # Добавления пользовательского файла
            self.fname = QFileDialog.getOpenFileName(self, 'Выбрать текст', '', 'Текст (*.txt)')[0]

            # Открытие файл
            with open(self.fname, encoding='utf8') as f:
                self.new_text = f.read()

            # Выбор языка текста
            if self.comboBox.currentText() == 'ABC':
                self.connection_text.cursor().execute("INSERT INTO ENG_TEXT VALUES(?, ?)",
                                                    (self.new_text, self.fname))
            else:
                self.connection_text.cursor().execute("INSERT INTO RUS_TEXT VALUES(?, ?)",
                                                    (self.new_text, self.fname))
            self.connection_text.commit()
            self.text_list_vivod()
        except FileNotFoundError:
            self.errorText.setText('Нет такого файла')
        except Exception:
            self.errorText.setText('Не верный формат данных в файле')

    def closeEvent(self, event):    # Закрытие БД при закрытие программы
        self.connection.close()
        self.connection_text.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())