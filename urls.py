from django.urls import path
from .views import main_schedule, instructor_board, delete_training, delete_track_reservation, reset_schedule

urlpatterns = [
    path('main-schedule/', main_schedule, name="main-schedule"),
    path('instructor-board/', instructor_board, name="instructor-board"),
    path('delete-training/<int:id>/', delete_training, name="delete-training"),
    path('delete-track-reservtion/<int:id>/', delete_track_reservation, name="delete-track-reservation"),
    path('reset-schedule/', reset_schedule, name="reset-schedule"),
]
