from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken

from mptt.models import MPTTModel, TreeForeignKey
from accounts.managers import UserManager
# Create your models here.

AUTH_PROVIDERS ={'email':'email', 'google':'google', 'github':'github', 'linkedin':'linkedin'}

class User(AbstractBaseUser, PermissionsMixin):
    id = models.BigAutoField(primary_key=True, editable=False) 
    email = models.EmailField(
        max_length=255, verbose_name=_("Email Address"), unique=True
    )
    phone_number = models.CharField(max_length=20)
    first_name = models.CharField(max_length=100, verbose_name=_("First Name"))
    last_name = models.CharField(max_length=100, verbose_name=_("Last Name"), null=True, blank=True)
    profile_pic = models.URLField(default="https://res.cloudinary.com/dybwn1q6h/image/upload/v1712815867/user_opfbgm.png")
    is_business_user = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified=models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    auth_provider=models.CharField(max_length=50, blank=False, null=False, default=AUTH_PROVIDERS.get('email'))
    

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserManager()

    def tokens(self):    
        refresh = RefreshToken.for_user(self)
        return {
            "refresh":str(refresh),
            "access":str(refresh.access_token)
        }


    def __str__(self):
        return f"{self.email} {self.first_name}"

    @property
    def get_full_name(self):
        return f"{self.first_name.title()} {self.last_name.title()}"

    class Meta:
        verbose_name_plural = "User Info"



class Category(MPTTModel):
  category = models.CharField(max_length=200, unique=True)
  parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
  categoryImage = models.URLField()
  
  class MPTTMeta:
    order_insertion_by = ['category']

  class Meta:
    verbose_name_plural = 'Categories'

  def __str__(self):
    return self.category
  
  class Meta:
        verbose_name_plural = "Business Category"

class BusinessUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='business_profile')
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, unique=True)
    priority = models.IntegerField(default=0, blank=True)
    
    def __str__(self):
        return f"{self.full_name}[{self.phone_number}]"
    
    class Meta:
        verbose_name_plural = "Business User Info"
class BusinessDetails(models.Model):
    business_id = models.BigAutoField(primary_key=True, editable=False)
    business_name = models.CharField(max_length=255)
    business_email = models.EmailField(max_length=255, verbose_name=_("Email Address"))
    views = models.PositiveIntegerField(default=0)
    business_phone_number = models.CharField(max_length=20)
    whatsapp_phone_number = models.CharField(max_length=20)
    business_profile = models.URLField(default="https://cdn4.vectorstock.com/i/1000x1000/47/38/business-profile-icon-flat-design-vector-14544738.jpg")
    Location = models.CharField(max_length=255)
    place = models.CharField(max_length=255,default="")
    rating = models.FloatField(default=0)
    is_Qr_generated=models.BooleanField(default=False)
    description = models.TextField()
    category = TreeForeignKey(Category, on_delete=models.CASCADE)
    business_user = models.ForeignKey(BusinessUser, on_delete=models.CASCADE)

    def __str__(self):
       return f"{self.business_name}({self.business_phone_number})"
    
    class Meta:
        verbose_name_plural = "Business Details"

class QRModel(models.Model):
    chunk = models.CharField(primary_key=True, editable=False)
    qr_image = models.URLField()
    qr_link = models.URLField()
    qr_redirect_link = models.URLField(default="https://digichola.in")
    business_id = models.IntegerField(default=0)
    business_phone_number = models.CharField(default="")
    business_email = models.CharField(default="")
    business_name = models.CharField(default="",max_length=255)
    linked_status = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "QR Creator"


class OneTimePassword(models.Model):
    user=models.OneToOneField(User, on_delete=models.CASCADE)
    otp=models.CharField(max_length=6)


    def __str__(self):
        return f"{self.user.first_name} - {self.user.phone_number}"
    
    class Meta:
        verbose_name_plural = "OTP"



class PlaceList(models.Model):
    place_names = models.CharField(blank=False,unique=True)

    class Meta:
        verbose_name_plural = "Place List"

class AutocompleteSearch(models.Model):
    search_name = models.CharField(max_length=255)
    search_image = models.URLField()
    search_main = models.CharField(max_length=255)
    business_id = models.IntegerField()

    
    class Meta:
        verbose_name_plural = "Autocomplete Search"

class HomeCarousel1(models.Model):
    home_image = models.URLField(default="https://t4.ftcdn.net/jpg/02/88/48/77/360_F_288487781_skjPODvR9bnuAGRVYP8AeRxT2AogzRHh.jpg")

    class Meta:
        verbose_name_plural = "Home Banner"