import asyncio
import ipaddress
import concurrent.futures
import threading
from aioping import ping
import os

# Глобальный объект для синхронизации
lock = threading.Lock()
found_devices_global = []

async def async_ping(ip, timeout):
    try:
        await ping(ip, timeout=timeout)
        return ip
    except TimeoutError:
        return None

async def scan_network(ip_list, timeout):
    found_ips = []

    # Запускаем асинхронные пинг-запросы
    tasks = [async_ping(ip, timeout) for ip in ip_list]
    for future in asyncio.as_completed(tasks):
        result = await future
        if result:
            found_ips.append(result)
            with lock:
                found_devices_global.append(result)

    if found_ips:
        for ip in found_ips:
            print(f"FOUND {ip}")
    else:
        # Выводим начальный IP диапазона, если все адреса в диапазоне не найдены
        print(f"NONE {ip_list[0]}")

def generate_ip_list(start_ip, end_ip):
    """Генерирует список IP-адресов от start_ip до end_ip включительно."""
    ip_list = []
    start = int(ipaddress.IPv4Address(start_ip))
    end = int(ipaddress.IPv4Address(end_ip))

    for ip_num in range(start, end + 1):
        ip_list.append(str(ipaddress.IPv4Address(ip_num)))

    return ip_list

def worker(start_ip, end_ip, timeout):
    print(f"Scanning range: {start_ip} to {end_ip}")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Генерируем и обрабатываем IP-адреса по частям для ограничения потребления памяти
    chunk_size = 256  # Размер чанка для обработки
    start = int(ipaddress.IPv4Address(start_ip))
    end = int(ipaddress.IPv4Address(end_ip))

    for chunk_start in range(start, end + 1, chunk_size):
        chunk_end = min(chunk_start + chunk_size - 1, end)
        ip_list = generate_ip_list(str(ipaddress.IPv4Address(chunk_start)), str(ipaddress.IPv4Address(chunk_end)))
        loop.run_until_complete(scan_network(ip_list, timeout))

    # Очистка ресурсов
    loop.close()

def parallel_scan():
    # Определяем диапазоны IP-адресов для каждого потока
    ranges = [
        ("26.0.0.0", "26.63.255.255"),
        ("26.64.0.0", "26.127.255.255"),
        ("26.128.0.0", "26.191.255.255"),
        ("26.192.0.0", "26.255.255.255")
    ]

    # Настройка таймаута
    timeout = 0.25

    # Запускаем пул потоков с ограничением на количество потоков
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for start_ip, end_ip in ranges:
            future = executor.submit(worker, start_ip, end_ip, timeout)
            futures.append(future)

        # Ждём завершения всех потоков
        concurrent.futures.wait(futures)

    # Проверяем и создаем файл, если его нет
    file_path = "results.txt"
    if not os.path.exists(file_path):
        open(file_path, 'w').close()  # Создание файла, если он не существует

    # Записываем все найденные IP-адреса в файл
    with open(file_path, "w") as file:
        with lock:
            for device in found_devices_global:
                file.write(f"{device}\n")

    print("\nNetwork scan completed. Results saved to results.ipr")

if __name__ == "__main__":
    print("Starting network scan...")
    parallel_scan()
    print("Network scan completed.")
