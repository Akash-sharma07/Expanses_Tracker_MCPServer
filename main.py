from fastmcp import FastMCP
import sqlite3
import os

file_path = os.path.join(os.path.dirname(__file__),"expense.db")
category_path = os.path.join(os.path.dirname(__file__),"categories.json")

mcp = FastMCP("Expense_Tracker")

def create_table():
    with sqlite3.connect(file_path) as c:
        c.execute("""CREATE TABLE IF NOT EXISTS expense(
        Id INTEGER PRIMARY KEY AUTOINCREMENT,
        Date TEXT NOT NULL,
        Amount REAL NOT NULL,
        Category TEXT NOT NULL,
        SubCategory TEXT DEFAULT "",
        Note TEXT DEFAULT ""
        )""")

create_table()

@mcp.tool()
def add_expense(date,amount,category,subcategory="",note=""):
    with sqlite3.connect(file_path) as c:
        cur = c.execute("INSERT INTO expense(Date,Amount,Category,SubCategory,Note) VALUES(?,?,?,?,?)",
                        (date,amount,category,subcategory,note))
        
        return {"status":"Ok","Id":cur.lastrowid}

@mcp.tool()
def read_data(start_date,end_date):
    with sqlite3.connect(file_path) as c:
        cur = c.execute(
            "SELECT Id, Date, Amount, Category, SubCategory, Note FROM expense WHERE Date BETWEEN ? AND ? ORDER BY Id ASC",
            (start_date,end_date)
            )

        col = [d[0] for d in cur.description]
        return [dict(zip(col,r)) for r in cur.fetchall()]

@mcp.tool()
def summary(start_date,end_date,category=None):
    with sqlite3.connect(file_path) as c:
        query = "SELECT Category, SUM(Amount) as Total_amount FROM expense WHERE Date BETWEEN ? AND ?"

        parameters = [start_date,end_date]

        if category:
            query+=" AND Category = ?"
            parameters.append(category)

        query+="GROUP BY Category ORDER BY Category ASC"

        cur = c.execute(query,parameters)

        col = [d[0] for d in cur.description]
        return [dict(zip(col,r)) for r in cur.fetchall()]

@mcp.resource("expanse://categories",mime_type="application/json")
def Resource():
    # Read fresh each time so you can edit the file without restarting
    with open(category_path,"r",encoding="utf-8") as file:
        return file.read()


def main() -> None:
    mcp.run(transport="streamable-http")

if __name__=="__main__":
    main()
