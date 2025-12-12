# Arka Planda Sessiz Video Kaydı Uygulaması

Bu proje, bilgisayardaki kamerayı herhangi bir pencere açmadan, sessizce arka planda çalıştırarak video kaydı yapan basit bir Python uygulamasıdır. Program hem .py dosyası olarak çalıştırılabilir hem de PyInstaller kullanılarak .exe dosyasına dönüştürülebilir.

Oluşturulan .exe dosyası çalıştırıldığı anda kamera kaydı otomatik olarak başlar. Kullanıcı uygulamayı kapattığında veya Görev Yöneticisi üzerinden sonlandırdığında kayıt edilen video otomatik olarak klasöre kaydedilir.

Bu uygulama .exe haline getirildiğinde herhangi bir Windows bilgisayarda ek bir yazılım kurulumuna gerek olmadan çalıştırılabilir.

## Projenin Amacı

Bu proje, arka planda çalışan sessiz bir video kayıt sistemi oluşturmak için temel bir yapı sunar. İlerleyen aşamalarda kayıtlı videoların otomatik aktarılması, uzaktan erişim, gizli depolama, sunucuya yükleme gibi özelliklerle genişletilebilir.

## Kullanılan Kütüphaneler

Bu uygulama yalnızca OpenCV (cv2) kütüphanesini kullanır.

Kurulum:

```
pip install opencv-python
```

.exe oluşturmak için kullanılan ek araç:

```
pip install pyinstaller
```

## Program Nasıl Çalışır?

Kod çalıştığında:

1. "videos" adında bir klasör yoksa otomatik olarak oluşturur.
2. Kamerayı `cv2.VideoCapture()` ile başlatır.
3. Her kayıt için benzersiz bir dosya adı üretir:

   Örnek:
   ```
   record_20251213_014530.avi
   ```

4. Pencere açmadan arka planda video kaydına başlar.
5. Program kapandığında veya Görev Yöneticisinden sonlandırıldığında kayıt durur.
6. Video AVI formatında XVID codec’i ile kaydedilir. Bu codec Windows üzerinde en sorunsuz çalışan formatlardan biridir ve çoğu medya oynatıcı tarafından desteklenir.

## .exe Oluşturma

Script'i .exe dosyasına dönüştürmek için:

```
pyinstaller --onefile --noconsole videostream.py
```

Açıklama:

- `--onefile` → Tek bir .exe oluşturur.
- `--noconsole` → Çalışırken herhangi bir terminal/pencere açılmaz.

## İleride Geliştirilebilecek Özellikler

Bu temel yapı üzerine pek çok gelişmiş özellik eklenebilir:

- Otomatik veri aktarımı  
  - Kayıtlı videoları uzak bir sunucuya yüklemek  
  - FTP, SFTP veya HTTP üzerinden senkronizasyon  
- Gizli çalışma modları  
  - Windows servis gibi arka planda çalışma  
  - Belirli saatlerde otomatik kayıt  
- Hareket algılama (motion detection)  
  - Sadece hareket olduğunda kayıt alma  
- Görüntü işleme özellikleri  
  - Yüz tanıma  
  - Nesne algılama  
  - Gerçek zamanlı uyarı üretme  
- Çoklu kamera desteği  
  - Aynı anda birden fazla kameradan kayıt alma  

## Önemli Not – Kamera Flashı / LED Işığı Hakkında

Laptop bilgisayarlarda dahili kameraların yanındaki LED ışığı bulunmaktadır. Bu ışık üretici tarafından güvenlik amacıyla kamera aktif olduğunda otomatik olarak yanacak şekilde donanımsal olarak tasarlanmıştır.

Bu nedenle gizli veya LED göstermeden kayıt almak için:

- Harici (USB) bir webcam kullanılmalıdır.  
- Veya LED ışığı olmayan bir cihazda bu uygulama çalıştırılmalıdır.
