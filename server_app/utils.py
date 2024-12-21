import json
import os.path
from server_app import app ,db
from server_app.models  import Thuoc ,Role, NguoiDung, ToaThuoc, PhieuKham,HoaDon
from flask_login import current_user
import hashlib
from sqlalchemy import func

def counter_medicine(medicine):
    total_quantity,total_price = 0,0
    if medicine:
        for c in medicine.values():
            total_quantity += c['quantity']
            total_price += c['quantity']*c['donGia']
            
    return {
        'total_quantity': total_quantity,
        'total_price': total_price
        }


def add_receipt(medicine):
    if medicine:
        receipt = PhieuKham(user=current_user)
        a="3 lan"
        b = "3 lan"
        db.session.add(receipt)
        for c in medicine.values():
            d =ToaThuoc(receipt=receipt,medicine_id=c['id'],soLuong=c['quantity'],lieuLuong=a,cachDung=b)
            db.session.add(d)
        db.session.commit()




def sales_report():
    # Lấy chỉ một số cột cụ thể
    specific_columns = HoaDon.query.with_entities(HoaDon.id, HoaDon.tienKham, HoaDon.tienThuoc,HoaDon.tongTien,HoaDon.ngayLap,HoaDon.thuNgan_id,HoaDon.phieuKham_id).all()
    return  specific_columns
    # return HoaDon.query.all()
    # monthly_data = {}
    # for invoice in invoices:
    #     month_year = invoice.ngayLap.strftime('%Y-%m')
    #     if month_year not in monthly_data:
    #         monthly_data[month_year] = {'total_amount': 0, 'visit_count': 0}
    #     monthly_data[month_year]['total_amount'] += invoice.amount
    #     monthly_data[month_year]['visit_count'] += 1
    # return monthly_data

def total_amount_by_month():
    result = db.session.query(
        func.CONCAT(func.YEAR(HoaDon.ngayLap), '-', func.FORMAT(func.MONTH(HoaDon.ngayLap), '00')).label('thang_nam'),
        func.sum(HoaDon.tongTien).label('Tong tien')
    ).group_by(func.CONCAT(func.YEAR(HoaDon.ngayLap), '-', func.FORMAT(func.MONTH(HoaDon.ngayLap), '00'))).all()

    # Chuyển kết quả thành danh sách từ điển để trả về JSON hoặc sử dụng trong template
    return result
#da tao tai