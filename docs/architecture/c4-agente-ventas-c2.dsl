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

        businessUser -> salesAgent "Consulta ventas y recibe respuestas visuales" "Web browser / HTTP"
        developer -> salesAgent "Ejecuta, prueba y revisa la aplicación localmente" "CLI / local browser"
        salesAgent -> bedrock "Solicita interpretación semántica, tipo de salida y SQL estructurado" "AWS SDK / boto3"

        businessUser -> salesAgent.streamlitApp "Consulta ventas y recibe respuestas visuales" "Web browser / HTTP"
        developer -> salesAgent.streamlitApp "Ejecuta, prueba y revisa la aplicación localmente" "CLI / local browser"
        developer -> salesAgent.seedCli "Genera o refresca datos locales" "uv run"

        salesAgent.streamlitApp -> bedrock "Solicita interpretación semántica, tipo de salida y SQL estructurado" "AWS SDK / boto3"
        salesAgent.streamlitApp -> salesAgent.mcpConnector "Ejecuta consultas SQL validadas de solo lectura" "MCP stdio"
        salesAgent.mcpConnector -> salesAgent.salesDatabase "Consulta la tabla ventas" "SQLite"
        salesAgent.seedCli -> salesAgent.salesDatabase "Crea esquema y carga ventas determinísticas" "SQLite"
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

        styles {
            element "Person" {
                shape person
                background #08427b
                color #ffffff
            }

            element "Target System" {
                background #1168bd
                color #ffffff
            }

            element "Web Application" {
                background #1168bd
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
