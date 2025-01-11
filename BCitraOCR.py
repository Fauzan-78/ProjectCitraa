import cv2
import pytesseract
import os

# Konfigurasi path Tesseract jika diperlukan
# Contoh: pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def read_license_plate(image_path):
    # Membaca gambar
    image = cv2.imread(image_path)

    # Konversi ke grayscale untuk meningkatkan akurasi OCR
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Filtering gambar make metode OTSU (GAUSSIAN --> OTSU)
    # gray = cv2.GaussianBlur(gray, (5, 5), 0)
    # _, gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Gunakan Tesseract untuk membaca teks
    text = pytesseract.image_to_string(gray, config='--psm 8')

    # Membersihkan hasil
    plate_number = ''.join(filter(str.isalnum, text))

    return plate_number

def calculate_accuracy_single(detected, actual):
    """
    Menghitung akurasi berdasarkan perbandingan karakter yang cocok.
    """
    if not actual:  # Jika referensi tidak tersedia, akurasi dianggap 0
        return 0

    matched = sum(1 for d, a in zip(detected, actual) if d.lower() == a.lower())
    max_len = max(len(detected), len(actual))
    accuracy = (matched / max_len) * 100 if max_len > 0 else 0
    return accuracy

def process_images_in_folder(folder_path, output_file):
    # Daftar semua file dalam folder
    files = os.listdir(folder_path)
    image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg'))] #Ngambil Gambar Extensi png, jpg, jpeg

    if not image_files:
        print("Tidak ada file gambar ditemukan di folder.")
        return

    print(f"Memproses {len(image_files)} file gambar di folder: {folder_path}")

    results = {}
    with open(output_file, 'w') as f:
        f.write("================================================================================================\n")
        f.write("FORMAT : Nama File;   Plat Nomor Terbaca;  Akurasinya (%)\n")
        f.write("================================================================================================\n\n")

        for image_file in image_files:
            image_path = os.path.join(folder_path, image_file)
            print(f"Membaca file: {image_file}")

            try:
                detected_plate = read_license_plate(image_path)
                actual_plate = os.path.splitext(image_file)[0]  # Mengambil nama file tanpa ekstensi

                # Hitung akurasi untuk plat masing - masing
                accuracy = calculate_accuracy_single(detected_plate, actual_plate)

                # Simpan hasil ke dictionary dan file
                results[image_file] = {
                    "detected": detected_plate,
                    "actual": actual_plate,
                    "accuracy": accuracy,
                }

                # Masukin Output ke FILE
                output_line = f"{image_file};   {detected_plate};\t\t\t{accuracy:.2f}%\n"
                f.write(output_line)
                print(f"{output_line.strip()}")
            except Exception as e:
                print(f"Terjadi kesalahan saat membaca {image_file}: {e}")

    print(f"\nHasil OCR dan akurasi disimpan ke: {output_file}")

if __name__ == "__main__":
    folder_path = './dataset'
    output_file = 'hasil_ocr_tanpaFilter.txt'
    
    if not output_file.endswith(".txt"):
        output_file += ".txt"

    if os.path.isdir(folder_path):
        process_images_in_folder(folder_path, output_file)
    else:
        print("Folder tidak ditemukan. Pastikan path sudah benar.")
