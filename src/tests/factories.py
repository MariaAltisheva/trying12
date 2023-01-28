import factory

from core.models import User


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Faker("name")
    first_name = "first name"
    last_name = "last name"
    email = "mail@mail.ru"
    password = "AnyPass2022"

    class Meta:
        model = User
