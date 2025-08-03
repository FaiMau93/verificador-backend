from flask import Flask, request, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from flask_cors import CORS  # <-- NUEVO: Importamos la extensión

# === Configuración inicial ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("/etc/secrets/creds.json", scope)
client = gspread.authorize(credentials)

# ID del documento
spreadsheet_id = "1tFeRzZyOKojWQW8vHA3m3ssv5_OFPFAtdYXpCBeZ6qQ"
worksheet = client.open_by_key(spreadsheet_id).sheet1

app = Flask(__name__)
CORS(app) # <-- NUEVO: Inicializamos CORS para permitir peticiones del frontend

@app.route("/")
def home():
    return "Backend verificador está activo y funcionando 🔥"

@app.route("/verificar", methods=["POST"])
def verificar():
    data = request.get_json()
    clave = data.get("clave", "").strip().upper()  # Forzar mayúsculas

    if not clave:
        return jsonify({"success": False, "message": "Clave vacía"}), 400

    try:
        celdas = worksheet.col_values(1)  # Columna A
        if clave in celdas:
            fila = celdas.index(clave) + 1
            valores = worksheet.row_values(fila)

            # Validar longitud de la fila para incluir la nueva columna de la imagen
            # (Ahora se esperan 4 valores en la hoja: Columna A, B, C y D)
            if len(valores) < 4:
                return jsonify({"success": False, "message": "Datos incompletos en la hoja"}), 500

            return jsonify({
                "success": True,
                "datos": {
                    "clave": valores[0],
                    "entropia": valores[1],
                    "usuario_cliente": valores[2],
                    "url_foto": valores[3]  # <--- NUEVO: Lee la Columna D (índice 3)
                }
            })
        else:
            return jsonify({"success": False, "message": "Clave no encontrada"}), 404
    except Exception:
        return jsonify({"success": False, "message": "Error interno del servidor"}), 500

if __name__ == "__main__":
    app.run()
