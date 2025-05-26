"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const axios_1 = __importDefault(require("axios"));
function activate(context) {
    console.log('La extensión "chatbot-api-ia-extension" ha sido activada.');
    // Registrar el comando "chatbot.ask"
    let disposable = vscode.commands.registerCommand('chatbot.ask', () => {
        // Crear un Webview Panel
        const panel = vscode.window.createWebviewPanel('chatbot', // Identificador interno
        'Chatbot', // Título del panel
        vscode.ViewColumn.One, // Dónde mostrar el panel
        {
            enableScripts: true, // Permitir JavaScript en el Webview
        });
        // Establecer el contenido HTML del Webview
        panel.webview.html = getWebviewContent();
        // Manejar mensajes enviados desde el Webview
        panel.webview.onDidReceiveMessage(async (message) => {
            if (message.type === 'ask') {
                const question = message.question;
                try {
                    // Enviar la pregunta al endpoint del chatbot
                    const response = await axios_1.default.post('http://localhost:8501/ask', { question });
                    // Enviar la respuesta de vuelta al Webview
                    panel.webview.postMessage({ type: 'response', response: response.data.response });
                }
                catch (error) {
                    // Manejar errores de conexión
                    panel.webview.postMessage({ type: 'response', response: 'Error al conectar con el chatbot.' });
                }
            }
        }, undefined, context.subscriptions);
    });
    context.subscriptions.push(disposable);
}
function getWebviewContent() {
    return `
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Chatbot</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    display: flex;
                    flex-direction: column;
                    height: 100vh;
                }
                #chat {
                    flex: 1;
                    overflow-y: auto;
                    padding: 10px;
                    border-bottom: 1px solid #ccc;
                }
                #input {
                    display: flex;
                    padding: 10px;
                }
                #input input {
                    flex: 1;
                    padding: 10px;
                    font-size: 14px;
                }
                #input button {
                    padding: 10px;
                    font-size: 14px;
                    margin-left: 5px;
                }
            </style>
        </head>
        <body>
            <div id="chat"></div>
            <div id="input">
                <input type="text" id="question" placeholder="Escribe tu pregunta..." />
                <button id="send">Enviar</button>
            </div>
            <script>
                const vscode = acquireVsCodeApi();
                const chat = document.getElementById('chat');
                const input = document.getElementById('question');
                const sendButton = document.getElementById('send');

                sendButton.addEventListener('click', () => {
                    const question = input.value;
                    if (question) {
                        chat.innerHTML += '<div><strong>Tú:</strong> ' + question + '</div>';
                        input.value = '';
                        vscode.postMessage({ type: 'ask', question });
                    }
                });

                window.addEventListener('message', event => {
                    const message = event.data;
                    if (message.type === 'response') {
                        chat.innerHTML += '<div><strong>Chatbot:</strong> ' + message.response + '</div>';
                    }
                });
            </script>
        </body>
        </html>
    `;
}
function deactivate() {
    console.log('La extensión "chatbot-api-ia-extension" ha sido desactivada.');
}
//# sourceMappingURL=extension.js.map