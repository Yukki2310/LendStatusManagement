import pyodbc

server = 'tcp:cameramanagement.database.windows.net,1433'
database = 'cameraManagement_DB'
username = 'azureuser'
password = 'DBServer24712'

conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
cursor = conn.cursor()
cursor.execute("SELECT * FROM item")
for row in cursor:
    print(row)
conn.close()