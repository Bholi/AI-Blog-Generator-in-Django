from django.urls import path
from .views import home,signup_view,login_view,logout_view,generate_blog,blog_list,blog_details
from django.conf import settings
from django.conf.urls.static import static
urlpatterns =[
    path('',home,name='home'),
    path('signup/',signup_view,name='signup'),
    path('login/',login_view,name='login'),
    path('logout/',logout_view,name='logout'),
    path('generate-blog/',generate_blog,name='generate_blog'),
    path('blog-list',blog_list,name='bloglist'),
    path('blog-list/<int:pk>/',blog_details,name='details'),
]  + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)