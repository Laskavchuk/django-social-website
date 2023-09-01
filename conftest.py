import faker
import pytest
import factory
from django.contrib.auth import get_user_model
from django.urls import reverse
from pytest_factoryboy import register

fake = faker.Faker()


@pytest.fixture(scope='session')
def faker_fixture():
    yield fake


@pytest.fixture(autouse=True)
def django_db_setup(db):
    yield


@register
class UserFactory(factory.django.DjangoModelFactory):
    email = factory.LazyAttribute(lambda x: fake.email())
    first_name = factory.LazyAttribute(lambda x: fake.first_name())
    last_name = factory.LazyAttribute(lambda x: fake.last_name())
    username = factory.LazyAttribute(lambda x: fake.word())

    class Meta:
        model = get_user_model()


@pytest.fixture(scope='function')
def login_client(db, client):
    def login_user(user=None, **kwargs):
        if user is None:
            user = UserFactory()
        password = fake.password()
        user.set_password(password)
        user.save()
        response = client.post(reverse('login'), data={
            'username': user.username,
            'password': password})
        assert response.status_code == 302
        return client, user
    return login_user



