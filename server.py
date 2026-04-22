import socket
import threading

# Хранилище подключённых клиентов: {сокет: имя}
clients = {}
lock = threading.Lock()

def broadcast(message, sender_socket=None):
    """Отправляет сообщение всем клиентам, кроме отправителя (если указан)."""
    with lock:
        for client_socket, name in clients.items():
            if client_socket != sender_socket:
                try:
                    client_socket.send(message.encode('utf-8'))
                except:
                    # Если не удалось отправить — удаляем клиента позже
                    pass

def handle_client(conn, addr):
    try:
        # 1. Запрашиваем имя пользователя
        conn.send("Введите ваше имя: ".encode('utf-8'))
        name = conn.recv(1024).decode('utf-8').strip()
        if not name:
            name = f"Гость_{addr[1]}"

        with lock:
            clients[conn] = name

        print(f"[+] {name} подключился ({addr})")
        broadcast(f"** {name} присоединился к чату **", sender_socket=conn)

        # 2. Основной цикл приёма сообщений
        while True:
            msg = conn.recv(1024).decode('utf-8')
            if not msg:
                break

            # Обработка команд
            if msg.startswith('/'):
                if msg.strip() == '/users':
                    # Отправляем список имён только запросившему
                    with lock:
                        user_list = ', '.join(clients.values())
                    conn.send(f"[Сервер] В чате: {user_list}".encode('utf-8'))
                else:
                    conn.send("[Сервер] Неизвестная команда".encode('utf-8'))
            else:
                # Обычное сообщение — рассылаем всем
                broadcast(f"{name}: {msg}", sender_socket=conn)

    except Exception as e:
        print(f"[!] Ошибка с клиентом {addr}: {e}")
    finally:
        # 3. Отключение клиента
        with lock:
            if conn in clients:
                name = clients[conn]
                del clients[conn]
        print(f"[-] {name} отключился ({addr})")
        broadcast(f"** {name} покинул чат **")
        conn.close()

def start_server():
    HOST = '0.0.0.0'
    PORT = 12345

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"[*] Сервер запущен на порту {PORT}. Ожидание подключений...")

    try:
        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.daemon = True
            thread.start()
            print(f"[*] Активных потоков: {threading.active_count() - 1}")
    except KeyboardInterrupt:
        print("\n[*] Сервер остановлен.")
    finally:
        server.close()

if __name__ == "__main__":
    start_server()