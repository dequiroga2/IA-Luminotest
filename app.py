import os
import asyncio
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from dotenv import load_dotenv
import json

load_dotenv(override=True)

deepseek_provider = OpenAIProvider(
    base_url="https://api.deepseek.com",
    api_key=os.environ["DEEPSEEK_API_KEY"]
)

deepseek_chat_model = OpenAIModel(
    'deepseek-chat',
    provider=deepseek_provider
)

exa_server = MCPServerStdio(
    'python',
    ['busqueda.py']
)

python_tool_server = MCPServerStdio(
    'python',
    ['python_tool.py']
)

postgres_tool_server = MCPServerStdio(
    'python',
    ['postgres_tool.py']
)

agent = Agent(
    deepseek_chat_model,
    mcp_servers=[exa_server, python_tool_server, postgres_tool_server],
    retries=3,
    #system_prompt='You are a support agent in our bank, give the customer support and judge the risk level of their query.'
)

async def main():
    async with agent.run_mcp_servers():

        # Ejemplo: ID de usuario (puede venir de un login, cookie, etc.)
        user_id = "David"
        
        # 1. Cargar contexto previo (si existe)
        context = await agent.run(f"""
        Carga el contexto para el usuario {user_id}, clave 'db_relations'.
        """)
        
        # 2. Ejecutar consulta con contexto
        result = await agent.run(f"""
        Usando este contexto: {context}.
        Ya te lo habia dicho, la columna luxes esta en la tabla puestos. Y la columna Puesto en la tabla clientes. Tienes que relacionarlas
        con el id de la tabla puestos. En este caso solo te estoy pidiendo cuales de las 28 empresas que fueron medidas en el puesto 1
        no cumplieron con lo requerido en el puesto 1. Recuerda que en la tabla puestos hay una columna llamada Luxes minimos 
        """)
        
        print(result.output)

if __name__ == "__main__":
    asyncio.run(main())







"""
Te voy a enseñar un poco sobre la tabla de puestos. Esta tabal tiene el id de cada puesto que corresponde a las
        columnas de la tabla clientes. Por ejemplo en la tabla puestos tenemos un id 3 que tiene luxes minimos de 100 como
        puedes ver en la columna Luexes minimos. Si quieres hacer una relacion con la tabla clientes, ya sabes que el id 3
        significa que en la tabla de clientes buscaras el Puesto 3 y si yo te hago la pregunta de que clientes no cumplieron con
        lo requerido en cada puesto, veras los luxes minimos de cada puesto en la tabla de puestos y los compararas con la tabla
        clientes. Y cuando te hable de quienes tuvieron mas fallas, significa cuales clientes no cumplieron con lo requerido en cada puesto. 
"""