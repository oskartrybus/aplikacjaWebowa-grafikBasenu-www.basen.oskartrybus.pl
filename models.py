from django.db import models
from django.shortcuts import get_object_or_404


class Date:
    DAYS_OF_THE_WEEK = (
        ('PN', 'Poniedziałek'),
        ('WT', 'Wtorek'),
        ('SR', 'Środa'),
        ('CZ', 'Czwartek'),
        ('PT', 'Piątek'),
        ('SB', 'Sobota'),
        ('ND', 'Niedziela'),
    )
    HOURS = (
        ('16:00', '16:00'),
        ('16:15', '16:15'),
        ('16:30', '16:30'),
        ('16:45', '16:45'),
        ('17:00', '17:00'),
        ('17:15', '17:15'),
        ('17:30', '17:30'),
        ('17:45', '17:45'),
        ('18:00', '18:00'),
        ('18:15', '18:15'),
        ('18:30', '18:30'),
        ('18:45', '18:45'),
        ('19:00', '19:00'),
        ('19:15', '19:15'),
        ('19:30', '19:30'),
        ('19:45', '19:45'),
        ('20:00', '20:00'),
        ('20:15', '20:15'),
        ('20:30', '20:30'),
        ('20:45', '20:45'),
        ('21:00', '21:00')
    )


class Term(models.Model, Date):
    day = models.CharField(max_length=2, choices=Date.DAYS_OF_THE_WEEK)
    hour = models.CharField(max_length=5, choices=Date.HOURS)
    numberOfReservedTracks = models.PositiveSmallIntegerField(blank=False, default=0)
    numberOfClients = models.PositiveSmallIntegerField(blank=False, default=0)
    fieldColor = models.CharField(max_length=12, default='green')

    def __str__(self):
        return f"'{self.fieldColor}', '{self.numberOfClients}','{self.day}','{self.hour}'"

    @staticmethod
    # as one lesson takes 45 mins and Term corresponds only to 15 mins we have to change 3 Term
    # objects which this function is already doing. In addition it updates color of the term fields:
    def change_number_of_clients_or_res_tracks(day, hourIndex, numOfClientsOrTracks, action, changeClientsOrTracks):
        term1 = get_object_or_404(Term, day=day, hour=Date.HOURS[hourIndex][0])
        term2 = get_object_or_404(Term, day=day, hour=Date.HOURS[hourIndex+1][0])
        term3 = get_object_or_404(Term, day=day, hour=Date.HOURS[hourIndex+2][0])
        if action == "increment":
            setattr(term1, changeClientsOrTracks, getattr(term1, changeClientsOrTracks)+numOfClientsOrTracks)
            setattr(term2, changeClientsOrTracks, getattr(term2, changeClientsOrTracks)+numOfClientsOrTracks)
            setattr(term3, changeClientsOrTracks, getattr(term3, changeClientsOrTracks)+numOfClientsOrTracks)
        else:
            setattr(term1, changeClientsOrTracks, getattr(term1, changeClientsOrTracks)-numOfClientsOrTracks)
            setattr(term2, changeClientsOrTracks, getattr(term2, changeClientsOrTracks)-numOfClientsOrTracks)
            setattr(term3, changeClientsOrTracks, getattr(term3, changeClientsOrTracks)-numOfClientsOrTracks)
        Term.update_field_color_and_save(term1)
        Term.update_field_color_and_save(term2)
        Term.update_field_color_and_save(term3)

    @staticmethod
    def update_field_color_and_save(term):
        if term.numberOfClients + term.numberOfReservedTracks * 4 > 19:
            term.fieldColor = "red"
        elif term.numberOfClients + term.numberOfReservedTracks * 4 > 15:
            term.fieldColor = "light-red"
        elif term.numberOfClients + term.numberOfReservedTracks * 4 > 11:
            term.fieldColor = "yellow"
        elif term.numberOfClients + term.numberOfReservedTracks * 4 > 7:
            term.fieldColor = "light-green"
        else:
            term.fieldColor = "green"
        term.save()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['day', 'hour'], name='Day and hour')
        ]


class Training(models.Model, Date):
    trainingDay = models.CharField('Dzień tygodnia ',max_length=2, choices=Date.DAYS_OF_THE_WEEK)
    trainingHour = models.CharField('Godzina ', max_length=5, choices=Date.HOURS[0:18])
    trainingNumberOfClients = models.PositiveSmallIntegerField('Ilość klientów ', blank=False, default=0)
    instructorUsername = models.CharField(max_length=150, blank=False, default="anonim")

    def __str__(self):
        return f"Termin: {self.trainingDay}, {self.trainingHour}-{Date.HOURS[(Date.HOURS.index((self.trainingHour, self.trainingHour))+3)][0]}, Ilość klientów: " \
               f"{self.trainingNumberOfClients}."

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['trainingDay', 'trainingHour', 'instructorUsername'],
                                    name='Training constraint')
        ]


class TrackReservation(models.Model, Date):
    trackResDay = models.CharField('Dzień tygodnia', max_length=2, choices=Date.DAYS_OF_THE_WEEK)
    trackResHour = models.CharField('Godzina', max_length=5, choices=Date.HOURS[0:18])
    trackResInstructorUsername = models.CharField(max_length=150, blank=False, default="anonim")
    trackResNumberOfTracks = models.PositiveSmallIntegerField('Ilość torów ', blank=False, default=0)

    def __str__(self):
        return f"Termin: {self.trackResDay}, {self.trackResHour}-{Date.HOURS[(Date.HOURS.index((self.trackResHour, self.trackResHour))+3)][0]}, " \
               f"Ilość torów: {self.trackResNumberOfTracks}."

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['trackResDay', 'trackResHour', 'trackResInstructorUsername'],
                                    name='Track Reservation constraint')
        ]