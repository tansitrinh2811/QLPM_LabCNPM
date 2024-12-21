from wtforms import StringField, SelectField
from wtforms.validators import DataRequired

from server_app import app, db, dao
from flask_admin import BaseView, expose
from flask_admin.contrib.sqla import ModelView
from server_app.models import Thuoc, DonViThuoc, Role, QuyDinh
from flask_login import current_user, logout_user, login_user
from flask import flash, redirect, request
from flask_admin import Admin, expose ,AdminIndexView
from server_app import utils

#tai de den 

class MyAdmin(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/admin_page.html', 
                           stats=utils.sales_report(),
                           sales_data=utils.total_amount_by_month())

class AuthenticatedAdmin(ModelView):
     def is_accessible(self):
         return current_user.is_authenticated and current_user.loaiNguoiDung.__eq__(Role.Admin)

class DrugsView(AuthenticatedAdmin):
    column_list = ['tenThuoc', 'ngaySX', 'hanSD', 'donGia', 'donViThuoc']
    column_searchable_list = ['tenThuoc', 'donGia']
    column_filters = ['tenThuoc', 'donGia']
    can_view_details = True
    can_export = True

class DonViThuocView(AuthenticatedAdmin):
    column_list = ['donVi']
    can_view_details = True
    can_export = True

    def on_model_change(self, form, model, is_created):
        if is_created:  # Chỉ kiểm tra khi đối tượng được tạo mới
            # Kiểm tra số lượng dữ liệu đơn vị thuốc đã đạt đến giới hạn chưa
            so_luong_hien_tai = dao.lay_so_luong('Loại đơn vị thuốc')

            if so_luong_hien_tai is not None:
                # Số lượng dữ liệu tối đa được quy định
                so_luong_toi_da = so_luong_hien_tai  # Số lượng dữ liệu tối đa có thể tạo mới

                so_luong_hien_tai_du_lieu = DonViThuoc.query.count()
                if so_luong_hien_tai_du_lieu >= so_luong_toi_da:
                    flash('Số lượng đơn vị thuốc đã đạt giới hạn tối đa. Không thể thêm mới.', 'warning')
                    return False  # Ngăn không cho thêm mới

        # Nếu không ngăn chặn việc thêm mới, gọi phương thức cha để tiếp tục tạo mới
        return super(DonViThuocView, self).on_model_change(form, model, is_created)

    def create_model(self, form):
        # Kiểm tra số lượng dữ liệu đơn vị thuốc đã đạt đến giới hạn chưa
        so_luong_hien_tai = dao.lay_so_luong('Loại đơn vị thuốc')

        if so_luong_hien_tai is not None:
            # Số lượng dữ liệu tối đa được quy định
            so_luong_toi_da = so_luong_hien_tai  # Số lượng dữ liệu tối đa có thể tạo mới

            so_luong_hien_tai_du_lieu = DonViThuoc.query.count()
            if so_luong_hien_tai_du_lieu >= so_luong_toi_da:
                flash('Số lượng đơn vị thuốc đã đạt giới hạn tối đa. Không thể thêm mới.', 'warning')
                return False  # Ngăn không cho thêm mới

        return super(DonViThuocView, self).create_model(form)




class MedicineView(DrugsView):
    can_view_details = True
    can_export = True
    column_searchable_list = ['tenThuoc', 'donGia']
    column_labels = {
        'tenThuoc': 'Tên thuốc',
        'ngaySX': 'Ngày sản xuất',
        'hanSD': 'Hạn sử dụng',
        'donGia': 'Đơn giá',
        'donViThuoc': 'Đơn vị thuốc'
    }
    column_filters = ['tenThuoc', 'donGia']
    form_excluded_columns = ['phieuKham']

    def create_form(self):
        form = super(MedicineView, self).create_form()

        # Tạo danh sách đơn vị thuốc mặc định
        default_units = [
            (1, 'Viên'),
            (2, 'Vĩ'),
            (3, 'Hộp')
        ]

        # Thêm trường chọn đơn vị thuốc vào form với danh sách mặc định
        form.donViThuoc_id = SelectField(
            'Đơn vị thuốc',
            choices=default_units,  # Sử dụng danh sách mặc định
            validators=[DataRequired()],  # Trường này bắt buộc phải nhập
            coerce=int  # Coerce để đảm bảo giá trị gửi lên là integer (id của đơn vị thuốc)
        )

        return form

    def on_model_change(self, form, model, is_created):
        if is_created:  # Chỉ kiểm tra khi đối tượng được tạo mới
            # Kiểm tra số lượng thuốc đã đạt đến giới hạn chưa
            so_luong_hien_tai = dao.lay_so_luong('Loại thuốc')
            if 'donViThuoc_id' in form:
                # Lấy giá trị ID của đơn vị thuốc từ form và gán vào model
                model.donViThuoc_id = form.donViThuoc_id.key  # Gán ID của đơn vị thuốc vào model

            if so_luong_hien_tai is not None:
                so_luong_toi_da = so_luong_hien_tai  # Giới hạn số lượng thuốc

                so_luong_thuoc_hien_tai = Thuoc.query.count()
                if so_luong_thuoc_hien_tai >= so_luong_toi_da:
                    flash('Số lượng thuốc đã đạt giới hạn tối đa. Không thể thêm mới.', 'warning')
                    return False  # Ngừng quá trình tạo nếu đã đạt giới hạn

        return super(MedicineView, self).on_model_change(form, model, is_created)

    def create_model(self, form):
        # Kiểm tra số lượng thuốc đã đạt đến giới hạn chưa
        so_luong_hien_tai = dao.lay_so_luong('Loại thuốc')

        if so_luong_hien_tai is not None:
            so_luong_toi_da = so_luong_hien_tai  # Giới hạn số lượng thuốc tối đa

            so_luong_thuoc_hien_tai = Thuoc.query.count()
            if so_luong_thuoc_hien_tai >= so_luong_toi_da:
                flash('Số lượng thuốc đã đạt giới hạn tối đa. Không thể thêm mới.', 'warning')
                return False  # Ngừng không cho thêm mới

        return super(MedicineView, self).create_model(form)







