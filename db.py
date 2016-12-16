import psycopg2
import dj_database_url
import settings
import logging
class db():

    def __init__(self):
        self.db_info = dj_database_url.config(default=settings.db_url)
        self.conn = None

    def connect(self):
        try:
            self.conn = psycopg2.connect(database=self.db_info.get('NAME'),
                        user=self.db_info.get('USER'),
                        password=self.db_info.get('PASSWORD'),
                        host=self.db_info.get('HOST'),
                        port=self.db_info.get('PORT'))
        except:
            # logger
            print 'error connection'

    def disconnect(self):
        try:
            self.conn.close()
        except:
            print 'error disconnection'