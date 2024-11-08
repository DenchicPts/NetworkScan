import subprocess

def traceroute(destination, max_hops=30):
    print(f"Tracing route to {destination}...\n")

    # Команда для Windows
    command = ["tracert", destination]

    try:
        # Запускаем команду tracert
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)

        # Выводим результаты
        if result.returncode == 0:
            print(result.stdout)  # Печатаем стандартный вывод
        else:
            print(f"Ошибка при выполнении команды: {result.stderr}")

    except Exception as e:
        print(f"Ошибка: {e}")
