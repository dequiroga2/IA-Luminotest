from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import os
import asyncpg
from typing import List, Optional, Dict, Any
import json

load_dotenv(override=True)

mcp = FastMCP(
    name='postgres_tool',
    version="1.0.0",
    description='PostgreSQL database interaction tool',
)

# Configuración de la conexión
DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST"),
    "port": int(os.getenv("POSTGRES_PORT")),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "database": os.getenv("POSTGRES_DB"),
    "ssl": "require",  # Requerido por Supabase
    "timeout": 10,     # Timeout de conexión
    "command_timeout": 15  # Timeout para comandos
}


@mcp.tool()
async def query_database(query: str, parameters: Optional[List] = None) -> str:
    """
    Execute a SQL query against the PostgreSQL database and return results as JSON.
    
    Args:
        query: SQL query to execute
        parameters: Optional list of parameters for parameterized queries
        
    Returns:
        JSON string with query results or error message
    """
    try:
        conn = await asyncpg.connect(**DB_CONFIG)
        
        if parameters:
            results = await conn.fetch(query, *parameters)
        else:
            results = await conn.fetch(query)
            
        await conn.close()
        
        # Convertir resultados a formato JSON-friendly
        formatted_results = []
        for record in results:
            formatted_results.append(dict(record))
            
        return json.dumps(formatted_results, indent=2, ensure_ascii=False)
        
    except Exception as e:
        return f"Database error: {str(e)}"
    

@mcp.tool()
async def get_table_schema(table_name: str) -> str:
    """Obtiene el schema completo de una tabla (columnas, tipos, constraints)"""
    query = """
    SELECT 
        c.column_name,
        c.data_type,
        c.is_nullable,
        c.column_default,
        tc.constraint_type
    FROM 
        information_schema.columns c
    LEFT JOIN 
        information_schema.key_column_usage kcu
        ON c.table_name = kcu.table_name 
        AND c.column_name = kcu.column_name
    LEFT JOIN 
        information_schema.table_constraints tc
        ON kcu.constraint_name = tc.constraint_name
    WHERE 
        c.table_name = $1
    ORDER BY 
        c.ordinal_position
    """
    try:
        conn = await asyncpg.connect(**DB_CONFIG)
        results = await conn.fetch(query, table_name.lower())
        await conn.close()
        
        schema = {
            "table_name": table_name,
            "columns": [],
            "constraints": []
        }
        
        for row in results:
            column_info = {
                "name": row['column_name'],
                "type": row['data_type'],
                "nullable": row['is_nullable'] == 'YES',
                "default": row['column_default']
            }
            schema["columns"].append(column_info)
            
            if row['constraint_type']:
                schema["constraints"].append({
                    "type": row['constraint_type'],
                    "column": row['column_name']
                })
        
        return json.dumps(schema, indent=2)
        
    except Exception as e:
        return f"Error al obtener schema: {str(e)}"
    

@mcp.tool()
async def list_all_tables() -> str:
    """Lista todas las tablas en la base de datos"""
    query = """
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_type = 'BASE TABLE'
    """
    try:
        conn = await asyncpg.connect(**DB_CONFIG)
        results = await conn.fetch(query)
        await conn.close()
        return json.dumps([dict(r) for r in results], indent=2)
    except Exception as e:
        return f"Error al listar tablas: {str(e)}"
    
@mcp.tool()
async def get_full_database_schema() -> str:
    """Obtiene el schema completo de toda la base de datos"""
    try:
        # Obtener lista de tablas
        tables = json.loads(await list_all_tables())
        
        full_schema = {}
        for table in tables:
            table_name = table['table_name']
            full_schema[table_name] = json.loads(await get_table_schema(table_name))
        
        return json.dumps(full_schema, indent=2)
        
    except Exception as e:
        return f"Error al obtener schema completo: {str(e)}"
    
# ... (imports existentes)

@mcp.tool()
async def save_context(
    user_id: str,
    context_key: str,
    context_data: dict
) -> str:
    """
    Guarda contexto en la base de datos para un usuario.
    Ejemplo de uso:
    await save_context("user123", "db_relations", {"tablas": ["clientes", "puestos"], "relacion": "codigo_cliente"})
    """
    query = """
    INSERT INTO ai_context_memory (user_id, context_key, context_data)
    VALUES ($1, $2, $3)
    ON CONFLICT (user_id, context_key) 
    DO UPDATE SET context_data = $3, updated_at = NOW()
    """
    try:
        await query_database(query, [user_id, context_key, json.dumps(context_data)])
        return "Contexto guardado exitosamente"
    except Exception as e:
        return f"Error al guardar contexto: {str(e)}"

@mcp.tool()
async def load_context(
    user_id: str,
    context_key: str
) -> str:
    """
    Carga contexto desde la base de datos.
    Retorna un JSON string o un dict vacío si no hay datos.
    """
    query = """
    SELECT context_data FROM ai_context_memory
    WHERE user_id = $1 AND context_key = $2
    """
    result = await query_database(query, [user_id, context_key])
    return result if result else "{}"




if __name__ == "__main__":
    mcp.run()