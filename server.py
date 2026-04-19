import socket
import sqlite3
import datetime
import sys

# Configuración global
HOST = '127.0.0.1'
PORT = 5000
DB_NAME = 'chat_mensajes.db'

def inicializar_db() -> None:
    # Inicializar la base de datos
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mensajes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contenido TEXT NOT NULL,
                    fecha_envio TEXT NOT NULL,
                    ip_cliente TEXT NOT NULL
                )
            ''')
            conn.commit()
            print("Base de datos inicializada correctamente.")
    except sqlite3.Error as e:
        # Manejar errores: DB no accesible
        print(f"Error crítico: DB no accesible. Detalle: {e}")
        sys.exit(1)

def guardar_mensaje(contenido: str, ip_cliente: str) -> bool:
    # Guardar cada mensaje en una DB SQLite
    try:
        fecha_actual = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO mensajes (contenido, fecha_envio, ip_cliente) VALUES (?, ?, ?)',
                (contenido, fecha_actual, ip_cliente)
            )
            conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error al escribir en la base de datos: {e}")
        return False

def inicializar_socket(host: str, port: int) -> socket.socket | None:
    # Configuración del socket TCP/IP
    try:
        # Inicializar el socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        server_socket.bind((host, port))
        server_socket.listen(5)
        print(f"Servidor configurado y escuchando en {host}:{port}")
        return server_socket
    except socket.error as e:
        # Manejar errores: Puerto ocupado
        print(f"Error crítico: No se pudo iniciar el socket. ¿El puerto {port} está ocupado? Detalle: {e}")
        return None

def aceptar_conexiones(server_socket: socket.socket) -> None:
    # Aceptar conexiones y recibir mensajes
    print("Esperando conexiones entrantes...")
    try:
        while True:
            client_socket, client_address = server_socket.accept()
            ip_cliente = client_address[0]
            print(f"\n[+] Nueva conexión establecida desde: {ip_cliente}")

            try:
                while True:
                    data = client_socket.recv(1024)
                    if not data:
                        break 
                    
                    mensaje = data.decode('utf-8').strip()
                    print(f"[{ip_cliente}] dice: {mensaje}")

                    if guardar_mensaje(mensaje, ip_cliente):
                        # Responde al cliente
                        respuesta = f"Mensaje recibido: {mensaje}"
                        client_socket.send(respuesta.encode('utf-8'))
                    else:
                        client_socket.send("Error: No se pudo guardar el mensaje en la DB.".encode('utf-8'))

            except ConnectionResetError:
                print(f"[-] El cliente {ip_cliente} forzó el cierre de la conexión.")
            finally:
                client_socket.close()
                print(f"[-] Conexión cerrada con {ip_cliente}")

    except KeyboardInterrupt:
        print("\nApagando el servidor de forma segura...")
    finally:
        server_socket.close()

if __name__ == "__main__":
    inicializar_db()
    server = inicializar_socket(HOST, PORT)
    if server:
        aceptar_conexiones(server)