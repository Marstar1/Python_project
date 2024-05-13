import psycopg2
import json

class DBConnection:
    def __init__(self):
        try:
            f = open('db_creds.json')
            db_creds = json.load(f)
            
            self.conn = psycopg2.connect(dbname=db_creds['dbname'], host=db_creds["host"], user=db_creds["user"],
                            password=db_creds["password"], port=db_creds["port"])
            # conn.autocommit = True
            self.cur = self.conn.cursor()
            f.close()
        except Exception as Exc:
            print(Exc)
        # finally:
            
    
    def close(self):
        self.conn.close()
    

    def executeonce(self, promt: str, params: list or dict = []):
        self.cur.execute(promt, params)
        self.conn.commit()
        
    def execute(self, promt: str, params: list or dict):
        self.cur.execute(promt, params)
    
    def commit(self):
        return self.conn.commit()

    def fetchall(self):
        return self.cur.fetchall()
            