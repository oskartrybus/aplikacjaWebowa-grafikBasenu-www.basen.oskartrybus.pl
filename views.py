from django.shortcuts import render, redirect, get_object_or_404
from .models import Term, Date, Training, TrackReservation
from django.contrib.auth.decorators import login_required
from .forms import TrainingForm, TrackForm
from django.db import IntegrityError
from django.contrib.auth.decorators import user_passes_test


def main_schedule(request):
    terms = {}
    hoursList=Term.HOURS[0:20]
    for _hour in hoursList:
        terms[f"{_hour[0]}"] = Term.objects.order_by('id').filter(hour=f"{_hour[0]}")
    terms = list(terms.values())

    daysOfTheWeek = []
    for element in Term.DAYS_OF_THE_WEEK:
        daysOfTheWeek.append(element[1])

    return render(request, 'pool_schedule.html', {'terms': terms, 'daysOfTheWeek': daysOfTheWeek})


@login_required()
def instructor_board(request):
    errorMessage = ""
    currentUser = request.user.username
    # trainings
    trainings = Training.objects.filter(instructorUsername=currentUser).order_by('trainingHour')
    order = [i[0] for i in Date.DAYS_OF_THE_WEEK]
    order = {key: i for i, key in enumerate(order)}
    ordered_trainings = sorted(trainings, key=lambda t: order.get(t.trainingDay))
    trainingForm = TrainingForm(request.POST or None)

    # track reservations
    tracksReservations = TrackReservation.objects.filter(trackResInstructorUsername=currentUser).order_by(
        'trackResHour')
    ordered_tracks = sorted(tracksReservations,
                            key=lambda r: order.get(r.trackResDay))
    trackResForm = TrackForm(request.POST or None)
    if trainingForm.is_valid():
        try:
            training = trainingForm.save(commit=False)
            if training.trainingNumberOfClients == 0:
                raise IntegrityError
            training.instructorUsername = request.user.username
            hourIndex = Date.HOURS.index((training.trainingHour, training.trainingHour))
            if Training.objects.filter(trainingDay=training.trainingDay, trainingHour=Date.HOURS[hourIndex - 1][0],
                                       instructorUsername=training.instructorUsername) or Training.objects.filter(
                                        trainingDay=training.trainingDay, trainingHour=Date.HOURS[hourIndex - 2][0],
                                        instructorUsername=training.instructorUsername):
                raise IntegrityError
            training.save()
            Term.change_number_of_clients_or_res_tracks(training.trainingDay, hourIndex,
                                                        training.trainingNumberOfClients, "increment",
                                                        "numberOfClients")
        except IntegrityError as e:
            errorMessage = "Uwaga! Lekcja nie została dodana (sprawdź czy już nie masz lekcji w tym terminie lub czy" \
                           " liczba w formularzu nie wynosi 0)!"
            return render(request, 'instructor-board.html',
                  {'ordered_tracks': ordered_tracks, 'trainings': ordered_trainings, 'trainingForm': trainingForm,
                   'trackResForm': trackResForm, 'errorMessage': errorMessage})
        except AttributeError as e:
            errorMessage = "Uwaga! Lekcja nie została dodana (sprawdź czy już nie masz lekcji w tym terminie lub czy" \
                           " liczba w formularzu nie wynosi 0)!"
            return render(request, 'instructor-board.html',
                  {'ordered_tracks': ordered_tracks, 'trainings': ordered_trainings, 'trainingForm': trainingForm,
                   'trackResForm': trackResForm, 'errorMessage': errorMessage})
        return redirect(instructor_board)

    if trackResForm.is_valid():
        try:
            trackRes = trackResForm.save(commit=False)
            if trackRes.trackResNumberOfTracks == 0:
                raise IntegrityError
            trackRes.trackResInstructorUsername = request.user.username
            hourIndex = Date.HOURS.index((trackRes.trackResHour, trackRes.trackResHour))
            if TrackReservation.objects.filter(trackResDay=trackRes.trackResDay,
                                               trackResHour=Date.HOURS[hourIndex - 1][0],
                                               trackResInstructorUsername=trackRes.trackResInstructorUsername) or TrackReservation.objects.filter(
                                                trackResDay=trackRes.trackResDay, trackResHour=Date.HOURS[hourIndex - 2][0],
                                                trackResInstructorUsername=trackRes.trackResInstructorUsername):
                raise IntegrityError
            trackRes.save()
            Term.change_number_of_clients_or_res_tracks(trackRes.trackResDay, hourIndex,
                                                        trackRes.trackResNumberOfTracks, "increment",
                                                        "numberOfReservedTracks")
        except IntegrityError as e:
            errorMessage = "Uwaga! Rezerwacja nie została dodana (sprawdź czy już nie masz rezerwacji w tym terminie" \
                           " lub wpisana w formularzu liczba nie jest rowna 0)!"
            return render(request, 'instructor-board.html',
                  {'ordered_tracks': ordered_tracks, 'trainings': ordered_trainings, 'trainingForm': trainingForm,
                   'trackResForm': trackResForm, 'errorMessage': errorMessage})
        except AttributeError as e:
            errorMessage = "Uwaga! Rezerwacja nie została dodana (sprawdź czy już nie masz rezerwacji w tym terminie" \
                           " lub wpisana w formularzu liczba nie jest rowna 0)!"
            return render(request, 'instructor-board.html',
                  {'ordered_tracks': ordered_tracks, 'trainings': ordered_trainings, 'trainingForm': trainingForm,
                   'trackResForm': trackResForm, 'errorMessage': errorMessage})
        return redirect(instructor_board)

    return render(request, 'instructor-board.html',
                  {'ordered_tracks': ordered_tracks, 'trainings': ordered_trainings, 'trainingForm': trainingForm,
                   'trackResForm': trackResForm, 'errorMessage': errorMessage})


@login_required()
def delete_training(request, id):
    training = get_object_or_404(Training, pk=id)
    hourIndex = Date.HOURS.index((training.trainingHour, training.trainingHour))
    if request.method == "POST":
        Term.change_number_of_clients_or_res_tracks(training.trainingDay, hourIndex, training.trainingNumberOfClients,
                                                    "decrement", "numberOfClients")
        training.delete()
        return redirect(instructor_board)

    return render(request, 'delete_training_confirm.html', {'training': training})


@login_required()
def delete_track_reservation(request, id):
    trackReservation = get_object_or_404(TrackReservation, pk=id)
    hourIndex = Date.HOURS.index((trackReservation.trackResHour, trackReservation.trackResHour))
    if request.method == "POST":
        Term.change_number_of_clients_or_res_tracks(trackReservation.trackResDay, hourIndex, trackReservation.trackResNumberOfTracks,
                                                    "decrement", "numberOfReservedTracks")
        trackReservation.delete()
        return redirect(instructor_board)

    return render(request, 'delete_track_reservation_confirm.html', {'trackReservation': trackReservation})


@user_passes_test(lambda u: u.is_superuser)
def reset_schedule(request):
    Term.objects.all().delete()
    Training.objects.all().delete()
    TrackReservation.objects.all().delete()
    for j in range(7):
        for i in range(len(Date.HOURS)-1):
            Term.objects.create(day=Date.DAYS_OF_THE_WEEK[j][0], hour=Date.HOURS[i][0])

    return main_schedule(request)