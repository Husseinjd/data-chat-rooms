from sqlalchemy import text

class DatabaseFunctions:
    def __init__(self, engine):
        self.engine = engine

    def get_all_functions(self):
        query = text("""
            SELECT 
                p.proname AS routine_name,
                pg_catalog.pg_get_functiondef(p.oid) AS routine_definition,
                d.description AS routine_comment
            FROM 
                pg_catalog.pg_proc p
            LEFT JOIN 
                pg_catalog.pg_namespace n ON n.oid = p.pronamespace
            LEFT JOIN 
                pg_catalog.pg_description d ON d.objoid = p.oid
            WHERE 
                n.nspname = 'public'
            ORDER BY 
                p.proname
        """)

        with self.engine.connect() as connection:
            result = connection.execute(query)
            return [
                {
                    "function_name": row[0],
                    "function_code": row[1],
                    "description": row[2],
                }
                for row in result
            ]

    def add_function(self, name, code, description):
        with self.engine.connect() as connection:
            connection.execute(text(code))
            comment_sql = f"COMMENT ON FUNCTION {name} IS '{description}';"
            connection.execute(text(comment_sql))
            connection.commit()

    def delete_function(self, name):
        with self.engine.connect() as connection:
            drop_sql = f"DROP FUNCTION IF EXISTS {name};"
            connection.execute(text(drop_sql))
            connection.commit()