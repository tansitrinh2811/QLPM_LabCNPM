import re

from fpdf import FPDF

from server_app import app, db
from server_app.models import *
from sqlalchemy.orm.exc import NoResultFound
import hashlib
from sqlalchemy import extract, func, not_
from io import BytesIO
from reportlab.pdfgen import canvas

def add_user(name, username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    user = NguoiDung(hoTen=name.strip(),
                     username=username.strip(),
                     password=password,
                     loaiNguoiDung=Role.Patient)
    db.session.add(user)
    db.session.commit()

def check_login(username, password, userRole):
    if username and password and userRole: 
        password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())   
        # Tìm kiếm người dùng dựa trên tên đăng nhập va vai tro
        try:
            user = NguoiDung.query.filter_by(username=username.strip(), loaiNguoiDung=userRole).one()
        except NoResultFound:
            return None  # Trả về None nếu không tìm thấy người dùng
        
        # Kiểm tra mật khẩu
        if user.password == password:
            return user  # Trả về đối tượng người dùng nếu thông tin đăng nhập hợp lệ
        return None  # Trả về None nếu mật khẩu không khớp
    
def get_user_by_id(user_id):
    return NguoiDung.query.get(user_id)

def update_patient(user_id, **kwargs):
    user = NguoiDung.query.filter_by(id=user_id).first()

    if user:
        user.hoTen = kwargs.get('name')
        user.gioiTinh = kwargs.get('sex')
        user.namSinh = kwargs.get('birth')
        user.email = kwargs.get('email')
        user.avatar = kwargs.get('avatar')
    
    patient = BenhNhan(nguoiDung=user, 
                       diaChi=kwargs.get('address'), 
                       soDienThoai=kwargs.get('phone'))
    db.session.add(patient)
    db.session.commit()

def register_medical(**kwargs):
    patient_id = kwargs.get('patient_id')
    phone = kwargs.get('phone')
    nurse_id = kwargs.get('nurse_id')

    if patient_id:
        phieuDK = PhieuDangKy(benhNhan_id=patient_id,
                              yTa_id = nurse_id,
                              ngayKham=kwargs.get('date_time'))
    elif phone:
        benhNhan = BenhNhan.query.filter_by(soDienThoai=phone).first()
        phieuDK = PhieuDangKy(benhNhan_id=benhNhan.id,
                              yTa_id = nurse_id,
                              ngayKham=kwargs.get('date_time'))
    db.session.add(phieuDK)
    db.session.commit()

def count_register_medical(date):
    
    return PhieuDangKy.query.filter(func.date(PhieuDangKy.ngayKham).__eq__(date)).count()

def get_register_medical_by_date(**kwargs):
    query = db.session.query(
        NguoiDung.hoTen,
        BenhNhan.soDienThoai,
        PhieuDangKy.ngayKham,
        BenhNhan.id
    ).join(BenhNhan, PhieuDangKy.benhNhan_id.__eq__(BenhNhan.id))\
    .join(NguoiDung, BenhNhan.id.__eq__(NguoiDung.id))

    date = kwargs.get('date')
    print(f"date ne: {date}")
    if date:
        query = query.filter(func.date(PhieuDangKy.ngayKham).__eq__(date))

    return query.all()



def check_medicine_exists(medicine_name):
    try:
        # Kiểm tra tên thuốc trong cơ sở dữ liệu
        result = Thuoc.query.filter(Thuoc.tenThuoc == medicine_name).first()

        if result is None:
            print(f"Không tìm thấy thuốc với tên: {medicine_name}")
        else:
            print(f"Thuốc tìm thấy: {result.tenThuoc}")  # Giả sử `tenThuoc` là trường tên thuốc

        return result is not None  # Trả về True nếu thuốc tồn tại, False nếu không

    except Exception as e:
        print(f"Đã xảy ra lỗi khi kiểm tra tên thuốc: {str(e)}")
        raise e  # Ném lỗi nếu có sự cố



