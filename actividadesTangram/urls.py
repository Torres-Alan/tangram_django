from django.urls import path, include

urlpatterns = [
    path('api/', include('actividadesTangram.api.urls')),
]
