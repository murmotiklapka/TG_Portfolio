import sqlite3
from config import DATABASE

skills = [ (_,) for _ in (['Python', 'SQL', 'API', 'Telegram'])]
statuses = [ (_,) for _ in (['На этапе проектирования', 'В процессе разработки', 'Разработан. Готов к использованию.', 'Обновлен', 'Завершен. Не поддерживается'])]

class DB_Manager:
    def __init__(self, database):
        self.database = database
        
    def create_tables(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''CREATE TABLE projects (
                            project_id INTEGER PRIMARY KEY,
                            user_id INTEGER,
                            project_name TEXT NOT NULL,
                            description TEXT,
                            url TEXT,
                            status_id INTEGER,
                            FOREIGN KEY(status_id) REFERENCES status(status_id)
                        )''') 
            conn.execute('''CREATE TABLE skills (
                            skill_id INTEGER PRIMARY KEY,
                            skill_name TEXT
                        )''')
            conn.execute('''CREATE TABLE project_skills (
                            project_id INTEGER,
                            skill_id INTEGER,
                            FOREIGN KEY(project_id) REFERENCES projects(project_id),
                            FOREIGN KEY(skill_id) REFERENCES skills(skill_id)
                        )''')
            conn.execute('''CREATE TABLE status (
                            status_id INTEGER PRIMARY KEY,
                            status_name TEXT
                        )''')
            conn.commit()

    def __executemany(self, sql, data):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.executemany(sql, data)
            conn.commit()
    
    def __select_data(self, sql, data = tuple()):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute(sql, data)
            return cur.fetchall()

    def alter_table(self, table_name, new_column_name, new_column_type):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {new_column_name} {new_column_type}")

    def drop_tables(self, table_names):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute(f"DROP TABLE IF EXISTS {table_names}")

            
    def default_insert(self):
        sql = 'INSERT OR IGNORE INTO skills (skill_name) values(?)'
        data = skills
        self.__executemany(sql, data)
        sql = 'INSERT OR IGNORE INTO status (status_name) values(?)'
        data = statuses
        self.__executemany(sql, data)


    def insert_project(self, data):
        sql = """INSERT INTO projects 
        (user_id, project_name, description, url, foto,  status_id) 
        values(?, ?, ?, ?, ?, ?)"""
        self.__executemany(sql, data)


    def insert_skill(self, user_id, project_name, skill):
        sql = 'SELECT project_id FROM projects WHERE project_name = ? AND user_id = ?'
        project_id = self.__select_data(sql, (project_name, user_id))[0][0]
        skill_id = self.__select_data('SELECT skill_id FROM skills WHERE skill_name = ?', (skill,))[0][0]
        data = [(project_id, skill_id)]
        sql = 'INSERT OR IGNORE INTO project_skills VALUES(?, ?)'
        self.__executemany(sql, data)


    def get_statuses(self):
        sql="SELECT status_name from status"
        return self.__select_data(sql)
        

    def get_status_id(self, status_name):
        sql = 'SELECT status_id FROM status WHERE status_name = ?'
        res = self.__select_data(sql, (status_name,))
        if res: return res[0][0]
        else: return None

    def get_projects(self, user_id):
        sql="""SELECT * FROM projects 
        WHERE user_id = ?"""

        return self.__select_data(sql, data = (user_id,))
        
    def get_project_id(self, project_name, user_id):
        return self.__select_data(sql='SELECT project_id FROM projects WHERE project_name = ? AND user_id = ?  ', data = (project_name, user_id,))[0][0]
        
    def get_skills(self):
        return self.__select_data(sql='SELECT * FROM skills')
    
    def get_project_skills(self, project_name):
        res = self.__select_data(sql='''SELECT skill_name FROM projects 
        JOIN project_skills ON projects.project_id = project_skills.project_id 
        JOIN skills ON skills.skill_id = project_skills.skill_id 
        WHERE project_name = ?''', data = (project_name,) )
        return ', '.join([x[0] for x in res])
    
    def get_project_info(self, user_id, project_name):
        sql = """
        SELECT project_name, description, url, status_name FROM projects 
        JOIN status ON
        status.status_id = projects.status_id
        WHERE project_name=? AND user_id=?
        """
        return self.__select_data(sql=sql, data = (project_name, user_id))


    def update_projects(self, param, data):
        sql = f"""UPDATE projects SET {param} = ? 
        WHERE project_name = ? AND user_id = ?"""
        self.__executemany(sql, [data]) 


    def delete_project(self, user_id, project_id):
        sql = """DELETE FROM projects 
        WHERE user_id = ? AND project_id = ? """
        self.__executemany(sql, [(user_id, project_id)])
    
    def delete_skill(self, skill_name, skill_id):
        sql = """DELETE FROM skills 
        WHERE skill_id = ? AND skill_name = ? """
        self.__executemany(sql, [(skill_id, skill_name)])


if __name__ == '__main__':
    manager = DB_Manager(DATABASE)
    manager.create_tables()
    manager.default_insert()
    # data_ = (1, 'Test Project', 'https', 1)
    # data2_ = (1, 'Test Project2', 'https', 2)
    # manager.insert_project([data_])
    # manager.insert_skill(1, 'Test Project', 'Python')
    # print(manager.get_statuses())
    # print(manager.get_status_id('В процессе разработки'))
    # print(manager.get_projects(1))
    # print(manager.get_project_id('Test Project', 1))
    # print(manager.get_skills())
    # print(manager.get_project_skills('Test Project'))
    # print(manager.get_project_info(1, 'Test Project'))
    # manager.update_projects('description', ('Updated description', 'Test Project', 1))
    # manager.delete_skill('Python', 1)
    # manager.delete_project(1, 1)

    manager.alter_table('projects', 'foto', 'TEXT')
    manager.insert_project([(1, 'TG_Portfolio', 'Моё портфолио дб с выводом в тг', 'https://github.com/murmotiklapka/TG_Portfolio.git', 'https://github.com/murmotiklapka/TG_Portfolio/blob/main/shot_260924_213036.png', 2)])
    manager.insert_project([(1, 'TG_Pokemon', 'Игра про покемонов', 'https://github.com/murmotiklapka/TG_Pokemon.git', 'https://github.com/murmotiklapka/TG_Pokemon/blob/main/shot_260924_213316.png', 5)])
    manager.insert_project([(1, 'TG-bot-', 'Определяет вид техники', 'https://github.com/murmotiklapka/TG-bot-.git', '', 5)])
    manager.insert_project([(1, 'finall-progect', 'Опредиление углеродного следа оставляймым вами', 'https://github.com/murmotiklapka/finall-progect.git', '', 5)])
    manager.insert_project([(1, 'TG_Translate', 'Транслейт', 'https://github.com/murmotiklapka/TG_Translate.git', '', 3)])
    manager.insert_project([(1, 'TG-ban', 'I ban you', 'https://github.com/murmotiklapka/TG-ban.git', '', 5)])
    manager.insert_project([(1, 'TG_Viktorina', 'Просто викторина', 'https://github.com/murmotiklapka/TG_Viktorina.git', '', 5)])
    manager.insert_project([(1, 'micro-site0-2', '', 'https://github.com/murmotiklapka/micro-site0-2.git', '', 3)])
    manager.insert_project([(1, '-_', '', 'https://github.com/murmotiklapka/-_.git', '', 3)])
