from django.forms import ModelForm
from .models import Training, TrackReservation


class TrainingForm(ModelForm):
    class Meta:
        model = Training
        exclude = ['instructorUsername']


class TrackForm(ModelForm):
    class Meta:
        model = TrackReservation
        exclude = ['trackResInstructorUsername']