#https://refactoring.guru/pl/design-patterns/singleton/python/example
from PyQt5.QtWidgets import QTableWidgetItem,  QHeaderView
from PyQt5.QtCore import Qt
from decimal import Decimal
class GUI_Manager_Meta(type):
    """
    The Singleton class can be implemented in different ways in Python. Some
    possible methods include: base class, decorator, metaclass. We will use the
    metaclass because it is best suited for this purpose.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class GUI_Manager(metaclass=GUI_Manager_Meta):
    def __init__(self,  mainwindow):
        self.mw = mainwindow


    def log_msg(self,  msg,  msg_type=1):
        prefix = ''
        if msg_type == 0:
            prefix = 'INFO: '
        elif msg_type == 1:
            prefix = 'DEBUG: '
        elif msg_type == 2:
            prefix = 'WARNING: '
            
        msg = prefix+msg
        self.mw.log_console.append(msg)
        
    
    def populate_comboBox(self,  cb,  items_list):
        cb.clear()
        cb.addItems(items_list)
        
        
    def fill_tab_nms(self, tabs):
        self.populate_comboBox(self.mw.combo_preview,  tabs)
        
    
    def __check_table_dims(self,  data):
        rows = len(data)
        cols = len(data[0])
        return [rows,  cols]
        
        
    def __change_tab_widget_size(self,  tw,  dims):
        tw.setRowCount(dims[0])
        tw.setColumnCount(dims[1])    
    
    
    def populate_table(self,  tw,  data,  headers=None):
        tw.setSortingEnabled(False)
        tw.clear()
        dims = self.__check_table_dims(data)
        self.__change_tab_widget_size(tw,  dims)
        
        for row in range(0,  dims[0]):
            for col in range(0,  dims[1]):
                element=data[row][col]
                item = QTableWidgetItem()
                
                if isinstance(element,  Decimal) == True:
                    element= str(element)
                
                item.setData(Qt.DisplayRole,  element)
                tw.setItem(row,  col,  item)
                
        tw.setSortingEnabled(True)
        tw.setHorizontalHeaderLabels(headers)
        header = tw.horizontalHeader()
        for i in range(0,  dims[1]):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
            

    def get_contributor_names(self,  tw):
        contributors = []
        row_count = tw.rowCount()
        for row in range(0, row_count-1):
            item = tw.item(row,  0)
            name = item.text()
            contributors.append(name)
            
        return contributors
        
        
    def get_tw_as_list2d(self,  tw, num_cols=[1,2,3], subst_zero=[3]):
        res = []
        rows = tw.rowCount()
        cols = tw.columnCount()
        
        for row in range(0,  rows-1):
            obs = []
            for col in range(0,  cols):
                item = tw.item(row,  col)
                value = item.text()
                if col in subst_zero:
                    if value =='':
                        value = 0
                if col in num_cols:
                    value = int(value)
                    
                obs.append(value)
            res.append(obs)
        return res


    def fill_players(self,  players_list):
        self.populate_comboBox(self.mw.cb_choose_player,  players_list)
        
        
    def fill_packs(self,  packs_list):
        self.populate_comboBox(self.mw.cb_choose_pack,  packs_list)
