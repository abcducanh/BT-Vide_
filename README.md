1) Tổng quan

Hệ thống web Flask hỗ trợ các chức năng chính:

Giáo viên

Tạo lớp (Course)

Giao bài tập (Assignment)

Chấm điểm, nhận xét, theo dõi bài nộp

Học sinh

Tạo nhóm, thêm thành viên

Nộp bài nhiều lần (file hoặc link)

Xem lịch sử nộp và kết quả chấm

Khác

Import danh sách lớp bằng Excel (openpyxl)

Export báo cáo CSV/Excel (openpyxl)

2) Cài đặt (Windows)
Bước 1 — Tạo môi trường và cài thư viện

cd mvp_groupwork_v3
py -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
copy .env.example .env

Bước 2 — Khởi tạo Database (Flask-Migrate)

Chỉ chạy db init 1 lần khi setup project lần đầu.

python -m flask --app run.py db init
python -m flask --app run.py db migrate -m "init"
python -m flask --app run.py db upgrade

Bước 3 — Seed tài khoản từ Excel (GV + 70 HS)
python -m flask --app run.py seed-users

Bước 4 — Chạy ứng dụng
python run.py

3) Seed tài khoản từ Excel

Các file seed nằm trong thư mục seed_data/:

seed_data/teacher.xlsx — tài khoản giáo viên

seed_data/students_70.xlsx — 70 tài khoản học sinh

Chạy seed (1 trong 2 cách):

python -m flask --app run.py seed-users

hoặc:

python seed_from_excel.py
Tài khoản đăng nhập mặc định

Giáo viên: teacher@test.com / 123456

Học sinh: student001@example.com … student070@example.com / 123456
