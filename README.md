El repositorio contiene pruebas y prototipos usando IA, particularmente hasta el momento prototipos usando LLMs de ChatGPT y DeepSeek.
Los diferentes prototipos buscan cubrir features diferentes

El foco es lograr realizar RAG tanto con ChatGPT mediante api y tanto con Ollama y DeepSeek R1 para correr local.
Los diferentes prototipos se entrenan con tu documentacion y responden en base a ella, tiene muchas aplicaciones posibles.

El RAG Retrieval-Augmented Generation se realiza mediante la particion de los documentos en chunks que luego son salvados a una base de datos vectorial a la cual el LLM podra usar como contexto para saber que responder.

##chatbotdoc-chatgpt-api
Docker que expone una api rest para consultar al sistema RAG entrenado en tus ducumentos
Previamente en la carpeta /data subir tus arhivos con los que sera entrenado el modelo y respondera sobre ellos.
Lo puedes usar en conbinacion con la extension de visal code que implementa un chat embebido en Visual Code y que interactua con la API del RAG en el Docker.

##chatbotdoc-chatgpt-cache-web            
Docker que expone una web  para consultar al sistema RAG entrenado en tus ducumentos
Previamente en la carpeta /data subir tus arhivos con los que sera entrenado el modelo y respondera sobre ellos.

##chatbotdoc-chatgpt-web                  
Docker que expone una web  para consultar al sistema RAG entrenado en el documento PDF que le subas a la web.

##chatbotdoc-ollama-deepseek-r1-api       
Docker que expone una api rest para consultar al sistema RAG entrenado en tus ducumentos
Previamente en la carpeta /data subir tus arhivos con los que sera entrenado el modelo y respondera sobre ellos.
Lo puedes usar en conbinacion con la extension de visal code que implementa un chat embebido en Visual Code y que interactua con la API del RAG en el Docker.

##chatbotdoc-ollama-deepseek-r1-cache-web
Docker que expone una web  para consultar al sistema RAG entrenado en tus ducumentos
Previamente en la carpeta /data subir tus arhivos con los que sera entrenado el modelo y respondera sobre ellos.

##chatbotdoc-ollama-deepseek-r1-web
Docker que expone una web  para consultar al sistema RAG entrenado en el documento PDF que le subas a la web.

##extensionvs
Extension para generar un chat dentro de visual code que interactue con los dos modelos que exponen api.

==========================

The repository contains tests and prototypes using AI, particularly so far prototypes using LLMs from ChatGPT and DeepSeek.
The different prototypes aim to cover various features:

The focus is to achieve RAG (Retrieval-Augmented Generation) both with ChatGPT via API and with Ollama and DeepSeek R1 for local execution.
The different prototypes are trained with your documentation and respond based on it, offering many possible applications.

The RAG (Retrieval-Augmented Generation) is performed by splitting the documents into chunks, which are then saved to a vector database that the LLM can use as context to determine the appropriate response.

##chatbotdoc-chatgpt-api
A Docker container that exposes a REST API to query the RAG system trained on your documents.
Beforehand, upload your files to the /data folder, which will be used to train the model and respond to queries about them.
You can use it in combination with the Visual Studio Code extension that implements an embedded chat in Visual Studio Code and interacts with the RAG API in the Docker container.

##chatbotdoc-chatgpt-cache-web
A Docker container that exposes a web interface to query the RAG system trained on your documents.
Beforehand, upload your files to the /data folder, which will be used to train the model and respond to queries about them.

##chatbotdoc-chatgpt-web
A Docker container that exposes a web interface to query the RAG system trained on the PDF document you upload to the web interface.

##chatbotdoc-ollama-deepseek-r1-api
A Docker container that exposes a REST API to query the RAG system trained on your documents.
Beforehand, upload your files to the /data folder, which will be used to train the model and respond to queries about them.
You can use it in combination with the Visual Studio Code extension that implements an embedded chat in Visual Studio Code and interacts with the RAG API in the Docker container.

##chatbotdoc-ollama-deepseek-r1-cache-web
A Docker container that exposes a web interface to query the RAG system trained on your documents.
Beforehand, upload your files to the /data folder, which will be used to train the model and respond to queries about them.

##chatbotdoc-ollama-deepseek-r1-web
A Docker container that exposes a web interface to query the RAG system trained on the PDF document you upload to the web interface.

##extensionvs
An extension to create a chat within Visual Studio Code that interacts with both models exposing APIs.

