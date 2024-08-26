from django.urls import re_path, include, path
from . import views
from rest_framework import routers
from .modules.profile import views as profileviews
from .modules.internships import views as intviews
from .modules.tests import views as testviews
router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('login', views.login),
    path('signup', views.signup),
    path('test_token', views.test_token),
    path('signup_companies', views.signup_companies),
    path('get_skills', profileviews.get_skills),
    path('get_user', profileviews.get_user),
    path('save_skills', profileviews.save_skills),
    path('add_internship', intviews.add_internship),
    path('get_internships', intviews.get_internships),
    path('update_internship_skills', intviews.update_internship_skills),
    path('get_company_internships_ids', intviews.get_company_internships_ids),
    path('get_internship/<int:internship_id>', intviews.get_internship),
    path('create_or_update_test', testviews.create_or_update_test),
    path('get_test_by_id/<int:test_id>', testviews.get_test_details),
    path('download_file/<int:question_id>/', testviews.download_file, name='download_file'),
    path('add_user_test', testviews.add_user_test),
    path('get_users_test_details/<int:test_id>', testviews.get_users_test_details),
    path('download_user_file/<int:user_id>/<int:question_id>', testviews.download_user_file, name='download_user_file'),
    path('get_user_results_status', testviews.get_users_test_status),
    path('update_status', testviews.update_status),
    path('get_companies', views.get_companies),
    path('get_user_by_id/<int:user_id>', views.get_user_by_id),
    path('get_internships_by_company_id/<int:company_id>', views.get_internships_by_company_id)
]
    