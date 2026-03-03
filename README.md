Quản lý bài tập nhóm
1) Tổng quan

Hệ thống web Flask hỗ trợ:

Giáo viên tạo lớp (course), giao bài tập (assignment)

Học sinh nộp bài nhiều lần (file/link), có lịch sử nộp

Giáo viên chấm điểm + nhận xét

Quản lý nhóm trong lớp: tạo nhóm, thêm thành viên, giới hạn số nhóm / số người

Import danh sách lớp bằng Excel (openpyxl)

Export báo cáo CSV/Excel (openpyxl)
Cài đặt (Windows)

Bước 1 — Tạo môi trường và cài thư viện
cd mvp_groupwork_v3
py -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
copy .env.example .env
Bước 2 — Khởi tạo database (Flask-Migrate)

Chỉ chạy db init 1 lần cho lần setup đầu tiên.

python -m flask --app run.py db init
python -m flask --app run.py db migrate -m "init"
python -m flask --app run.py db upgrade
Bước 3 — Seed tài khoản từ Excel (GV + 70 HS)
python -m flask --app run.py seed-users
Bước 4 — Chạy ứng dụng
python run.py
2) Seed tài khoản từ Excel

Các file seed nằm trong thư mục seed_data/:

seed_data/teacher.xlsx — tài khoản giáo viên

seed_data/students_70.xlsx — 70 tài khoản học sinh

Chạy seed (2 cách):

python -m flask --app run.py seed-users

hoặc:

python seed_from_excel.py
Tài khoản đăng nhập mặc định

Giáo viên: teacher@test.com / 123456

Học sinh: student001@example.com … student070@example.com / 123456
