import pyaudio
import wave
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import time
import os

# Kayıt ayarları
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1  # Mono kayıt
RATE = 44100  # Örnekleme hızı
RECORD_SECONDS = 10  # Test için kısalttım (10 saniye)
INTERVAL = 20  # Test için kısalttım (20 saniye)

def record_audio(filename, duration):
    """Mikrofon kaydı yapan fonksiyon"""
    print(f"Kayıt başlatılıyor: {filename}")
    
    try:
        audio = pyaudio.PyAudio()
        
        # Mikrofon bilgisini göster
        print(f"Mikrofon cihazı: {audio.get_default_input_device_info()['name']}")
        
        # Mikrofon akışını aç
        stream = audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )
        
        frames = []
        
        # Belirtilen süre boyunca kayıt yap
        for i in range(0, int(RATE / CHUNK * duration)):
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)
            if i % 10 == 0:  # İlerleme göster
                print(f"Kayıt devam ediyor... {i}/{int(RATE / CHUNK * duration)}")
        
        print("Kayıt tamamlandı.")
        
        # Akışı kapat
        stream.stop_stream()
        stream.close()
        audio.terminate()
        
        # WAV dosyası olarak kaydet
        wf = wave.open(filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        # Dosya bilgisini göster
        file_size = os.path.getsize(filename)
        print(f"Dosya oluşturuldu: {filename} ({file_size} bytes)")
        
        return True
        
    except Exception as e:
        print(f"Kayıt hatası: {e}")
        import traceback
        traceback.print_exc()
        return False

def send_email_with_attachment(filename):
    """Ses dosyasını mail ile gönderen fonksiyon"""
    
    # Dosya var mı kontrol et
    if not os.path.exists(filename):
        print(f"HATA: {filename} dosyası bulunamadı.")
        return False
    
    # Dosya boyutu kontrol et
    file_size = os.path.getsize(filename)
    print(f"Dosya boyutu: {file_size} bytes ({file_size/1024:.2f} KB)")
    
    if file_size < 1000:
        print("UYARI: Dosya çok küçük, mail gönderilmedi.")
        return False
    
    # Gmail'in dosya boyutu limiti: 25MB
    if file_size > 25 * 1024 * 1024:
        print("UYARI: Dosya çok büyük (>25MB), Gmail göndermez.")
        return False
    
    try:
        print("Mail hazırlanıyor...")
        
        # Mail oluştur
        msg = MIMEMultipart()
        msg["Subject"] = f"Ses Kaydı - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        msg["From"] = "erencoding94@gmail.com"
        msg["To"] = "16008121072@ogr.bozok.edu.tr"
        
        # Mail gövdesi ekle
        body = f"Ses kaydı ektedir.\nDosya boyutu: {file_size/1024:.2f} KB\nKayıt tarihi: {datetime.datetime.now()}"
        msg.attach(MIMEText(body, 'plain'))
        
        # Dosyayı ekle
        print("Dosya ekleniyor...")
        with open(filename, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
        
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename={os.path.basename(filename)}"
        )
        msg.attach(part)
        
        print("SMTP bağlantısı kuruluyor...")
        # SMTP bağlantısı
        mail = smtplib.SMTP('smtp.gmail.com', 587, timeout=30)
        mail.set_debuglevel(1)  # Debug modunu aç
        mail.ehlo()
        mail.starttls()
        mail.ehlo()
        
        print("Giriş yapılıyor...")
        mail.login('erencoding94@gmail.com', 'UYGULAMA SİFRENİZ')
        
        print("Mail gönderiliyor...")
        mail.sendmail("erencoding94@gmail.com", '16008121072@ogr.bozok.edu.tr', msg.as_string())
        mail.quit()
        
        print(f"✓ Mail başarıyla gönderildi: {datetime.datetime.now()}")
        
        # Mail gönderildikten sonra dosyayı sil
        os.remove(filename)
        print(f"✓ {filename} dosyası silindi.")
        
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"SMTP Kimlik Doğrulama Hatası: {e}")
        print("Uygulama şifreniz yanlış veya süresi dolmuş olabilir.")
        return False
    except smtplib.SMTPException as e:
        print(f"SMTP Hatası: {e}")
        return False
    except Exception as e:
        print(f"Genel Mail Gönderme Hatası: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Ana program döngüsü"""
    print("="*50)
    print("Mikrofon Kaydedici başlatıldı.")
    print("Durdurmak için Ctrl+C yapın.")
    print("="*50)
    
    try:
        while True:
            # Benzersiz dosya adı oluştur
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"audio_{timestamp}.wav"
            
            print(f"\n[{datetime.datetime.now()}] Yeni kayıt döngüsü başlıyor...")
            
            # Ses kaydı yap
            if record_audio(filename, RECORD_SECONDS):
                # Mail gönder
                send_email_with_attachment(filename)
            else:
                print("Kayıt başarısız oldu, mail gönderilmedi.")
            
            # Belirtilen süre kadar bekle
            print(f"\nBekleniyor ({INTERVAL} saniye)...")
            time.sleep(INTERVAL)
            
    except KeyboardInterrupt:
        print("\n\n" + "="*50)
        print("Mikrofon Kaydedici durduruldu.")
        print("="*50)

if __name__ == "__main__":
    main()
