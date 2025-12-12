# II3160 - Smart Parking Management System

## Fitur Utama

* **Autentikasi Terpusat**: Login/Register menggunakan JWT token dengan dukungan *Role-Based Access Control* (PETUGAS, PENGGUNA).
* **Manajemen Kendaraan**: Kelola data dan kepemilikan kendaraan pengguna (mobil/motor).
* **Pengelolaan Slot**: *Full CRUD* untuk slot parkir, termasuk data sensor (ultrasonik/kamera/infrared).
* **Sesi Parkir**: Otomasi *Check-in/Check-out* dengan perhitungan tarif dan durasi parkir *real-time*.
* **Kualitas Kode**: **236 Unit Tests** dengan cakupan **95%+**, mencakup *edge cases* dan *error handling*.
* **CI/CD**: Pipeline otomatis untuk *testing* dan *linting* via GitHub Actions.

## TechStack

* **Framework**: FastAPI 0.121+
* **Autentikasi**: JWT (python-jose)
* **Testing**: Pytest + Coverage
* **Integrasi**: GitHub Actions

## How to Run

### 1. Prerequisite

* Python 3.11 atau lebih tinggi
* pip package manager

### 2. Instalation

```bash
# Clone repository
git clone [https://github.com/desatidinda/II3160-18223110.git](https://github.com/desatidinda/II3160-18223110.git)
cd II3160-18223110

# Install dependensi
pip install -r requirements.txt
```
### 3. Run Program

```bash
# Development server (dari root project)
cd src
python -m uvicorn main:app --reload --port 8000
```
Akses API:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 4. Run Test

``` bash
# Jalankan semua tes (dari root project)
python -m pytest tests/ -v

# Jalankan dengan laporan coverage (termasuk baris yang terlewat)
python -m pytest tests/ --cov=src/manajemen_parkir --cov-report=term-missing
```

## Test Coverage

Current coverage: **95%**

| Layer | Coverage |
|-------|----------|
| Domain | 100% |
| Infrastructure | 100% |
| Application | 97% |
| API | 93% |

## Test Statistics

| Metrik | Jumlah |
| :--- | :--- |
| Total Tes | 236 |
| Tingkat Keberhasilan | 100% |
| Edge Cases | 23 tes |
| Error Handling | 7 tes |
