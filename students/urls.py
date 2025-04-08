from django.urls import path
from . import views


urlpatterns = [

    path('student/',views.student,name='student'),
    path('registercheck/',views.registercheck,name='registercheck'),
    path('UserLoginCheck/',views.UserLoginCheck,name='UserLoginCheck'),
    path('userhome/',views.userhome,name='userhome'),
    path('alreadyapplied/',views.alreadyapplied,name='alreadyapplied'),
    path('logoutfun/',views.logoutfun,name="logoutfun"),
    path('create_applicant',views.create_applicant,name='create_applicant'),
    path('route-selection/<int:applicant_id>/', views.route_selection, name='route_selection'),
    path('display-amount/<int:route_selection_id>/', views.display_amount, name='display_amount'),
    # path('generate_pdf/<int:route_selection_id>/', views.generate_pdf, name='generate_pdf'),
    path('payment_gateway/<int:route_selection_id>/', views.payment_gateway, name='payment_gateway'),
    path('payment_success/<int:route_selection_id>/', views.payment_success, name='payment_success'),
    path('final_pass_html/<int:route_selection_id>/', views.final_pass_html, name='final_pass_html'),
    path('search_bus_pass/', views.search_bus_pass, name='search_bus_pass'),
    path('generate_pdf/<int:route_selection_id>/', views.generate_pdf, name='generate_pdf'),
    
    
]