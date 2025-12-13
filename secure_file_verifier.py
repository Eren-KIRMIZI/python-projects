import hashlib
import os

def calculate_hash(file_path, algorithm="sha256", block_size=65536):
    """
    Dosyanın kriptografik hash değerini hesaplar
    """
    hash_func = hashlib.new(algorithm)

    with open(file_path, "rb") as f:
        for block in iter(lambda: f.read(block_size), b""):
            hash_func.update(block)

    return hash_func.hexdigest()


def create_hash_file(file_path, algorithm="sha256"):
    """
    Dosya için .hash dosyası oluşturur
    """
    if not os.path.exists(file_path):
        print("Dosya bulunamadı!")
        return

    hash_value = calculate_hash(file_path, algorithm)
    hash_file_path = file_path + ".hash"

    with open(hash_file_path, "w") as f:
        f.write(f"{algorithm}:{hash_value}")

    print("Hash dosyası oluşturuldu")
    print("Dosya :", file_path)
    print("Hash  :", hash_value)


def verify_file(file_path):
    """
    Dosyanın değiştirilip değiştirilmediğini kontrol eder
    """
    hash_file_path = file_path + ".hash"

    if not os.path.exists(file_path):
        print("Dosya bulunamadı!")
        return

    if not os.path.exists(hash_file_path):
        print("Hash dosyası bulunamadı!")
        return

    with open(hash_file_path, "r") as f:
        content = f.read().strip()

    algorithm, saved_hash = content.split(":")

    current_hash = calculate_hash(file_path, algorithm)

    print("Kayıtlı Hash :", saved_hash)
    print("Güncel Hash  :", current_hash)

    if current_hash == saved_hash:
        print("Dosya değişmemiş ✓")
    else:
        print("UYARI: Dosya değiştirilmiş!")


def main():
    print("Secure File Verification Tool")
    print("1 - Hash oluştur")
    print("2 - Dosya doğrula")

    choice = input("Seçim: ").strip()
    file_path = input("Dosya yolu: ").strip()

    if choice == "1":
        create_hash_file(file_path)
    elif choice == "2":
        verify_file(file_path)
    else:
        print("Geçersiz seçim")


if __name__ == "__main__":
    main()
