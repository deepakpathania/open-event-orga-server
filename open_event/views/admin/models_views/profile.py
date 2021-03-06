from flask import request, url_for, redirect, abort
from flask.ext.admin import BaseView
from flask_admin import expose
from flask.ext import login

from ....helpers.data import DataManager
from ....helpers.data_getter import DataGetter
from open_event.helpers.storage import upload


class ProfileView(BaseView):

    def is_accessible(self):
        return login.current_user.is_authenticated

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('admin.login_view', next=request.url))

    @expose('/')
    def index_view(self):
        profile = DataGetter.get_user(login.current_user.id)
        return self.render('/gentelella/admin/profile/index.html',
                           profile=profile)

    @expose('/edit/', methods=('GET', 'POST'))
    @expose('/edit/<user_id>', methods=('GET', 'POST'))
    def edit_view(self, user_id=None):
        if not user_id:
            user_id = login.current_user.id
        if request.method == 'POST':
            url = ""
            if 'avatar' in request.files and request.files['avatar'].filename != "":
                avatar_img = request.files['avatar']
                url = upload(avatar_img, 'users/%d/avatar' % int(user_id))
            profile = DataManager.update_user(request.form, int(user_id), url)
            return redirect(url_for('.index_view'))
        profile = DataGetter.get_user(int(user_id))
        return self.render('/gentelella/admin/profile/edit.html', profile=profile)

    @expose('/notifications/', methods=('GET', 'POST'))
    def notifications_view(self):
        user = login.current_user
        notifications = DataGetter.get_all_user_notifications(user)

        return self.render('/gentelella/admin/profile/notifications.html',
                           notifications=notifications)

    @expose('/notifications/read/<notification_id>/', methods=('GET', 'POST'))
    def mark_notification_as_read(self, notification_id):
        user = login.current_user
        notification = DataGetter.get_user_notification(notification_id)

        if notification and notification.user == user:
            DataManager.mark_user_notification_as_read(notification)
            return redirect(url_for('.notifications_view'))
        else:
            abort(404)
