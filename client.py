import socket
import threading

def receive_messages(client):
    """Фоновый поток для приёма сообщений от сервера."""
    while True:
        try:
            msg = client.recv(1024).decode('utf-8')
            if not msg:
                break
            print(f"\n{msg}\n> ", end='')
        except:
            break

def start_client():
    SERVER_IP = '10.15.30.141'   # Замените на IP сервера
    SERVER_PORT = 12345

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((SERVER_IP, SERVER_PORT))
    except ConnectionRefusedError:
        print(f"[!] Не удалось подключиться к {SERVER_IP}:{SERVER_PORT}.")
        return

    # Запускаем поток приёма сообщений
    recv_thread = threading.Thread(target=receive_messages, args=(client,))
    recv_thread.daemon = True
    recv_thread.start()

    # Основной цикл отправки
    print("[*] Подключено к серверу. Вводите сообщения (/users — список, exit — выход).")
    while True:
        msg = input("> ")
        if msg.lower() == 'exit':
            break
        if not msg:
            continue
        try:
            client.send(msg.encode('utf-8'))
        except:
            print("[!] Ошибка отправки сообщения.")
            break

    client.close()

if __name__ == "__main__":
    start_client()