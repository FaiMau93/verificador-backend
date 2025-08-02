from flask import Flask, request, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# === Configuración inicial ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(credentials)

# ID del documento (sacado de la URL de tu hoja de cálculo)
spreadsheet_id = "1tFeRzZyOKojWQW8vHA3m3ssv5_OFPFAtdYXpCBeZ6qQ"
worksheet = client.open_by_key(spreadsheet_id).sheet1

app = Flask(__name__)

@app.route("/verificar", methods=["POST"])
def verificar():
    data = request.get_json()
    clave = data.get("clave", "").strip().upper()  # Forzar mayúsculas

    if not clave:
        return jsonify({"success": False, "message": "Clave vacía"}), 400

    try:
        celdas = worksheet.col_values(1)  # Columna A = claves
        if clave in celdas:
            fila = celdas.index(clave) + 1
            valores = worksheet.row_values(fila)
            return jsonify({
                "success": True,
                "datos": {
                    "clave": valores[0],
                    "entropia": valores[1],
                    "usuario_cliente": valores[2],
                    "fecha_compra": valores[3]
                }
            })
        else:
            return jsonify({"success": False, "message": "Clave no encontrada"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
