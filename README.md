# Airline Management System

Bu proje, bir havayolu şirketinin uçaklarını, uçuşlarını ve yolcu rezervasyonlarını yönetebilmesi için geliştirilmiş bir **Django REST Framework backend** uygulamasıdır.

API üzerinden uçak ve uçuş oluşturulabilir, rezervasyon alınabilir, uçuşların kapasitesi ve çakışmaları kontrol edilebilir. Ayrıca rota bazlı kullanım raporu oluşturulup Excel olarak dışa aktarılabilir.

Proje PostgreSQL üzerinde çalışır ve JWT authentication, Docker ve GitHub Actions CI/CD içerir.

---

## Kullanılan Teknolojiler

- Python 3.12
- Django 6.1.1
- Django REST Framework
- PostgreSQL 17
- Simple JWT
- django-filter
- Docker & Docker Compose
- Gunicorn
- openpyxl
- Postman
- GitHub Actions

---

## Proje Yapısı

```text
airline-management/
│
├── airplanes/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── flights/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── filters.py
│   └── urls.py
├── reservations/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── reports/
│   ├── models.py
│   └── management/commands/generate_route_report.py
├── config/
│
├── .github/
│   └── workflows/
│       └── deploy.yml
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── postman_collection.json
├── .env.example
└── README.md
```

Uçak, uçuş, rezervasyon ve rapor işlemleri ayrı Django app'leri içerisinde tutulur. Her kaynak kendi model, serializer, view ve URL dosyaları üzerinden yönetilir.

---

# 1. Kurulum

## Gereksinimler

Projeyi lokal olarak çalıştırmak için:

- Python 3.12+
- PostgreSQL 17+
- Git

Docker ile çalıştırmak isterseniz ayrıca Docker Desktop yeterlidir.

---

## 2. Projeyi Klonlama

```bash
git clone https://github.com/metehanayhan/airline-management.git
cd airline-management
```

---

## 3. Virtual Environment Oluşturma

### Windows

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 4. Paketleri Yükleme

```bash
pip install -r requirements.txt
```

---

# 5. PostgreSQL Veritabanını Oluşturma

Lokal PostgreSQL kullanıyorsanız önce `airline_management` isimli database oluşturun.

PostgreSQL'e bağlanıp:

```sql
CREATE DATABASE airline_management;
```

İsterseniz terminalden:

```bash
psql -U postgres
```

ardından:

```sql
CREATE DATABASE airline_management;
\q
```

---

# 6. Environment Ayarları

`.env.example` dosyasını `.env` olarak kopyalayın.

Windows:

```powershell
Copy-Item .env.example .env
```

Linux / macOS:

```bash
cp .env.example .env
```

`.env` içerisinde PostgreSQL bilgilerini kendi ortamınıza göre düzenleyin:

```env
DB_NAME=airline_management
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

SECRET_KEY=change-this-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=noreply@airline-management.local
```

`.env` dosyası Git'e gönderilmemelidir.

---

# 7. Migration

Database hazır olduktan sonra:

```bash
python manage.py migrate
```

---

# 8. İlk Kullanıcıyı Oluşturma

API JWT authentication kullandığı için önce bir kullanıcı oluşturmanız gerekir:

```bash
python manage.py createsuperuser
```

Örneğin:

```text
Username: admin
Email: admin@example.com
Password: ********
```

Bu kullanıcı hem JWT ile API'ye giriş yapmak hem de Django admin paneline erişmek için kullanılabilir.

Admin panel:

```text
http://127.0.0.1:8000/admin/
```

---

# 9. Uygulamayı Çalıştırma

```bash
python manage.py runserver
```

API:

```text
http://127.0.0.1:8000/
```

---

# Docker ile Çalıştırma

Python ve PostgreSQL'i ayrıca kurmak istemiyorsanız proje Docker Compose ile de çalıştırılabilir.

```bash
docker compose up -d --build
```

Container'ları kontrol etmek için:

```bash
docker compose ps
```

Migration:

```bash
docker compose exec web python manage.py migrate
```

İlk kullanıcı:

```bash
docker compose exec web python manage.py createsuperuser
```

