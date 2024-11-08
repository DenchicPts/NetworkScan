import socket
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

def check_port(ip, port, open_ports):
    """Проверка порта без асинхронности и добавление в список открытых портов."""
    try:
        with socket.create_connection((ip, port), timeout=1):
            print(f"Порт {port} на {ip} открыт")
            open_ports.append(port)  # Добавляем открытый порт в список
    except (socket.timeout, ConnectionRefusedError):
        pass  # Порт закрыт

def scan_ports(ip, ports):
    """Сканирование портов с использованием потоков и сохранение открытых портов в переменную."""
    open_ports = []
    with ThreadPoolExecutor(max_workers=100) as executor:
        executor.map(lambda port: check_port(ip, port, open_ports), ports)
    return open_ports

def run_port_scan(ip, ports):
    """Запускаем сканирование и возвращаем найденные открытые порты."""
    return scan_ports(ip, ports)

def parallel_scan(ip, ports, workers=4):
    """Параллельное сканирование с использованием процессов и запись результатов в файл."""
    port_chunks = [ports[i::workers] for i in range(workers)]  # Разделяем порты на группы
    open_ports = []  # Список для хранения всех открытых портов

    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(run_port_scan, ip, chunk) for chunk in port_chunks]
        for future in futures:
            open_ports.extend(future.result())  # Объединяем результаты в общий список

    # Удаляем дубликаты
    open_ports = sorted(set(open_ports))

    # Сохраняем результаты в файл
    file_path = f"OPEN_PORTS/{ip}_scan.txt"
    with open(file_path, "w") as file:
        for port in open_ports:
            file.write(f"Порт {port} на {ip} открыт\n")
    print(f"Результаты сохранены в {file_path}")
