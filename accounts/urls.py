from django.urls import path
from .views import *

urlpatterns = [
    path('login-api/', LoginView.as_view(), name='login-api'),
    path('login/', LoginTemplateView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('generate_qr_codes/', GenerateQRCodesView.as_view(), name='generate_qr_codes'),
    path('Qrsetup/<int:business_id>/<str:business_phone_number>/<str:business_name>/<str:business_email>/', QRSetupView.as_view(), name='qr_setup'),
    path('qrredirect/<str:chunk>/', QRRedirect.as_view(), name='qr_redirect'),
    path('success/', SuccessView.as_view(), name='success'),
    path('download-unlinked-qrs/', download_unlinked_qrs, name='download_unlinked_qrs'),
    path('unlinked-qrs/', unlinked_qr_list, name='unlinked_qr_list'),
    path('linked-qrs/', linked_qr_list, name='linked_qr_list'),
    path('download-qr/<str:chunk>/', download_qr_image, name='download_qr_image'),
    path('business-details/', BusinessDetailsView.as_view(), name='business_details'),
]
