from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QBrush
from PyQt5 import QtCore, QtGui, QtWidgets
from functools import partial
import sys
import json
import numpy as np
import time

import pickle

# pos_info = {'Win': {'x':0, 'y':0, 'h':600, 'w':600}}
# json.dump(pos_info, open("info.ini", 'w'))

class BoardText(QTextEdit):
    def __init__(self):
        super(BoardText, self).__init__()
        self.textChanged.connect(self._call_textChanged)
        self.setAutoFormatting(QTextEdit.AutoBulletList)
        self.setCursorWidth(1)

        # self.setFixedWidth(300)
        # self.setFixedHeight(30)
        self.setTabStopDistance(80)

    def _call_textChanged(self):
        # QTextEdit은 QDocument의 크기
        # print(self, "This text is changed.", self.parent().parent())
        if self.parent() is not None:
            # 초기 class 선언하면서 실행되는 과정을 방지.
            self.resize_text_box()
        pass
        # print(f"This text edit Changed {self}")
        # print(f"{self.toPlainText()}")
        # self.setTextColor(QColor(0, 100, 100))
        # self.zoomIn(5)

    def resize_text_box(self):
        # print('Call resize', self.document().size().height())
        if self.document().size().height() != 0:
            self.setFixedHeight(int(self.document().size().height()) +
                                int(self.contentsMargins().top()) +
                                int(self.contentsMargins().bottom()))

    def contextMenuEvent(self, event):
        gp = event.globalPos()
        menu = self.createStandardContextMenu(gp)
        Getinfo = menu.addAction("GetSelectedStrInfo")
        GetHtml = menu.addAction("GetHtmlInfo")
        action = menu.exec_(gp)

        if action == Getinfo:
            get_txt = self.textCursor()
            # if get_txt.hasSelection():
            fmt = QtGui.QTextCharFormat()

            fmt.setBackground(QtCore.Qt.green)
            fmt.setForeground(QBrush(QColor(100, 100, 255)))
            # fmt.setUnderlineColor(QtCore.Qt.green)
            get_txt.setCharFormat(fmt)

        if action == GetHtml:
            get_txt = self.textCursor()
            print(self.toHtml())