class ThayDoiQuyDinh(AuthenticatedAdmin):
    can_view_details = True
    can_export = True
    column_list = ['tenQuyDinh', 'moTa']
    column_searchable_list = ['tenQuyDinh']
    column_labels = {
        'tenQuyDinh': 'Tên quy định',
        'moTa': 'Mô tả'
    }
    column_filters = ['tenQuyDinh']
    form_excluded_columns = ['quanTriVien_id']  # Loại bỏ khỏi giao diện form

    def on_model_change(self, form, model, is_created):
        """
        Ghi đè để cập nhật `quanTriVien_id` khi tạo mới hoặc sửa quy định.
        """
        if is_created:
            model.quanTriVien_id = current_user.id  # Gán ID người tạo mới quy định
            # Bạn có thể thêm các thuộc tính khác nếu cần khi tạo mới
            print("is_created" + str(is_created))
            print("is_created" + str(current_user.id))
        else:
            # Thêm logic xử lý khi sửa, ví dụ như ghi lại thời gian sửa hoặc thay đổi thông tin thêm
            model.last_modified_by = current_user.id  # Ghi lại ID người sửa nếu cần
            print("sua" + str(is_created))
            print("sua" + str(current_user.id))


        # Tiếp tục gọi phương thức của lớp cha để xử lý phần còn lại
        super().on_model_change(form, model, is_created)
        db.session.commit()

class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')

    def is_accessible(self):
        return current_user.is_authenticated
    
class MoneyView(BaseView):
    @expose('/')
    def index(self):
        month = request.args.get('month')

        return self.render('admin/stats.html',
                           money=dao.money_stats(month=month))
    
    def is_accessible(self):
         return current_user.is_authenticated and current_user.loaiNguoiDung.__eq__(Role.Admin)

class ExaminationFrequency(BaseView):
    @expose('/')
    def index(self):
        month = request.args.get('month')

        return self.render('admin/ExaminationFrequency.html',
                           tanSuat=dao.tan_suat_kham(month=month))
    
    def is_accessible(self):
         return current_user.is_authenticated and current_user.loaiNguoiDung.__eq__(Role.Admin)

class DrugFrequency(BaseView):
    @expose('/')
    def index(self):
        month = request.args.get('month')

        return self.render('admin/DrugFrequency.html',
                           tanSuat=dao.tan_suat_su_dung_thuoc(month=month))
    
    def is_accessible(self):
         return current_user.is_authenticated and current_user.loaiNguoiDung.__eq__(Role.Admin)

admin = Admin(app=app, name='LT Clinic', template_mode='bootstrap4', index_view=MyAdmin())
admin.add_view(DonViThuocView(DonViThuoc,db.session, name='Đơn vị thuốc'))
admin.add_view(MedicineView(Thuoc,db.session, name='Thuốc'))
admin.add_view(ThayDoiQuyDinh(QuyDinh, db.session, name='Quy định'))
admin.add_view(MoneyView(name='Thống kê doanh thu'))
admin.add_view(ExaminationFrequency(name='Thống kê tần suất khám'))
admin.add_view(DrugFrequency(name='Thống kê tần suất sử dụng thuốc'))
admin.add_view(LogoutView(name='Logout'))
