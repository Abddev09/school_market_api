from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.http import HttpResponse
schema_view = get_schema_view(
    openapi.Info(
        title="School API",
        default_version='v1',
        description="Maktab uchun oddiy REST API",
        terms_of_service="https://www.emaktab.uz/terms/",
        contact=openapi.Contact(email="abddev09@gmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


def home(request):
    html_content = """
    <html>
      <head><title>255-Maktab API</title></head>
      <body>
      <mosquee>
          <h1>🕌 API ishlayapti 🚀</h1>
      </mosquee>
      </body>
    </html>
    """
    return HttpResponse(html_content)



urlpatterns = [
    path('admin/', admin.site.urls),
    path('',home),
    path('api/', include("user.urls")),
    path('api/',include("school.urls")),
    path('api/',include("market.urls")),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)