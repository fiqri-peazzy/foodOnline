from distutils.command.upload import upload
from email.policy import default
from pyexpat import model
from django.db import models
from accounts.models import User, UserProfile
from accounts.utils import send_notification_email
from datetime import time, date, datetime
# Create your models here.
class Vendor(models.Model):
    user = models.OneToOneField(User, related_name='user',on_delete=models.CASCADE)
    user_profile = models.OneToOneField(UserProfile, related_name='userprofile', on_delete=models.CASCADE)
    vendor_name = models.CharField(max_length=50)
    vendor_slug = models.SlugField(max_length=100, blank=True, unique=True)
    vendor_license = models.ImageField(upload_to='vendor/license')
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.vendor_name 

    def is_open(self):
         # Check current day opening hour
        today_date = date.today()
        today = today_date.isoweekday()
        current_opening_hours = OpeningHour.objects.filter(vendor=self, day=today)
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        is_open = None
        for i in current_opening_hours:
            if not i.is_closed:
                start = str(datetime.strptime(i.from_hour,"%I:%M %p").time())
                end = str(datetime.strptime(i.to_hour,"%I:%M %p").time())
                if current_time > start and current_time < end:
                    is_open = True
                    break
                else:
                    is_open = False
        return is_open

    def save(self, *args, **kwargs):
        if self.pk is not None:
            # update
            orig = Vendor.objects.get(pk=self.pk)
            if orig.is_approved != self.is_approved:
                mail_template = 'accounts/emails/admin_approval_email.html'
                context = {
                    'user':self.user,
                    'is_approved': self.is_approved,
                    'to_email':self.user.email
                   }
                if self.is_approved == True:
                    # send notification email
                    mail_subject = 'Congratulations! your restaurant is approved'
                    send_notification_email(mail_subject, mail_template, context)
                else:
                    # send notification email
                    mail_subject = 'We are sorry! You are not eligible for publishing your food menu on our marketplace'
                    send_notification_email(mail_subject, mail_template, context)
        return super(Vendor, self).save(*args,**kwargs)


DAYS = [
    (1, ("SENIN")),
    (2, ("SELASA")),
    (3, ("RABU")),
    (4, ("KAMIS")),
    (5, ("JUMAT")),
    (6, ("SABTU")),
    (7, ("MINGGU")),
]

HOURS_OF_DAY_24 = [(time(h, m).strftime("%I:%M %p"), time(h, m).strftime("%I:%M %p"))for h in range(0, 24) for m in (0, 30)]

class OpeningHour(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    day = models.IntegerField(choices=DAYS)
    from_hour = models.CharField(choices=HOURS_OF_DAY_24, max_length=10,blank=True)
    to_hour = models.CharField(choices=HOURS_OF_DAY_24, max_length=10,blank=True)
    is_closed = models.BooleanField(default=False)

    class Meta:
        ordering = ('day','-from_hour')
        unique_together = ('vendor','day','from_hour', 'to_hour')

    def __str__(self):
        return self.get_day_display()