import sqlite3


connection = sqlite3.connect("results.sqlite")
connection.cursor().execute("""DELETE from result""")
connection.commit()