def create_medical_list_pdf(data):
    pdf_buffer = BytesIO()
    pdf = canvas.Canvas(pdf_buffer)

    pdf.setFont("Helvetica", 12)
    pdf.drawString(100, 800, "Danh sách khám bệnh")
    y_coordinate = 750

    for record in data:
        pdf.drawString(100, y_coordinate, f"Họ tên: {record[0]}, Ngày giờ khám: {record[2]}, Số điện thoại: {record[1]}")
        y_coordinate -= 20  # Giả sử mỗi dòng là 20 điểm

    pdf.save()
    pdf_buffer.seek(0)
    return pdf_buffer


def create_invoice_pdf(medical_list):
    pdf_buffer = BytesIO()
    pdf = canvas.Canvas(pdf_buffer)

    pdf.setFont("Helvetica", 12)
    pdf.drawString(100, 800, "Hóa Đơn Thanh Toán")
    y = 750

    for item in medical_list:
        pdf.drawString(50, y, f"ID Hóa Đơn: {item['hoa_don_id']}")
        y -= 20
        pdf.drawString(50, y, f"Tên Thu Ngân: {item['thu_ngan']}")
        y -= 20
        pdf.drawString(50, y, f"Ngày Lập: {item['ngay_lap']}")
        y -= 20
        pdf.drawString(50, y, f"ID Phiếu Khám: {item['phieu_kham_id']}")
        y -= 20
        pdf.drawString(50, y, f"Tiền Khám: {item['tien_kham']:.0f} VND")
        y -= 20
        pdf.drawString(50, y, f"Tiền Thuốc: {item['tien_thuoc']:.0f} VND")
        y -= 20
        pdf.drawString(50, y, f"Tổng Tiền: {item['tong_tien']:.0f} VND")
        y -= 20
        pdf.drawString(50, y, f"SĐT Bệnh Nhân: {item['so_dien_thoai']}")
        y -= 40

    pdf.save()
    pdf_buffer.seek(0)
    return pdf_buffer


def count_medicine():
    return Thuoc.query.filter(Thuoc.id.isnot(None)).count()

def load_medicine(kw=None,page=1):
    drugs = Thuoc.query.filter(Thuoc.id.isnot(None))

    if kw:
        drugs = drugs.filter(Thuoc.tenThuoc.contains(kw))

    page_size =app.config['PAGE_SIZE']
    start = (page-1)*page_size
    end =start + page_size

    return drugs.slice(start,end).all()

def count_patient():
    return BenhNhan.query.filter(BenhNhan.id.isnot(None)).count()

def load_patient(kw=None,page=1):
    query = db.session.query(
        NguoiDung.hoTen,
        PhieuKham.ngayKham,
        PhieuKham.trieuChung,
        PhieuKham.duDoan
    ).join(NguoiDung, NguoiDung.id == PhieuKham.benhNhan_id)\
    .filter(NguoiDung.loaiNguoiDung == Role.Patient)

    if kw:
        query = query.filter(NguoiDung.hoTen.contains(kw))

    page_size =app.config['PAGE_SIZE']
    start = (page-1)*page_size
    end =start + page_size

    patients = query.slice(start, end).all()

    return patients

def add_examination_form(**kwargs):
    name = kwargs.get('name')
    date = kwargs.get('date')
    symptom = kwargs.get('symptom')
    disease = kwargs.get('disease')
    medicineName = kwargs.get('medicineName')
    quantity = kwargs.get('quantity')
    unit = kwargs.get('unit')
    id = kwargs.get('id')
    instruction = kwargs.get('instruction')

    patient = NguoiDung.query.filter_by(hoTen=name, loaiNguoiDung=Role.Patient).first()
    
    if patient:
        benhNhan_id = patient.id

    medicine = Thuoc.query.filter_by(tenThuoc=medicineName).first()
    if medicine:
        idThuoc = medicine.id

    new_examination = PhieuKham(
        ngayKham=date,
        trieuChung=symptom,
        duDoan=disease,
        benhNhan_id=benhNhan_id,
        bacSi_id = id
    )
    db.session.add(new_examination)
    db.session.commit()

    if unit:
        donvi_thuoc = DonViThuoc.query.filter_by(id=unit).first()
    
    new_prescription = ToaThuoc(
        thuoc_id=idThuoc,
        phieuKham_id=new_examination.id,
        soLuong=quantity,
        lieuLuong= donvi_thuoc.donVi,
        cachDung=instruction
    )
    db.session.add(new_prescription)
    db.session.commit()

