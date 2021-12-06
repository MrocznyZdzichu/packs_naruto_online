from PyQt5 import QtWidgets
from Ui_paczki_okno_glowne import Ui_MainWindow
from DB_Manager import DB_Manager
from GUI_Manager import GUI_Manager

def initialize(ui):
    DBM = DB_Manager()
    GUIM = GUI_Manager(ui)
    
    rc = DBM.setup_connection()
    if rc == 0:
        GUIM.log_msg('Nazwiazano połaczenie z baza danych', 0)
    else:
        GUIM.log_msg('Połaczenie nieudane - brak dostepnej funkcjonalności!', 2)
        return        
        
    status = DBM.get_conn_status()
    GUIM.log_msg(status,  1)

    tabs = DBM.get_tabs_list()
    GUIM.log_msg(f'Lista tabel bazy: {tabs}',  1)
    GUIM.fill_tab_nms(tabs)
    
    players_list = DBM.get_players()
    GUIM.fill_players(players_list)
    
    packs_list = DBM.get_packs()
    GUIM.fill_packs(packs_list)
    
    
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    initialize(ui)

    sys.exit(app.exec_())
