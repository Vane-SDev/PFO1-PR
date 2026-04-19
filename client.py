import socket

def iniciar_cliente() -> None:
    host = '127.0.0.1'
    port = 5000

    # Configuración del socket TCP/IP
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            
            # Conectarse al servidor
            client_socket.connect((host, port))
            print(f"Conectado exitosamente al servidor {host}:{port}")
            print("Escribí tus mensajes. Escribí 'éxito' para finalizar la sesión.\n")

            # Enviar múltiples mensajes
            while True:
                mensaje = input("Tú: ")

                if mensaje.strip().lower() == 'éxito':
                    print("Cerrando la conexión con el servidor...")
                    break

                if not mensaje.strip():
                    continue 

                client_socket.send(mensaje.encode('utf-8'))
                
                # Mostrá la respuesta del servidor para cada mensaje
                respuesta = client_socket.recv(1024).decode('utf-8')
                print(f"Servidor: {respuesta}")

    except ConnectionRefusedError:
        print("Error de conexión: El servidor no responde. Verificá que server.py esté en ejecución.")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

if __name__ == "__main__":
    iniciar_cliente()