def get_list_examination():
    try:
        medical_fees = lay_gia_tien('Tiền khám 100.000 VNĐ')
        print("medical_feesssssssssssssssssssss: ", medical_fees)
        subquery = db.session.query(HoaDon.phieuKham_id).subquery()
        results = db.session.query(
            NguoiDung.hoTen,
            PhieuKham.ngayKham,
            PhieuKham.id,
            medical_fees,
            Thuoc.donGia,
            ToaThuoc.soLuong,
            # func.sum(Thuoc.donGia * ToaThuoc.soLuong)
            func.sum(Thuoc.donGia * ToaThuoc.soLuong + medical_fees)
        )\
        .join(NguoiDung, NguoiDung.id.__eq__(PhieuKham.benhNhan_id))\
        .join(ToaThuoc, ToaThuoc.phieuKham_id.__eq__(PhieuKham.id))\
        .join(Thuoc, Thuoc.id.__eq__(ToaThuoc.thuoc_id))\
        .filter(not_(PhieuKham.id.in_(subquery)))\
        .group_by(
            NguoiDung.hoTen,
            PhieuKham.ngayKham,
            PhieuKham.id,
            Thuoc.donGia,
            ToaThuoc.soLuong,
        ).all()

        if not results:
            print("No results found!")
        else:
            print("Results found:", len(results), "rows")
            for row in results:
                print(row)

    except Exception as ex:
        print(ex)
    
    return results


def create_receipt(**kwargs):
    phieuKham_id = kwargs.get('phieuKham_id')
    thuNgan_id = kwargs.get('thuNgan_id')

    print(f"phieuKham_id: {phieuKham_id}")
    print(f"thuNgan_id: {thuNgan_id}")

    phieuKham_id = int(phieuKham_id)

    if thuNgan_id:
        thuNgan = NguoiDung.query.filter_by(id=thuNgan_id, loaiNguoiDung=Role.Cashier).first()
        print(f"ThuNgan: {thuNgan}")  # In thông tin thu ngân nếu tìm thấy

    if phieuKham_id:
        phieuKham = PhieuKham.query.filter_by(id=phieuKham_id).first()
        print(f"PhieuKham: {phieuKham}")  # In thông tin phiếu khám nếu tìm thấy

    # Kiểm tra Tiền khám
    medical_fees = lay_gia_tien('Tiền khám 100.000 VNĐ')
    print(f"Medical Fees: {medical_fees}")

    # Lấy thông tin thuốc
    medicine_money = db.session.query(Thuoc.donGia) \
        .join(ToaThuoc, Thuoc.id == ToaThuoc.thuoc_id) \
        .join(PhieuKham, PhieuKham.id == ToaThuoc.phieuKham_id) \
        .filter(PhieuKham.id == phieuKham_id) \
        .first()
    print(f"Medicine Money: {medicine_money}")  # In đơn giá thuốc

    # Lấy số lượng thuốc
    quantity = ToaThuoc.query.filter_by(phieuKham_id=phieuKham_id).first().soLuong
    print(f"Quantity: {quantity}")  # In số lượng thuốc

    # Lấy ngày khám
    date = PhieuKham.query.filter_by(id=phieuKham_id).first().ngayKham
    print(f"Date: {date}")  # In ngày khám

    # Tính tổng tiền
    total_money = medical_fees + (medicine_money[0] * quantity)
    print(f"Total Money: {total_money}")  # In tổng tiền thanh toán

    # Tạo hóa đơn
    new_receipt = HoaDon(tienKham=medical_fees,
                         tienThuoc=medicine_money[0],
                         tongTien=total_money,
                         ngayLap=date,
                         thuNgan_id=thuNgan.id,
                         phieuKham_id=phieuKham_id)

    print(f"New Receipt: {new_receipt}")  # In thông tin hóa đơn mới

    # Thêm hóa đơn vào cơ sở dữ liệu
    db.session.add(new_receipt)
    db.session.commit()

    print("Receipt has been created and committed.")


