import psycopg2
from pydantic_ai import Agent

try:
    conn = psycopg2.connect(
        host="db.xxjbozeynifkswavtcqh.supabase.co",
        port="5432",
        dbname="postgres",
        user="postgres",
        password="tatapeque0316",
        sslmode="require"
    )
    print("Conexión exitosa")
    conn.close()
except Exception as e:
    print(f"Error de conexión: {e}")

aprendizaje_result = await Agent.run(f"""
        Entendido. Vamos a resumir y organizar la información para que sea clara y útil:

        1. **Tabla `puestos`**:
        - Contiene información sobre los puestos, incluyendo un `id` único para cada puesto.
        - Una columna relevante es `Luexes minimos` (asumo que es "Luxes mínimos"), que define el requisito mínimo para cada puesto (por ejemplo, el puesto con `id = 3` tiene un mínimo de 100 luxes).

        2. **Tabla `clientes`**:
        - Tiene una columna llamada `Puesto` que se relaciona con el `id` de la tabla `puestos`.
        - Para saber si un cliente cumple con los requisitos de su puesto, compararías el valor de `Luexes` (o similar) del cliente con el `Luexes minimos` del puesto correspondiente en la tabla `puestos`.

        3. **Consultas comunes**:
        - **Clientes que no cumplen**: Comparar los `Luexes` del cliente con los `Luexes minimos` de su puesto. Si `Luexes` del cliente es menor, no cumple.
        - **Clientes con más fallas**: Contar cuántas veces un cliente no cumplió con los requisitos de su puesto.

        4. **Relación entre tablas**:
        - La relación se basa en `puestos.id` = `clientes.Puesto`.
        
        Con todo este contexto, quiero que lo guardes para el usuario {user_id} usando la herramienta `save_context`.
        """)

        
        # 3. Guardar nuevo contexto si la IA aprende algo
        await Agent.run(f"""
        Guarda el siguiente contexto para el usuario {user_id} usando la herramienta `save_context`.

        user_id: "{user_id}"
        context_key: "db_relations"
        context_data: {{"aprendizaje": "{aprendizaje_result}"}}
        """)