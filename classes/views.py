from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from .models import FitnessClass, Booking
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
import logging
logger = logging.getLogger(__name__)
# API Views

class ClassListView(View):
    def get(self, request):
        now = timezone.now()
        classes = FitnessClass.objects.filter(datetime__gte=now)
        data = [
            {
                "id": cls.id,
                "name": cls.name,
                "datetime": cls.datetime.isoformat(),
                "instructor": cls.instructor,
                "available_slots": cls.available_slots
            }
            for cls in classes
        ]
        return JsonResponse(data, safe=False)

@method_decorator(csrf_exempt, name='dispatch')
class BookClassView(View):
    def post(self, request):
        try:
            body = json.loads(request.body)
            class_id = body.get("class_id")
            name = body.get("client_name")
            email = body.get("client_email")

            if not all([class_id, name, email]):
                return JsonResponse({"error": "Missing fields"}, status=400)

            fc = FitnessClass.objects.get(id=class_id)
            if fc.available_slots <= 0:
                return JsonResponse({"error": "No slots available"}, status=400)

            Booking.objects.create(
                fitness_class=fc,
                client_name=name,
                client_email=email
            )
            fc.available_slots -= 1
            fc.save()
            return JsonResponse({"message": "Booking successful!"})

        except FitnessClass.DoesNotExist:
            return JsonResponse({"error": "Fitness class not found"}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

class BookingListView(View):
    def get(self, request):
        email = request.GET.get("email")
        if not email:
            return JsonResponse({"error": "Email is required"}, status=400)

        bookings = Booking.objects.filter(client_email=email)
        data = [
            {
                "class_name": b.fitness_class.name,
                "datetime": b.fitness_class.datetime.isoformat(),
                "instructor": b.fitness_class.instructor
            }
            for b in bookings
        ]
        return JsonResponse(data, safe=False)

# HTML VIEWS

class ClassListHTML(View):
    def get(self, request):
        now = timezone.now()
        classes = FitnessClass.objects.filter(datetime__gte=now)
        return render(request, 'classes.html', {'classes': classes})

class BookClassHTML(View):
    def get(self, request):
        class_id = request.GET.get('class_id', '')
        return render(request, 'book.html', {'class_id': class_id})

    def post(self, request):
        class_id = request.POST.get("class_id")
        client_name = request.POST.get("client_name")
        client_email = request.POST.get("client_email")

        if not all([class_id, client_name, client_email]):
            return render(request, 'book.html', {"error": "Missing fields."})

        try:
            fitness_class = FitnessClass.objects.get(id=class_id)
        except FitnessClass.DoesNotExist:
            return render(request, 'book.html', {"error": "Class not found."})

        if fitness_class.available_slots <= 0:
            return render(request, 'book.html', {"error": "No slots available."})

        # Reduce available slots
        fitness_class.available_slots -= 1
        fitness_class.save()

        # Save booking
        Booking.objects.create(
            fitness_class=fitness_class,
            client_name=client_name.strip(),
            client_email=client_email.strip().lower()
        )

        return render(request, 'book.html', {"message": "Booking successful!"})

class BookingListHTML(View):
    def get(self, request):
        email = request.GET.get('email', '').strip().lower()

        bookings = []
        if email:
            bookings = Booking.objects.filter(client_email__iexact=email)

        return render(request, 'bookings.html', {
            'bookings': bookings,
            'entered_email': email
        })
class HomeView(View):
    def get(self, request):
        return render(request, 'base.html')
