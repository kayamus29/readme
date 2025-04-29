from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class ExtensionTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Optionally add custom claims for extension
        token['is_extension'] = True
        return token

class ExtensionTokenObtainPairView(TokenObtainPairView):
    serializer_class = ExtensionTokenObtainPairSerializer
