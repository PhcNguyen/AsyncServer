import asyncio  # Import asyncio to run asynchronous functions

from src.manager.mysqlite import DBManager

# Create an instance of DBManager with the database path
sql = DBManager(DBManager.db_path)

async def main():
    # Get the SQL query line for inserting an account
    query_line = await sql._queries_line(5)  # Assuming the INSERT statement is at line 2

    if query_line:
        username = 'test_user'  # Replace with the desired username
        password = 'test_password'  # Replace with the desired password
        
        # Execute the INSERT statement
        await sql.conn.execute(query_line, (username, password))
        await sql.conn.commit()  # Commit the transaction
        
        print("Account inserted successfully.")
    else:
        print("Failed to retrieve the SQL insert query.")

# Run the asynchronous main function
asyncio.run(main())