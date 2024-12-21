# @app.route("/api/info_receipt", methods=['post'])
# def add_to_receipt():
#     '''
#         #cấu trúc của 1 hóa đơn
#         #dat 1 cai key tên là 'receipt'
#         "receipt" : {
#         "1":{ #mã số 1 là key -> lưu thông tin
#             "benhNhanId":"1",
#             "ho":"Nguyen",
#             "ten" = "Van C",
#             "ngaySinh" = 1/1/2002,
#             "gioiTinh" = 0,
#             "diaChi" = "7 ABC, quan 8, TPHCM",
#
#             "ngayKham" = 1/1/2022,
#             "tienKham" = 100000,
#             "tienThuoc" = 25000,
#             "tongTien" = 125000
#             }
#         }
#     :return:
#     '''
#     data = request.json
#
#     # tao hoa don
#     receipt = session.get('receipt')
#
#     # kiem tra da co du lieu trong hoa don chua -> neu chua thi tao
#     if receipt is None:
#         receipt = {}
#
#     # kiem tra da tao hoa don cho ma benh nhan chua
#     id = str(data.get("benhNhanId"))
#     if id not in receipt:  # nếu mã bệnh nhân chưa được tạo hóa đơn
#         # đưa thông tin bệnh nhân vào biến receipt - lưu kiểu từ điển
#         # if not data.get("benhNhanId") or not data.get("ho") or not data.get("ten")\
#         #     or not data.get("diaChi") or not str(data.get("ngaySinh")) or not str(data.get("ngayKham")) or not float(data.get("tienThuoc")):
#         #     pass
#         # else:
#         receipt[id] = {
#             "benhNhanId": data.get("benhNhanId"),  # lấy từ data gửi lên
#             "ho": data.get("ho"),
#             "ten": data.get("ten"),
#             "ngaySinh": str(data.get("ngaySinh")),
#             "gioiTinh": str(data.get("gioiTinh")),
#             "diaChi": data.get("diaChi"),
#             "ngayKham": str(data.get("ngayKham")),
#             "tienKham": data.get("tienKham"),
#             "tienThuoc": float(data.get("tienThuoc")),
#             "tongTien": data.get("tongTien")
#         }
#         print(receipt[id])
#         dao.add_receipt(receipt)
#         del receipt[id]
#         session['receipt'] = receipt  # luu vao session1
#
#     # else:  # nếu mã bệnh nhân đã được tạo hóa đơn
#     #     print("Bệnh nhân đã có hóa đơn.")
#
#     return jsonify(utils.count_receipt(receipt))