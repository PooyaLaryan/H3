import pyodbc
import pandas as pd

class SQLTransaction:
    def __init__(self):
        # تنظیمات اتصال به دیتابیس
        server = '172.31.56.41'  # یا IP سرور
        database = 'master'  # نام دیتابیس
        username = 'cs_lariyan'  # نام کاربری
        password = 'ERGY4bK31U7Qd2PF6T?R_W'  # رمز عبور
        driver = '{ODBC Driver 17 for SQL Server}'  # درایور ODBC

        # ساخت رشته اتصال
        self.connection_string = f'''
            DRIVER={driver};
            SERVER={server};
            DATABASE={database};
            UID={username};
            PWD={password};
            TrustServerCertificate=yes;'''



    def execute_query(self, query) -> pd.DataFrame :
        try:
            self.connection = pyodbc.connect(self.connection_string)
            cursor = self.connection.cursor()
            cursor.execute(query)
            
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()

            df = pd.DataFrame.from_records(rows, columns=columns)

            cursor.close()
            self.connection.close()

            return df

        except Exception as e:
            print("خطا در اتصال یا اجرای کوئری:", e)
        
    
    def insert(self, insert_query, values):
        try:
            self.connection = pyodbc.connect(self.connection_string)
            cursor = self.connection.cursor()
            cursor.execute(insert_query, values)
            self.connection.commit()
            cursor.close()
            self.connection.close()
            print("✅ رکورد با موفقیت درج شد.")
        except Exception as e:
            print("❌ خطا در درج رکورد:", e)

    def insert(self, insert_query):
        try:
            self.connection = pyodbc.connect(self.connection_string)
            cursor = self.connection.cursor()
            cursor.execute(insert_query)
            self.connection.commit()
            cursor.close()
            self.connection.close()
            print("✅ رکورد با موفقیت درج شد.")
        except Exception as e:
            print("❌ خطا در درج رکورد:", e)