Test:

```bash
docker compose exec web python manage.py test
```

Uygulama:

```text
http://127.0.0.1:8000/
```

Docker Compose PostgreSQL'i ayrı bir container olarak çalıştırır ve database verisini Docker volume içerisinde saklar.

---

# Authentication

Tüm API endpointleri authentication gerektirir.

JWT almak için:

```http
POST /api/token/
```

Request:

```json
{
    "username": "admin",
    "password": "admin"
}
```

Response içerisinden `access` ve `refresh` tokenları alınır.

API isteklerinde access token:

```http
Authorization: Bearer <access_token>
```

şeklinde kullanılır.

Access token'ın süresi dolduğunda refresh token ile yeni access token alınabilir:

```http
POST /api/token/refresh/
```

---

# Postman

Projede hazır bir Postman Collection bulunmaktadır:

```text
postman_collection.json
```

Postman'de:

**Import → File → postman_collection.json**

adımlarını izleyerek collection'ı içeri aktarabilirsiniz.

Collection içerisinde:

- Authentication
- Airplanes
- Flights
- Reservations
- Flight filters

için hazır requestler ve örnek body'ler bulunmaktadır.

## Postman ile giriş

Önce:

```text
Authentication → Login
```

requestini çalıştırın.

Login requestinde oluşturduğunuz superuser'ın kullanıcı adı ve şifresini kullanın.

Collection içerisindeki script, başarılı login sonrasında dönen:

```text
access
refresh
```

tokenlarını otomatik olarak collection variable'larına kaydeder.

Bu nedenle diğer requestlerde tokenı elle kopyalayıp yapıştırmanız gerekmez.

Access token'ın süresi dolarsa:

```text
Authentication → Refresh Token
```

requestini çalıştırmanız yeterlidir. Yeni access token otomatik olarak collection'daki `access_token` değişkenine kaydedilir.

Postman'deki `base_url` değişkenini çalıştığınız ortama göre değiştirebilirsiniz:

Lokal:

```text
http://127.0.0.1:8000
```

Deploy edilmiş sunucu:

```text
http://<server-ip>:8000
```

---

# API Endpointleri

## Airplanes

```text
GET     /airplanes/
GET     /airplanes/{id}/
GET     /airplanes/{id}/flights/
POST    /airplanes/
PATCH   /airplanes/{id}/
DELETE  /airplanes/{id}/
```

Örnek POST:

```json
{
    "tail_number": "TC-NRT01",
    "model": "Airbus A320",
    "capacity": 180,
    "production_year": 2020,
    "status": true
}
```

---

## Flights

```text
GET     /flights/
GET     /flights/{id}/
GET     /flights/{id}/reservations/
POST    /flights/
PATCH   /flights/{id}/
DELETE  /flights/{id}/
```

Örnek POST:

```json
{
    "flight_number": "TK101",
    "departure": "Heathrow Airport",
    "destination": "Istanbul Airport",
    "departure_time": "2026-09-25T10:00:00+03:00",
    "arrival_time": "2026-09-25T14:00:00+03:00",
    "airplane": 1
}
```

---

## Reservations

```text
GET     /reservations/
GET     /reservations/{id}/
POST    /reservations/
PATCH   /reservations/{id}/
```

Örnek POST:

```json
{
    "passenger_name": "Ahmet Yılmaz",
    "passenger_email": "ahmet@example.com",
    "flight": 1,
    "status": true
}
```

`reservation_code` request body içerisinde gönderilmez. Sistem tarafından otomatik oluşturulur.

Rezervasyon iptali:

```json
{
    "status": false
}
```

---

# Uçuş Filtreleri

`/flights/` endpointinde aşağıdaki filtreler kullanılabilir:

```text
GET /flights/?departure=Heathrow
GET /flights/?destination=Istanbul
GET /flights/?departure_date=2026-09-25
GET /flights/?arrival_date=2026-09-25
```

`departure` ve `destination` filtreleri:

- büyük/küçük harfe duyarsızdır
- kısmi eşleşmeyi destekler

Örneğin:

```text
/flights/?departure=istan
```