# def lay_so_luong(name):
#     # medicine_amount = QuyDinh.query.filter_by(tenQuyDinh=name).first()
#     medicine_amount = QuyDinh.query.filter(QuyDinh.tenQuyDinh.ilike(f"%{name.strip()}%")).first()
#
#     print("medicine_amount:" + str(medicine_amount));
#     if medicine_amount:
#         amount = medicine_amount.moTa
#
#         # Chuyển đổi mô tả thành số nguyên (nếu có thể)
#         try:
#             amount = int(amount)
#             return amount
#         except (TypeError, ValueError):
#             return None  # Trả về None nếu không thể chuyển đổi thành số nguyên
#     else:
#         return None  # Trả về None nếu không tìm thấy dữ liệu phù hợp

def lay_so_luong(name):
    # Sử dụng truy vấn tương đối để tìm tên quy định
    medicine_amount = QuyDinh.query.filter(QuyDinh.tenQuyDinh.ilike(f"%{name.strip()}%")).first()

    print("medicine_amount:", medicine_amount)

    if medicine_amount and medicine_amount.moTa:
        # Trích xuất số từ chuỗi moTa
        match = re.search(r'\d+', medicine_amount.moTa)  # Tìm số đầu tiên trong chuỗi
        if match:
            return int(match.group())  # Trả về số dưới dạng số nguyên
        else:
            print("Không tìm thấy số trong moTa.")
            return None
    else:
        print("Không tìm thấy dữ liệu cho tên quy định.")
        return None

def lay_gia_tien(name):
    # Truy vấn để tìm quy định
    medicine_amount = QuyDinh.query.filter(func.lower(QuyDinh.tenQuyDinh) == name.lower()).first()
    if medicine_amount:
        ten_quy_dinh = medicine_amount.tenQuyDinh
        print("ten_quy_dinh:", ten_quy_dinh)  # Debug chuỗi đầu vào

        # Sử dụng regex để tìm số trong chuỗi
        try:
            # Loại bỏ các ký tự không phải số hoặc dấu chấm
            clean_string = re.sub(r'[^\d]', '', ten_quy_dinh)
            print("clean_string:", clean_string)  # Chuỗi sau khi làm sạch

            # Chuyển đổi chuỗi số sang float
            amount = float(clean_string)
            print("amount:", amount)  # Giá trị sau khi chuyển đổi
            return amount
        except (TypeError, ValueError) as e:
            print("Lỗi khi xử lý số:", e)
            return None
    else:
        print("Không tìm thấy quy định với tên:", name)
        return None
    
def money_stats(month):
    with app.app_context():
        query = db.session.query(
            extract('month', HoaDon.ngayLap).label('Tháng'),
            func.sum(HoaDon.tongTien).label('Doanh thu')
        ).group_by(extract('month', HoaDon.ngayLap))

        results = query.all()

        return results
    
def tan_suat_kham(month):
    with app.app_context():
        query = db.session.query(
            extract('month', PhieuKham.ngayKham).label('Tháng'),
            (func.count(PhieuKham.id) / 30 * 100).label('Tần suất khám')
        ).group_by(extract('month', PhieuKham.ngayKham))

        if month:
            query = query.filter(extract('month', PhieuKham.ngayKham) == month)

        results = query.all()

        return results
    
def tan_suat_su_dung_thuoc(month):
    with app.app_context():
        # Tạo truy vấn cơ bản
        query = db.session.query(
            Thuoc.tenThuoc,
            extract('month', PhieuKham.ngayKham).label('Tháng'),
            (func.sum(ToaThuoc.soLuong) / 30 * 100).label('Tần suất sử dụng')
        )\
        .join(ToaThuoc, ToaThuoc.thuoc_id.__eq__(Thuoc.id))\
        .join(PhieuKham, PhieuKham.id.__eq__(ToaThuoc.phieuKham_id))\
        .group_by(Thuoc.tenThuoc, extract('month', PhieuKham.ngayKham))

        if month:
            query = query.filter(extract('month', PhieuKham.ngayKham) == month)

        results = query.all()

        return results