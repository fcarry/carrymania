# Agente AI con Capacidades de Email

Proyecto de Agente AI que utiliza Ollama con el modelo Phi 3 y tiene capacidades para enviar correos electrónicos a través de Gmail.

## Características

- 🤖 **Agente AI**: Utiliza Ollama con modelo Phi 3 para respuestas inteligentes
- 📧 **Envío de Emails**: Integración con Gmail SMTP para enviar correos
- 🧠 **Procesamiento de Lenguaje Natural**: Interpreta comandos en español como "envía un correo a email@ejemplo.com con el mensaje Hola Mundo"
- 🌐 **Interfaz Web**: Aplicación Streamlit con interfaz de chat
- 🔒 **Configuración Segura**: Credenciales configurables a través de la interfaz
- 🐳 **Docker**: Completamente containerizado

## Comandos de Email Soportados

El agente puede interpretar comandos naturales en español como:

- `envía un correo a test@gmail.com con el mensaje Hola Mundo`
- `manda un correo a usuario@email.com`
- `enviar correo a contacto@empresa.com con mensaje Reunión mañana`

## Configuración

### Credenciales de Gmail

1. Configura tu email de Gmail en la barra lateral
2. Usa una **contraseña de aplicación** de Google (no tu contraseña personal)
   - Ve a tu cuenta de Google → Seguridad → Verificación en 2 pasos
   - Genera una contraseña de aplicación para "Correo"

### Docker

```bash
# Construir la imagen
docker build -t chatbotdoc-ollama-phi3-email-agent-web .

# Ejecutar el contenedor
docker run -p 8501:8501 chatbotdoc-ollama-phi3-email-agent-web
```

### Ejecución Local

```bash
# Instalar dependencias
pip install streamlit langchain langchain_community

# Ejecutar la aplicación
streamlit run chatbotdoc-ollama-phi3-email-agent-web.py
```

## Uso

1. Abre la aplicación web en `http://localhost:8501`
2. Configura tus credenciales de Gmail en la barra lateral
3. Interactúa con el agente mediante:
   - Comandos de email: `"envía un correo a destino@email.com con mensaje Tu mensaje"`
   - Chat general: cualquier pregunta o conversación

## Estructura del Proyecto

```
chatbotdoc-ollama-phi3-email-agent-web/
├── chatbotdoc-ollama-phi3-email-agent-web.py  # Aplicación principal
├── Dockerfile                                  # Configuración Docker
├── start.sh                                   # Script de inicio
├── test_email_parsing.py                      # Tests del parsing de emails
└── README.md                                  # Esta documentación
```

## Funcionalidades Técnicas

- **Parsing de Comandos**: Expresiones regulares para interpretar comandos de email
- **SMTP Gmail**: Conexión segura con autenticación
- **Manejo de Errores**: Validación de credenciales y conexiones
- **Interfaz Responsiva**: CSS personalizado siguiendo patrones del repositorio
- **Historial de Chat**: Conversaciones persistentes durante la sesión

## Seguridad

- Las credenciales se almacenan solo en la sesión (no persistentes)
- Usa contraseñas de aplicación de Google
- Conexión SMTP segura con TLS
- Validación de inputs para prevenir inyección de comandos

## Dependencias

- streamlit
- langchain
- langchain_community
- smtplib (incluido en Python)
- re (incluido en Python)

---

*Desarrollado siguiendo los patrones y convenciones del repositorio carrymania*