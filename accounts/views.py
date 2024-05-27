from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from django.contrib.auth import get_user_model, authenticate, login
from django.shortcuts import render, redirect,get_object_or_404
from .serializers import UserLoginSerializer, UserSerializer,QRRedirectSerializer
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.contrib.auth import logout as auth_logout
import uuid
from django.http import QueryDict
import io
import requests
import qrcode
import cloudinary.uploader
from django.conf import settings
from django.views import View
from django.http import HttpResponse,HttpResponseNotFound
from .models import QRModel,BusinessDetails
from .forms import QRCodeForm,QRSetupForm
import os
import zipfile
from io import BytesIO
User = get_user_model()

class LoginTemplateView(TemplateView):
    template_name = 'login.html'

class SuccessView(TemplateView):
    template_name = 'success.html'

# Function to check if the user is an admin
def is_admin(user):
    return user.is_authenticated and user.is_staff

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_admin), name='dispatch')
class HomePageView(TemplateView):
    template_name = 'home.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'user': request.user})

# API Views for login/logout
class LoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            refresh = RefreshToken.for_user(user)
            response = Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            })
            return redirect('home')
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            auth_logout(request)
            return render(request, 'logout.html', {'message': 'Logged out successfully'})
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        


class GenerateQRCodesView(View):
    form_class = QRCodeForm
    template_name = 'generate_qr_codes.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            number_of_qrs = form.cleaned_data['number_of_qrs']
            qr_models, zip_buffer = self.generate_qr_codes(number_of_qrs)
            response = HttpResponse(zip_buffer, content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename="qr_codes.zip"'
            return response
        return render(request, self.template_name, {'form': form})

    def generate_qr_codes(self, number_of_qrs):
        qr_models = []
        zip_buffer = BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for _ in range(number_of_qrs):
                unique_chunk = uuid.uuid4().hex
                qr_link = f"https://digichola.in/{unique_chunk}"

                # Create the QR code
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(qr_link)
                qr.make(fit=True)

                img = qr.make_image(fill='black', back_color='white')

                # Save the image to a file
                file_path = f'{unique_chunk}.png'
                img.save(file_path)

                # Upload the image to Cloudinary
                upload_result = cloudinary.uploader.upload(file_path)
                cloudinary_url = upload_result['url']

                # Add the image to the zip file
                zip_file.write(file_path, arcname=f'{unique_chunk}.png')

                # Remove the local file after uploading to Cloudinary
                os.remove(file_path)

                # Create a QRModel instance
                qr_model = QRModel(
                    chunk=unique_chunk,
                    qr_image=cloudinary_url,
                    qr_link=qr_link,
                    qr_redirect_link="https://digichola.in"
                )
                qr_models.append(qr_model)

        # Bulk create the QRModel instances
        QRModel.objects.bulk_create(qr_models)

        zip_buffer.seek(0)

        return qr_models, zip_buffer
    
class QRSetupView(View):
    template_name = 'qr_setup.html'

    def get(self, request, business_id, business_phone_number, business_name, business_email):
        form = QRSetupForm(initial={
            'business_id': business_id,
            'business_phone_number': business_phone_number,
            'business_name': business_name,
            'business_email': business_email,
        })
        return render(request, self.template_name, {'form': form})

    def post(self, request, business_id, business_phone_number, business_name, business_email):
        form = QRSetupForm(request.POST)
        if form.is_valid():
            qr_link_values = form.cleaned_data.get('qr_link')
            if isinstance(qr_link_values, QueryDict):
                qr_link = qr_link_values.getlist('qr_link')[0]
            else:
                qr_link = qr_link_values
            
            if qr_link:
                chunk = qr_link.split('/')[-1]
                qr_model = get_object_or_404(QRModel, chunk=chunk)

                if qr_model.linked_status:
                    # QR code is already linked to another business
                    return render(request, self.template_name, {
                        'form': form,
                        'error_message': 'This QR is already linked'
                    })
                
                qr_model.business_id = form.cleaned_data['business_id']
                qr_model.business_phone_number = form.cleaned_data['business_phone_number']
                qr_model.business_name = form.cleaned_data['business_name']
                qr_model.business_email = form.cleaned_data['business_email']
                qr_model.linked_status = True
                business_data = BusinessDetails.objects.get(business_id=form.cleaned_data['business_id'])
                category = business_data.category.category
                redirect_url = f"https://digichola.in/profile/QR/{category}/{form.cleaned_data['business_id']}/"
                qr_model.qr_redirect_link = redirect_url
                qr_model.save()
                business_data.is_Qr_generated=True
                business_data.save()
                return render(request, 'success.html', {
                    'profile': business_data.business_profile,
                    'business_name': business_data.business_name,
                    'qr_image': qr_model.qr_image,
                    'qr_link': qr_model.qr_link
                })

        return render(request, self.template_name, {'form': form})
class QRRedirect(APIView):
    def get(self, request, *args, **kwargs):
        chunk = kwargs.get('chunk')
        qr_data = get_object_or_404(QRModel, chunk=chunk)
        serializer = QRRedirectSerializer(qr_data)
        return Response(serializer.data)
    
def download_unlinked_qrs(request):
    # Filter unlinked QR codes
    unlinked_qrs = QRModel.objects.filter(linked_status=False)
    
    # Create an in-memory buffer to hold the zip file
    buffer = io.BytesIO()
    
    # Create a new zip file in the buffer
    with zipfile.ZipFile(buffer, 'w') as zip_file:
        for qr in unlinked_qrs:
            # Download the QR image
            response = requests.get(qr.qr_image)
            image_data = response.content
            
            # Add the image to the zip file
            image_name = f"{qr.chunk}.png"  # Assuming the images are PNGs
            zip_file.writestr(image_name, image_data)
    
    # Seek to the beginning of the buffer
    buffer.seek(0)
    
    # Create a response with the buffer as the content and set the content type to 'application/zip'
    response = HttpResponse(buffer, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="unlinked_qrs.zip"'
    
    return response

def unlinked_qr_list(request):
    # Filter unlinked QR codes
    unlinked_qrs = QRModel.objects.filter(linked_status=False)
    context = {'unlinked_qrs': unlinked_qrs}
    return render(request, 'unlinked_qr_list.html', context)

def linked_qr_list(request):
    # Filter linked QR codes
    linked_qrs = QRModel.objects.filter(linked_status=True)
    context = {'linked_qrs': linked_qrs}
    return render(request, 'linked_qr_list.html', context)

def download_qr_image(request, chunk):
    try:
        qr = QRModel.objects.get(chunk=chunk)
        response = requests.get(qr.qr_image)
        image_data = response.content

        response = HttpResponse(image_data, content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename="{chunk}.png"'
        return response
    except QRModel.DoesNotExist:
        return HttpResponseNotFound("QR Code not found")

class BusinessDetailsView(View):
    template_name = 'business_details.html'

    def get(self, request):
        # Filter BusinessDetails objects by is_Qr_generated = False
        businesses = BusinessDetails.objects.filter(is_Qr_generated=False)

        # Pass the filtered data to the template
        context = {
            'businesses': businesses
        }
        return render(request, self.template_name, context)
