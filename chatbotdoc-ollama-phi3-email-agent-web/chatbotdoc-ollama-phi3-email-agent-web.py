import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage
import re
import os
import json

# Color palette following the existing pattern
primary_color = "#1E90FF"
secondary_color = "#FF6347"
background_color = "#F5F5F5"
text_color = "#4561e9"

# Custom CSS following the existing pattern
st.markdown(f"""
    <style>
    .stApp {{
        background-color: {background_color};
        color: {text_color};
    }}
    .stButton>button {{
        background-color: {primary_color};
        color: white;
        border-radius: 5px;
        border: none;
        padding: 10px 20px;
        font-size: 16px;
    }}
    .stTextInput>div>div>input {{
        border: 2px solid {primary_color};
        border-radius: 5px;
        padding: 10px;
        font-size: 16px;
    }}
    .stTextArea>div>div>textarea {{
        border: 2px solid {primary_color};
        border-radius: 5px;
        padding: 10px;
        font-size: 16px;
    }}
    .email-success {{
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }}
    .email-error {{
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }}
    </style>
""", unsafe_allow_html=True)

# Email sending function
def send_email(to_email, subject, message, smtp_server, smtp_port, from_email, password):
    """Send email via Gmail SMTP"""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add body to email
        msg.attach(MIMEText(message, 'plain'))
        
        # Gmail SMTP configuration
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Enable security
        server.login(from_email, password)
        
        # Send email
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        
        return True, "Email enviado exitosamente"
    except Exception as e:
        return False, f"Error al enviar email: {str(e)}"

