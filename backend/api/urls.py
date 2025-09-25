from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import IngredientViewSet, TagViewSet, RecipeViewSet, UserViewSet, test_ingredients
from .auth_views import custom_login, custom_me

router = DefaultRouter()
router.register('ingredients', IngredientViewSet)
router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet)
router.register('users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('test-ingredients/', test_ingredients, name='test-ingredients'),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('auth/custom-login/', custom_login, name='custom-login'),
    path('auth/users/me/', custom_me, name='custom-me'),
]
