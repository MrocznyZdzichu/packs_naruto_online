#https://refactoring.guru/pl/design-patterns/singleton/python/example
import pyodbc
from GUI_Manager import GUI_Manager

class DB_Manager_Meta(type):
    _instances={}
    def __call__(cls,  *args,  **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]
        
        
class DB_Manager(metaclass=DB_Manager_Meta):
    def __init__(self):
        self.__status = 'READY'
        self.tabs_active_flags = {
            'GRACZE_PUNKTY' : 'CZY_AKTYWNY'
            , 'GRACZE_UROBKI' : 'CZY_AKTYWNY'
            , 'PACZKI' : 'CZY_AKTYWNE'
        }
        
        
    def setup_connection(self):
        if self.__status == 'READY':
            self.__conn = pyodbc.connect(
                              'Driver={SQL Server};'
                              'Server=DESKTOP-HU1RMS9;'
                              'Database=PACZKI_NO;'
                              'Trusted_Connection=yes;')
            self.__crsr = self.__conn.cursor()
            self.__status = 'CONNECTED'
            return 0
        else:
            return 1
            
            
    def get_conn_status(self):
        return self.__status
        
    
    def execute_sql_select(self,  sql):
        self.__crsr.execute(sql)
        results = []
        for row in self.__crsr.fetchall():
            results.append(row)
        return results
        
    
    def __get_single_col(self,  tab_nm,  col_nm,  where=''):
        sql = f'select {col_nm} from {tab_nm} {where};'
        results = self.execute_sql_select(sql)
        
        processed = []
        for row in results:
            processed.append(row[0])
        return processed
        
        
    def get_tabs_list(self):
        results = self.__get_single_col('sys.tables',  'name')
        return results
        
        
    def add_player(self,  player_name):
        sql = f"insert into GRACZE values ('{player_name}', sysdatetime());"
        self.__crsr.execute(sql)
        sql = f"insert into GRACZE_PUNKTY values ('{player_name}',  0,  sysdatetime(),  1)"
        self.__crsr.execute(sql)
        #self.__conn.commit()
    
    
    def get_full_table(self,  tab,  active_only=0):
        sql = f"select * from {tab};"
        if active_only > 0:
            if tab in self.tabs_active_flags.keys():
                sql = sql[:-1]
                sql += f" where {self.tabs_active_flags[tab]} = 1;"
                        
        res = self.execute_sql_select(sql)
        return res


    def get_col_names(self,  tab):
        sql = f"select NAME from sys.all_columns where object_id in (select object_id from sys.tables where NAME = '{tab}');"
        res = self.execute_sql_select(sql)
        
        cols = []
        for row in res:
            cols.append(row[0])
        return cols
        
        
    def add_pack(self,  pack_nm,  pack_pts):
        scd2_unactive = f"update PACZKI set CZY_AKTYWNE = 0 where NAZWA = '{pack_nm}';"
        insert_sql = f"insert into PACZKI values('{pack_nm}', {int(pack_pts)}, sysdatetime(),1 );"
        self.__crsr.execute(scd2_unactive)
        self.__crsr.execute(insert_sql)
        #self.__conn.commit()
        return 0

    
    def list2_to_sql_insert(self,  list2d,  tab_nm,  quotes_cols):
        sql = f"insert into {tab_nm} values"
        for row in list2d:
            sql += '('
            
            for col in range(0,  len(row)):
                if quotes_cols[col] == 1:
                    sql += "'"
                sql += str(row[col])
                if quotes_cols[col] == 1:
                    sql += "'"
                sql += ","
                
            sql = sql[:-1]
            sql += '),'
        
        sql = sql[:-1]
        sql += ';'
        return sql
        
    
    def __get_player_points(self,  player):
        sql = f"select PUNKTY from GRACZE_PUNKTY where GRACZ = '{player}' and CZY_AKTYWNY = 1;"
        res = self.execute_sql_select(sql)
        return res[0][0]
        
    
    def __disable_urobki_scd2(self, player):
        sql = f"update GRACZE_UROBKI set CZY_AKTYWNY = 0 where CZY_AKTYWNY = 1 and GRACZ = '{player}'"
        self.__crsr.execute(sql)
        #self.__conn.commit()
        
    
    def disable_scd2(self,  tab,  key_cols,  key_vals,  scd2_col,  quotes_list):
        sql = f"update {tab} set {scd2_col} = 0 where "
        for i in range(0,  len(key_cols)):
            if i > 0:
                sql += 'and '
                
            sql += f'{key_cols[i]} = '
            if quotes_list[i] == 1:
                sql += "'"
            sql += key_vals[0]
            if quotes_list[i] == 1:
                sql += "'"
        
        sql += f' and {scd2_col} = 1;'
        print(sql)
        
        self.__crsr.execute(sql)
        #self.__conn.commit()
        
        
    def __disable_urobki_points_scd2s(self, player):
        self.disable_scd2('GRACZE_UROBKI',  ['GRACZ'],  [player],  'CZY_AKTYWNY',  [1])
        self.disable_scd2('GRACZE_PUNKTY',  ['GRACZ'],  [player],  'CZY_AKTYWNY',  [1])
        
    
    def validate_player_names(self,  contributors):
        player_names = self.__get_single_col('GRACZE',  'NAZWA')
        rc = all(el in player_names for el in contributors)
        return rc
        
        
    def insert_points(self,  data):
        punkty = []
        for row in data:
            player = row[0]
            urobek = int(row[1]) + int(row[2]/1000) + int(row[3])
            row.append(urobek)
            row.append('sysdatetime()')
            row.append(1)
            
            punkty_row = []
            curr_pts = self.__get_player_points(player)
            pts_total = curr_pts+urobek
            punkty_row. append(player)
            punkty_row.append(pts_total)
            punkty_row.append('sysdatetime()')
            punkty_row.append(1)
            punkty.append(punkty_row)
            
            self.__disable_urobki_points_scd2s(player)
            
        urobki_sql = self.list2_to_sql_insert(data,  'GRACZE_UROBKI',  [1,  0, 0,  0, 0,  0,  0])
        print(urobki_sql)
        self.__crsr.execute(urobki_sql)
        #self.__conn.commit()
        
        punkty_sql = self.list2_to_sql_insert(punkty,  'GRACZE_PUNKTY',  [1,  0,  0,  0])
        print(punkty_sql)
        self.__crsr.execute(punkty_sql )
        #self.__conn.commit()


    def get_players(self):
        res = self.__get_single_col('GRACZE',  'NAZWA')
        return res
        
        
    def get_packs(self):
        res = self.__get_single_col('PACZKI', 'NAZWA',  'where CZY_AKTYWNE = 1')
        return res
        
        
    def assign_pack(self,  player_nm,  pack_nm):
        pack_points = self.__get_single_col('PACZKI',  'PUNKTY',  f"where CZY_AKTYWNE = 1 and NAZWA = '{pack_nm}'")
        curr_points = self.__get_single_col('GRACZE_PUNKTY',  'PUNKTY',  f"where CZY_AKTYWNY = 1 and GRACZ = '{player_nm}'")
        new_pts = int(curr_points[0]) - int(pack_points[0])
        
        GUIM = GUI_Manager()
        GUIM.log_msg(f'Koszt paczki: {pack_points},  obecne punkty gracza: {curr_points},  punkty po paczce: {new_pts}',  1)
        
        sql = self.list2_to_sql_insert([[player_nm,  pack_nm,  'sysdatetime()']],  'GRACZE_PACZKI',  [1,  1,  0])
        GUIM.log_msg(f'Przygotowany insert: {sql}',  2)
        self.__crsr.execute(sql)
        #self.__conn.commit()
        
        self.disable_scd2('GRACZE_PUNKTY',  ['GRACZ'],  [player_nm],  'CZY_AKTYWNY',  [1])
        sql = self.list2_to_sql_insert([[player_nm,  new_pts,  'sysdatetime()',  1]],  'GRACZE_PUNKTY',  [1,  0,  0,  0])
        GUIM.log_msg(f'Przygotowany insert: {sql}',  2)
        self.__crsr.execute(sql)
        #self.__conn.commit()

    def commit(self):
        self.__conn.commit()
        
        
    def rollback(self):
        self.__conn.rollback()