Istanbul gibi eşleşen sonuçları getirir.

Filtreler birlikte de kullanılabilir.

---

# İş Kuralları

## Airplane

- `tail_number` benzersiz olmalıdır.
- `tail_number` ve `model` boş bırakılamaz.
- `capacity` 0'dan büyük olmalıdır.
- `production_year` geçerli bir yıl olmalıdır.

## Flight

- `flight_number` benzersiz olmalıdır.
- Departure ve destination boş bırakılamaz.
- Arrival zamanı departure zamanından sonra olmalıdır.
- Aynı uçak üzerinde çakışan uçuş oluşturulamaz.
- Aynı uçak üzerindeki iki uçuş arasında en az 1 saat bulunmalıdır.

Çakışma durumunda API `400 Bad Request` döndürür.

## Reservation

- Yolcu adı zorunludur.
- Email formatı kontrol edilir.
- Aktif rezervasyon sayısı uçağın kapasitesini aşamaz.
- İptal edilmiş rezervasyonlar kapasite hesabına dahil edilmez.
- `reservation_code` sistem tarafından otomatik oluşturulur.
- Reservation code benzersizdir ve client tarafından değiştirilemez.

---

# Rezervasyonlarda Eşzamanlılık Kontrolü

Rezervasyon oluşturulurken aynı anda birden fazla isteğin kapasiteyi aşmasını önlemek için database transaction kullanılır.

İlgili flight:

```python
select_for_update()
```

ile transaction süresince kilitlenir.

Kapasite kontrolü transaction içerisinde tekrar yapılır ve ardından rezervasyon oluşturulur.

---

# Email Confirmation

Rezervasyon oluşturulduğunda yolcuya confirmation email gönderilebilir.

Email içerisinde:

- Reservation code
- Flight number
- Route
- Departure time
- Arrival time

bilgileri bulunur.

Local geliştirmede email göndermek yerine terminalde görmek için:

```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

kullanılabilir.

SMTP kullanmak için `.env`:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-user
EMAIL_HOST_PASSWORD=your-password
DEFAULT_FROM_EMAIL=noreply@example.com
```

SMTP şifreleri repository'ye gönderilmemelidir.

---

# Route Report

Rota kullanım raporu şu komutla oluşturulur:

```bash
python manage.py generate_route_report
```

Docker:

```bash
docker compose exec web python manage.py generate_route_report
```

Varsayılan Excel dosyası:

```text
route_report.xlsx
```

Farklı bir dosya yolu vermek için:

```bash
python manage.py generate_route_report --output reports/route_report.xlsx
```

Rapor her:

```text
departure + destination
```

kombinasyonu için şu bilgileri hesaplar:

```text
total_flights
total_seats
used_seats
occupancy_rate
most_used_plane_model
```

Örneğin:

```text
Istanbul → London

Flights: 12
Total Seats: 2160
Used Seats: 1740
Occupancy: 80.56%
Most Used Plane: Airbus A320
```

Sonuçlar `RouteReport` tablosuna kaydedilir.

Komut tekrar çalıştırıldığında aynı rota için yeni kayıt oluşturmak yerine mevcut kayıt güncellenir.

Excel dosyası `openpyxl` kullanılarak oluşturulur ve başlık satırı, filtreleme, sütun genişlikleri ve sabit başlık satırı gibi temel formatlamalar içerir.

### Performans

Route report aggregation işlemleri database tarafında Django ORM ile yapılır.

Kullanılan yapılar:

```python
values()
annotate()
Count()
Sum()
```

Raw SQL kullanılmaz ve 10.000+ uçuş için tüm Flight kayıtları tek tek Python tarafına çekilmez.

---

# Testler

Projede Django REST Framework test altyapısı kullanılarak toplam **32 test** bulunmaktadır.

Testler temel olarak:

- Airplane CRUD
- Airplane validation
- Flight CRUD
- Flight time validation
- Flight conflict kontrolü
- Flight filtering
- Reservation CRUD
- Reservation code generation
- Reservation code immutability
- Reservation capacity kontrolü
- Cancelled reservation davranışı
- Email validation
- Route report
- Route report update/upsert
- Excel export