# Email command parser
def parse_email_command(text):
    """Parse natural language email commands"""
    # Pattern to match email commands in Spanish
    patterns = [
        r"env[ií]a(?:\s+un)?\s+correo\s+a\s+([^\s]+@[^\s]+)(?:\s+con)?(?:\s+el)?(?:\s+mensaje)?(?:\s+[\"']?([^\"']+)[\"']?)?",
        r"manda(?:\s+un)?\s+correo\s+a\s+([^\s]+@[^\s]+)(?:\s+con)?(?:\s+el)?(?:\s+mensaje)?(?:\s+[\"']?([^\"']+)[\"']?)?",
        r"enviar\s+correo\s+a\s+([^\s]+@[^\s]+)(?:\s+con)?(?:\s+el)?(?:\s+mensaje)?(?:\s+[\"']?([^\"']+)[\"']?)?"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            email = match.group(1)
            message = match.group(2) if len(match.groups()) > 1 and match.group(2) else "Mensaje desde el agente AI"
            return email, message
    
    return None, None

# Initialize LLM
@st.cache_resource
def get_llm():
    return Ollama(model="phi3")

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'email_config' not in st.session_state:
    st.session_state.email_config = {
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'from_email': '',
        'password': ''
    }

# Streamlit app title
st.title("🤖 Agente AI con Capacidades de Email")
st.markdown("#### Agente inteligente usando Ollama Phi 3 que puede enviar correos electrónicos")

# Sidebar for email configuration
st.sidebar.header("⚙️ Configuración de Email")
st.sidebar.markdown("**Configurar credenciales de Gmail:**")

# Email configuration inputs
new_email = st.sidebar.text_input(
    "Email de Gmail:", 
    value=st.session_state.email_config['from_email'],
    placeholder="tu_email@gmail.com"
)

new_password = st.sidebar.text_input(
    "Contraseña de aplicación:", 
    type="password",
    value=st.session_state.email_config['password'],
    help="Usa una contraseña de aplicación de Google, no tu contraseña normal"
)

# Update email config
if new_email != st.session_state.email_config['from_email']:
    st.session_state.email_config['from_email'] = new_email

if new_password != st.session_state.email_config['password']:
    st.session_state.email_config['password'] = new_password

# Configuration status
if st.session_state.email_config['from_email'] and st.session_state.email_config['password']:
    st.sidebar.success("✅ Email configurado")
else:
    st.sidebar.warning("⚠️ Email no configurado")

st.sidebar.markdown("---")
st.sidebar.markdown("**Ejemplos de comandos:**")
st.sidebar.markdown("- Envía un correo a test@gmail.com con el mensaje Hola Mundo")
st.sidebar.markdown("- Manda un correo a usuario@email.com")
st.sidebar.markdown("- Enviar correo a contacto@empresa.com con mensaje Reunión mañana")

# Main chat interface
st.markdown("### 💬 Chat con el Agente")

# Display chat history
for message in st.session_state.chat_history:
    if message["role"] == "user":
        st.markdown(f"**🧑 Usuario:** {message['content']}")
    else:
        st.markdown(f"**🤖 Agente:** {message['content']}")

# User input
user_input = st.text_area(
    "Escribe tu mensaje o comando:", 
    height=100,
    placeholder="Ejemplo: Envía un correo a fcarriquiry@gmail.com con el mensaje Hola Mundo"
)

# Process user input
if st.button("📤 Enviar", type="primary"):
    if user_input.strip():
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Check if it's an email command
        email_address, email_message = parse_email_command(user_input)
        
        if email_address:
            # It's an email command
            if not st.session_state.email_config['from_email'] or not st.session_state.email_config['password']:
                response = "❌ No puedo enviar emails porque no has configurado las credenciales de Gmail en la barra lateral."
            else:
                # Send email
                success, result = send_email(
                    to_email=email_address,
                    subject="Mensaje desde Agente AI",
                    message=email_message,
                    smtp_server=st.session_state.email_config['smtp_server'],
                    smtp_port=st.session_state.email_config['smtp_port'],
                    from_email=st.session_state.email_config['from_email'],
                    password=st.session_state.email_config['password']
                )
                
                if success:
                    response = f"✅ {result}\n📧 **Destinatario:** {email_address}\n📝 **Mensaje:** {email_message}"
                else:
                    response = f"❌ {result}"
        else:
            # Regular chat with the AI
            try:
                llm = get_llm()
                
                # Create prompt for the AI agent
                prompt_template = """Eres un agente AI útil que puede ayudar con diferentes tareas. 
                
                Puedes:
                1. Responder preguntas generales
                2. Ayudar con tareas de texto
                3. Procesar comandos para enviar emails (pero solo cuando el usuario use palabras como 'envía', 'manda', 'enviar' seguido de 'correo' o 'email')
                
                Si el usuario quiere enviar un email, diles que usen comandos como:
                - "Envía un correo a [email] con el mensaje [mensaje]"
                - "Manda un correo a [email]"
                
                Pregunta del usuario: {question}
                
                Responde de manera amigable y útil en español:"""
                
                prompt = PromptTemplate.from_template(prompt_template)
                formatted_prompt = prompt.format(question=user_input)
                
                # Get AI response
                ai_response = llm.invoke(formatted_prompt)
                response = ai_response
                
            except Exception as e:
                response = f"❌ Error al procesar la consulta: {str(e)}\n\nAsegúrate de que Ollama esté ejecutándose y el modelo Phi 3 esté instalado."
        
        # Add AI response to history
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        # Refresh the page to show new messages
        st.rerun()

# Clear chat button
if st.button("🗑️ Limpiar Chat"):
    st.session_state.chat_history = []
    st.rerun()

# Information section
st.markdown("---")
st.markdown("### ℹ️ Información del Agente")
st.markdown("""
**Capacidades del agente:**
- 💬 Chat inteligente usando Ollama Phi 3
- 📧 Envío de correos electrónicos via Gmail
- 🧠 Procesamiento de lenguaje natural para comandos de email
- 🔒 Configuración segura de credenciales

**Para enviar emails:**
1. Configura tu email y contraseña de aplicación en la barra lateral
2. Usa comandos naturales como "Envía un correo a destino@email.com con el mensaje Tu mensaje aquí"

**Nota de seguridad:** Usa contraseñas de aplicación de Google, no tu contraseña personal.
""")

# Footer
st.markdown("---")
st.markdown("*Agente AI desarrollado con Streamlit, Ollama Phi 3 y capacidades de email*")