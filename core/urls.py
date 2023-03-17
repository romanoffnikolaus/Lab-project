from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title='Lab',
        description='Udemi_clone',
        default_version='v1'
    ), public=True
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/v1/', include('account.urls')),
    path('docs/', schema_view.with_ui('swagger')),
]


urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
