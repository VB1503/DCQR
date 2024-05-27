from django import forms

class QRCodeForm(forms.Form):
    number_of_qrs = forms.IntegerField(label='Number of QR Codes', min_value=1)

class QRSetupForm(forms.Form):
    business_id = forms.IntegerField()
    business_phone_number = forms.CharField(max_length=15)
    business_name = forms.CharField(max_length=255)
    business_email = forms.CharField()
    qr_link = forms.URLField(label='qr_link')  # Make qr_link optional