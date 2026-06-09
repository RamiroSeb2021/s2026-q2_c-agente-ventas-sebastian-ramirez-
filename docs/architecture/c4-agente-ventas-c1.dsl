workspace "Agente de Ventas" "Modelo C4 para el agente de análisis de ventas con Streamlit, Bedrock, MCP y SQLite." {
    !identifiers hierarchical

    model {
        businessUser = person "Usuario de negocio" "Hace preguntas en lenguaje natural sobre ventas y consume respuestas, tablas, gráficos y archivos descargables."
        developer = person "Desarrollador / evaluador" "Prepara datos locales, ejecuta la app y valida el comportamiento de la entrega."

        salesAgent = softwareSystem "Agente de Ventas" "Aplicación agentic AI que responde preguntas de ventas en lenguaje natural sobre una tabla ventas local." {
            tags "Target System"
        }

        bedrock = softwareSystem "Amazon Bedrock Runtime" "Proveedor LLM que infiere intención de salida y genera planes SQL estructurados." "AWS" {
            tags "External System,AWS"
        }

        businessUser -> salesAgent "Consulta ventas y recibe respuestas visuales" "Web browser / HTTP"
        developer -> salesAgent "Ejecuta, prueba y revisa la aplicación localmente" "CLI / local browser"

        salesAgent -> bedrock "Solicita interpretación semántica, tipo de salida y SQL estructurado" "AWS SDK / boto3"
    }

    views {
        systemContext salesAgent "C1-SystemContext" {
            include businessUser
            include developer
            include salesAgent
            include bedrock
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

            element "External System" {
                background #999999
                color #ffffff
            }

            element "AWS" {
                background #ff9900
                color #000000
            }

        }
    }

    configuration {
        scope softwaresystem
    }
}
