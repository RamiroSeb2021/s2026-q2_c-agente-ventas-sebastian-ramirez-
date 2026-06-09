workspace "Agente de Ventas" "Modelo C4 para el agente de análisis de ventas con Streamlit, Bedrock, MCP y SQLite." {
    !identifiers hierarchical

    model {
        businessUser = person "Usuario de negocio" "Hace preguntas en lenguaje natural sobre ventas y consume respuestas, tablas, gráficos y archivos descargables."
        developer = person "Desarrollador / evaluador" "Prepara datos locales, ejecuta la app y valida el comportamiento de la entrega."

        bedrock = softwareSystem "Amazon Bedrock Runtime" "Proveedor LLM que infiere intención de salida y genera planes SQL estructurados." "AWS" {
            tags "External System,AWS"
        }

        salesAgent = softwareSystem "Agente de Ventas" "Aplicación agentic AI que responde preguntas de ventas en lenguaje natural sobre una tabla ventas local." {
            tags "Target System"

            streamlitApp = container "Aplicación web Streamlit" "Interfaz de chat; coordina el flujo agentic, muestra SQL, tablas, gráficos y descargas CSV/Excel." "Python / Streamlit" {
                tags "Web Application"

                chatUi = component "Streamlit Chat UI" "Captura preguntas, mantiene estado de chat y renderiza SQL, tablas, gráficos y descargas." "app.py / Streamlit"
                graphBoundary = component "Sales Agent Graph Boundary" "Expone el punto de entrada LangGraph para responder preguntas de ventas." "LangGraph"
                queryService = component "Sales Query Application Service" "Coordina el caso de uso: plan semántico, validación SQL, ejecución MCP y resultado normalizado." "Python service"
                bedrockPlanner = component "Bedrock Query Planner Adapter" "Construye prompts, invoca Bedrock y parsea planes JSON con output_type, sql y chart_type opcional." "boto3 / Bedrock Runtime"
                sqlGuard = component "SQL Safety Guard" "Restringe SQL generado a consultas SELECT seguras sobre ventas antes de ejecutar." "Python validation"
                mcpAdapter = component "MCP SQLite Query Adapter" "Invoca herramientas MCP SQLite por stdio y normaliza resultados de consulta/diagnóstico." "MCP Python SDK"
                presentationAdapter = component "Result Presentation Adapter" "Convierte resultados a tablas, gráficos Plotly y bytes CSV/Excel." "pandas / Plotly / openpyxl"
            }

            mcpConnector = container "Proceso MCP SQLite" "Conector local lanzado por la app para exponer herramientas SQLite mediante MCP." "mcp-server-sqlite / MCP stdio" {
                tags "MCP"
            }

            seedCli = container "Seed CLI" "Script reproducible que crea datos determinísticos de ejemplo para la tabla ventas." "Python / uv" {
                tags "CLI"
            }

            salesDatabase = container "Base SQLite de ventas" "Almacena la tabla ventas con vendedor, sede, producto, cantidad, precio y fecha." "SQLite" {
                tags "Database"
            }
        }

        businessUser -> salesAgent.streamlitApp.chatUi "Consulta ventas y recibe respuestas visuales" "Web browser / HTTP"
        developer -> salesAgent.streamlitApp.chatUi "Ejecuta, prueba y revisa la aplicación localmente" "CLI / local browser"
        developer -> salesAgent.seedCli "Genera o refresca datos locales" "uv run"

        salesAgent.streamlitApp.chatUi -> salesAgent.streamlitApp.graphBoundary "Envía preguntas para procesar" "Python call"
        salesAgent.streamlitApp.graphBoundary -> salesAgent.streamlitApp.queryService "Delega el caso de uso de pregunta de ventas" "Python call"
        salesAgent.streamlitApp.queryService -> salesAgent.streamlitApp.bedrockPlanner "Solicita plan semántico de salida y SQL" "Python call"
        salesAgent.streamlitApp.bedrockPlanner -> bedrock "Invoca el modelo para generar plan estructurado" "AWS SDK / boto3"
        salesAgent.streamlitApp.queryService -> salesAgent.streamlitApp.sqlGuard "Valida SQL antes de ejecutar" "Python call"
        salesAgent.streamlitApp.queryService -> salesAgent.streamlitApp.mcpAdapter "Ejecuta SQL validado de solo lectura" "Python call"
        salesAgent.streamlitApp.mcpAdapter -> salesAgent.mcpConnector "Invoca herramientas SQLite" "MCP stdio"
        salesAgent.mcpConnector -> salesAgent.salesDatabase "Consulta la tabla ventas" "SQLite"
        salesAgent.seedCli -> salesAgent.salesDatabase "Crea esquema y carga ventas determinísticas" "SQLite"
        salesAgent.streamlitApp.chatUi -> salesAgent.streamlitApp.presentationAdapter "Solicita tabla, gráfico o exportación" "Python call"
    }

    views {
        systemContext salesAgent "C1-SystemContext" {
            include businessUser
            include developer
            include salesAgent
            include bedrock
            autoLayout lr
        }

        container salesAgent "C2-Containers" {
            include businessUser
            include developer
            include bedrock
            include salesAgent.streamlitApp
            include salesAgent.mcpConnector
            include salesAgent.seedCli
            include salesAgent.salesDatabase
            autoLayout lr
        }

        component salesAgent.streamlitApp "C3-StreamlitComponents" {
            include businessUser
            include developer
            include bedrock
            include salesAgent.streamlitApp.chatUi
            include salesAgent.streamlitApp.graphBoundary
            include salesAgent.streamlitApp.queryService
            include salesAgent.streamlitApp.bedrockPlanner
            include salesAgent.streamlitApp.sqlGuard
            include salesAgent.streamlitApp.mcpAdapter
            include salesAgent.streamlitApp.presentationAdapter
            include salesAgent.mcpConnector
            include salesAgent.salesDatabase
            include salesAgent.seedCli
            autoLayout lr
        }

        styles {
            element "Person" {
                shape person
                background #08427b
                color #ffffff
            }

            element "External System" {
                background #999999
                color #ffffff
            }

            element "AWS" {
                background #ff9900
                color #000000
            }

            element "Component" {
                background #85bbf0
                color #000000
            }

            element "Web Application" {
                background #1168bd
                color #ffffff
            }

            element "MCP" {
                background #6b46c1
                color #ffffff
            }

            element "CLI" {
                background #455a64
                color #ffffff
            }

            element "Database" {
                shape cylinder
                background #2e7d32
                color #ffffff
            }
        }
    }

    configuration {
        scope softwaresystem
    }
}
