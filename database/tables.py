query_users = f"""
        CREATE TABLE IF NOT EXISTS users (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        TG_ID INT,
        KAITEN_API TEXT,
        KAITEN_DOMAIN TEXT,
        STATUS TEXT,
        NAME TEXT
        )
        """

query_tables = f"""
        CREATE TABLE IF NOT EXISTS tables (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        TG_ID INT,
        KAITEN_BOARD_ID
        )
        """

query_spaces = f"""
        CREATE TABLE IF NOT EXISTS spaces (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        TG_ID INT,
        KAITEN_SPACE_ID
        )
        """
    
query_users_id = f"""
        CREATE TABLE IF NOT EXISTS users_id (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        TG_ID INT,
        USER_ID INT
        )
        """