class BoardUI_Base(QWidget):
    """
    Function
    """
    def __init__(self, title, WindowId):
        super(BoardUI_Base, self).__init__()
        # --------------------------------------------------------------------------------------------------------------
        self.setWindowTitle(title)
        self.WindowId = WindowId
        # --------------------------------------------------------------------------------------------------------------
        pos_info = json.load(open("info.ini"))[self.WindowId]
        self.setGeometry(pos_info['x'], pos_info['y'], pos_info['h'], pos_info['w'])
        # --------------------------------------------------------------------------------------------------------------
        his_info = json.load(open("his.ini"))
        if his_info == {}:
            # 비어 있는 경우 Pass
            self.table_row = 0
            self.table_col = 2
            pass
        else:
            self._load_his_ini(his_info)
        # 요소 선언 -----------------------------------------------------------------------------------------------------
        # 1] Main Frame
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)
        # 2] Table
        self.main_lay_table = QTableWidget()
        self.main_layout.addWidget(self.main_lay_table)
        self.main_lay_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.main_lay_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

        self.main_lay_table.setRowCount(self.table_row)
        self.main_lay_table.setColumnCount(self.table_col)
        # --------------------------------------------------------------------------------------------------------------
        # Signal
        self.main_lay_table.cellChanged.connect(self._call_cellChanged)
        self.main_lay_table.cellClicked.connect(self._call_cellClicked)
        # --------------------------------------------------------------------------------------------------------------
        # Table DB
        self.Table_DB = {
            # 'Row' : {'Time': str(time), 'Contents': object(html))
        }

        # --------------------------------------------------------------------------------------------------------------
        self.show()
        self.main_lay_table.setHorizontalHeaderLabels(['Time', 'Content'])
        self._load_all()

    def _save_all(self):
        self.Table_DB = {}  # Table DB Clean

        for i in range(self.main_lay_table.rowCount()):

            get_cont_wid = self.main_lay_table.cellWidget(i, 1)

            self.Table_DB[i] = {'Time': self.main_lay_table.item(i, 0).text(),
                                'Cont': get_cont_wid.toHtml()}
            # print(f"Line_{i} is saved.")
        # save file
        json.dump(self.Table_DB, open("DB.ini", 'w'))

    def _load_all(self):
        # print('Load all file')
        # 이전 파일 모두 지움
        [self.main_lay_table.removeRow(0) for i in range(self.main_lay_table.rowCount())]

        # 데이터 Load
        self.Table_DB = json.load(open("DB.ini"))

        # Table에 업데이트
        for i in self.Table_DB:
            self.main_lay_table.insertRow(int(i))
            self.main_lay_table.setItem(int(i), 0, QTableWidgetItem(f"{self.Table_DB[i]['Time']}"))
            self._make_cell_widget(self.main_lay_table, int(i), self.Table_DB[i]['Cont'])

        head = self.main_lay_table.horizontalHeader()
        head.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        head.setSectionResizeMode(1, QHeaderView.Stretch)

        self.main_lay_table.resizeRowsToContents()

    def _resize_main_lay_table(self, ):
        # print("Resize Main lay table according to contents")
        self.main_lay_table.resizeRowsToContents()

    def _save_pos_info(self, win_name):
        # Get_current_pos
        pos_info = json.load(open("info.ini"))
        # Get wind pos
        geo = self.geometry().getRect()
        pos_info[win_name] = {'x': geo[0], 'y': geo[1], 'h': geo[2], 'w': geo[3]}
        # Update pos
        json.dump(pos_info, open("info.ini", 'w'))

    def _call_cellChanged(self):
        print("Cell Changed.")

    def _call_cellClicked(self, cell):
        print(f"Call Cell Clicked - Row{cell}")

    def _insert_row(self):
        self.main_lay_table.insertRow(0)
        t = time.localtime()
        self.main_lay_table.setItem(0, 0, QTableWidgetItem(f"{t.tm_mon:02}-{t.tm_mday:02}-"
                                                           f"{t.tm_hour:02}-{t.tm_min:02}-"
                                                           f"{t.tm_sec:02}"))
        self._make_cell_widget(self.main_lay_table, 0)

        head = self.main_lay_table.horizontalHeader()
        head.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        head.setSectionResizeMode(1, QHeaderView.Stretch)

        # self.main_lay_table.resizeColumnsToContents()
        self.main_lay_table.resizeRowsToContents()

    def _make_cell_widget(self, paraent_table, row, init_html=''):
        cell_widget = BoardText()
        paraent_table.setCellWidget(row, 1, cell_widget)

        cell_widget.setHtml(init_html)
        cell_widget.textChanged.connect(self._resize_main_lay_table)

    def contextMenuEvent(self, event):
        """ Main window 에서 마우스 오른쪽 누르면 나오는 메뉴 """
        gp = event.globalPos()
        menu = QMenu(self)
        remove_row = menu.addAction("Remove Row")
        insert_row = menu.addAction("Insert Row [Insert]")
        save_db = menu.addAction("Save DB")
        load_db = menu.addAction("Load DB")

        # disable
        if self.main_lay_table.currentItem() is not None:
            remove_row.setDisabled(False)  # 셀을 선택한 후 액션을 한 경우
        else:
            remove_row.setDisabled(True)

        action = menu.exec_(gp)

        # Action connect -----------------------------------------------------------------------------------------------
        if action == remove_row:
            get_row = self.main_lay_table.currentItem().row()   # 선택된 셀의 row 취득
            self.main_lay_table.removeRow(get_row)              # row 정보에 따라 해당 row 제거
        if action == insert_row:
            self._insert_row()
        if action == save_db:
            if self.main_lay_table.rowCount() != 0:
                self._save_all()
        if action == load_db:
            self._load_all()

    def keyPressEvent(self, a):
        if a.key() == Qt.Key_Insert:
            self._insert_row()
        else:
            pass

    def moveEvent(self, a) -> None:
        self._save_pos_info(win_name=self.WindowId)

    def resizeEvent(self, a) -> None:
        self._save_pos_info(win_name=self.WindowId)


if __name__ == '__main__':
    # Board_Tester
    app = QApplication(sys.argv)
    window = BoardUI_Base(title='TimeActionScheduler', WindowId='Win')
    app.exec_()
