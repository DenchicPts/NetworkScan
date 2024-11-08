import asyncio
import subprocess
import ipaddress
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import port_scanTCP
import traceroute


def ping_ip(ip):
    try:
        # Отправляем пинг-запрос
        output = subprocess.check_output(["ping", "-n", "1", "-w", "3000", str(ip)], stderr=subprocess.STDOUT, universal_newlines=True)
        if "TTL=" in output:
            return str(ip)
    except subprocess.CalledProcessError:
        return None

def scan_network(network):
    ip_list = [str(ip) for ip in ipaddress.IPv4Network(network)]
    found_devices = []

    with ThreadPoolExecutor(max_workers=300) as executor:
        future_to_ip = {executor.submit(ping_ip, ip): ip for ip in ip_list}

        for future in as_completed(future_to_ip):
            ip = future_to_ip[future]
            result = future.result()
            if result:
                print(f"FOUND {result}")
                found_devices.append(result)
            else:
                # Выводим только если весь блок из 255 адресов пуст
                if ip.endswith(".0"):
                    print(f"NONE {ip}")

            # Очищаем память
            del future_to_ip[future]

    return found_devices

if __name__ == "__main__":
    # Диапазон IP-адресов для сканирования
    # 192.168.8.0/24 ----- 192.168.8.255
    # 192.168.0.0/16 ----- 192.168.255.255
    # 192.0.0.0/8 ----- 192.255.255.255

    #ip_range = "192.168.194.0/24"
    #devices = scan_network(ip_range)

    #with open('results.txt', 'w') as file:
    #    for device in devices:
    #        file.write(f"{device}\n")
    print("Network scan completed. Results saved to results.txt")

    ip_scan = "26.75.227.218"
    port_range = range(1, 65535)

    port_scanTCP.parallel_scan(ip_scan, port_range, workers=60)

    destination = input("Введите браузерную ссылку: ")
    traceroute.traceroute(destination)