senaryolarını kapsar.

Tüm testleri çalıştırmak için:

```bash
python manage.py test
```

Docker ile:

```bash
docker compose exec web python manage.py test
```

Başarılı bir çalıştırmada:

```text
Found 32 test(s).
...
Ran 32 tests
OK
```

şeklinde sonuç alınır.

Testler kendi test database'lerini kullanır; mevcut development database'inizdeki verileri değiştirmez.

---

# Deployment

Uygulama Docker Compose kullanılarak Linux tabanlı bir sunucu/VM üzerinde çalıştırılabilir.

Production ortamında temel yapı:

```text
GitHub
   ↓
GitHub Actions
   ↓
Linux VM
   ↓
Docker Compose
   ├── Django + Gunicorn
   └── PostgreSQL
```

Sunucuda temel kurulum:

```bash
git clone <repository-url>
cd airline-management
```

Environment dosyasını oluşturduktan sonra:

```bash
docker compose up -d --build
```

Migration:

```bash
docker compose exec web python manage.py migrate
```

Django kontrolü:

```bash
docker compose exec web python manage.py check
```

Container durumu:

```bash
docker compose ps
```

Production ortamında:

```env
DEBUG=False
```

kullanılmalıdır.

PostgreSQL container'ı dışarıya açılmadan yalnızca Docker network üzerinden Django container'ı tarafından kullanılabilir.

## AWS EC2

Proje AWS EC2 üzerinde Ubuntu tabanlı bir sanal makineye deploy edilmiştir.

Sunucuda:

```text
AWS EC2
   └── Docker Compose
       ├── Django + Gunicorn
       └── PostgreSQL
```

uygulama yapısı kullanılmaktadır.

EC2 sunucusuna bağlandıktan sonra uygulama dizininde temel kontroller:

```bash
cd ~/airline-management
docker compose ps
docker compose exec web python manage.py check
```

CI/CD deployment aşaması da aynı EC2 sunucusunu günceller.

---

# CI/CD

Projenin GitHub Actions workflow'u:

```text
.github/workflows/deploy.yml
```

dosyasında bulunur.

`main` branch'ine push yapıldığında workflow otomatik olarak çalışır.

Akış:

```text
git push
   ↓
Run Tests
   ↓
Tests başarılıysa
   ↓
SSH ile sunucuya bağlan
   ↓
git pull
   ↓
Docker image build
   ↓
docker compose up -d
   ↓
migrate
   ↓
Django check
```

Testler başarısız olursa deployment aşamasına geçilmez.

GitHub Actions tarafında kullanılan secret'lar:

```text
EC2_HOST
EC2_USER
EC2_SSH_KEY
```

SSH private key repository içerisinde tutulmaz.

---

# Environment ve Güvenlik

Aşağıdaki dosya ve bilgileri repository'ye göndermeyin:

```text
.env
*.pem
SECRET_KEY
Database passwords
SMTP passwords
Cloud credentials
SSH private keys
```

Bu nedenle `.gitignore` içerisinde environment dosyaları, Python cache dosyaları, IDE dosyaları, generated report ve private key dosyaları hariç tutulmalıdır.

---

# Hızlı Başlangıç

Projeyi ilk kez çalıştırmak için temel akış:

```bash
git clone <repository-url>
cd airline-management

python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Paketleri yükleyin:

```bash
pip install -r requirements.txt
```

PostgreSQL'de database oluşturun:

```sql
CREATE DATABASE airline_management;
```

`.env` oluşturun ve database bilgilerini girin.

Migration:

```bash
python manage.py migrate
```

İlk kullanıcı:

```bash
python manage.py createsuperuser
```

Sunucuyu başlatın:

```bash
python manage.py runserver
```

Ardından Postman Collection'ı import edip:

```text
Authentication → Login
```

requestini bir kez çalıştırın.

Tokenlar otomatik kaydedildikten sonra diğer endpointleri doğrudan kullanabilirsiniz. Access token süresi dolduğunda yalnızca:

```text
Authentication → Refresh Token
```

requestini çalıştırmanız yeterlidir.
