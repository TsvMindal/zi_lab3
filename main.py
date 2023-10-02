import subprocess
import os
import time

# Генерирует случайный ключ, используя утилиту OpenSSL
def generate_key():
    # Создание случайного ключа с помощью утилиты openssl
    openssl_command = ["openssl", "rand", "-hex", "16"]
    key = subprocess.check_output(openssl_command, text=True).strip()
    return key

# Разбивает исходное изображение на две части: заголовок (первые 122 байта) и основную часть данных.
def split_image(image_path, header_path, data_path):
    with open(image_path, "rb") as image_file:
        image_bytes = image_file.read()
        header = image_bytes[:122]
        data = image_bytes[122:]

        with open(header_path, "wb") as header_file:
            header_file.write(header)

        with open(data_path, "wb") as data_file:
            data_file.write(data)

# Объединяет заголовок и основную часть данных из двух файлов в один файл изображения.
def merge_image(header_path, data_path, output_path):
    with open(header_path, "rb") as header_file:
        header = header_file.read()

    with open(data_path, "rb") as data_file:
        data = data_file.read()

    output_bytes = header + data

    with open(output_path, "wb") as output_file:
        output_file.write(output_bytes)

# Реализует шифрования основной части данных изображения с использованием заданного ключа и вектора инициализации.
def encrypt_image(data_path, key, iv, encrypted_data_path, aes_mode):
    start_time = time.time()
    openssl_command = [
        "openssl",
        "enc",
        f"-aes-256-{aes_mode}",
        "-pbkdf2",
        "-in", data_path,
        "-out", encrypted_data_path,
        "-K", key,
        "-iv", iv
    ]
    result = subprocess.run(openssl_command, text=True, stderr=subprocess.PIPE)
    end_time = time.time()

    if result.returncode != 0:
        print(f"Ошибка при шифровании изображения: {result.stderr}")
    else:
        print(f"Изображение успешно зашифровано в режиме {aes_mode}.")
        elapsed_time = end_time - start_time
        print(f"Время шифрования режима: {elapsed_time:.2f} секунд\n")

image_path = 'tux.bmp'

# Чтение режимов из файла aes_4v.txt
with open("aes_4v.txt", "r") as aes_modes_file:
    aes_modes = [line.strip() for line in aes_modes_file]

# Создание папки 'tux', если ее нет
if not os.path.exists("tux"):
    os.makedirs("tux")

keys = [generate_key() for _ in aes_modes]
ivs = [generate_key() for _ in aes_modes]

for i, mode in enumerate(aes_modes):
    key = keys[i]
    iv = ivs[i]

    # Разделение исходного изображения на заголовочную и основную части
    header_path = "header.bmp"
    data_path = "data.bmp"
    split_image(image_path, header_path, data_path)

    # Шифрование основной части изображения
    encrypted_data_path = os.path.join("tux", f"tux_data_{mode}.bmp")
    encrypt_image(data_path, key, iv, encrypted_data_path, mode)

    # Объединение заголовка с зашифрованной основной частью
    tux_image_path = os.path.join("tux", f"tux_{mode}.bmp")
    merge_image(header_path, encrypted_data_path, tux_image_path)

    # Удаление временных файлов
    os.remove(data_path)
    os.remove(encrypted_data_path)
