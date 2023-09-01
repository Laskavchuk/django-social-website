from django.contrib.auth import get_user_model
from django.urls import reverse

from account.models import Profile

User = get_user_model()


def test_login(client, faker):
    url = reverse('login')
    response = client.get(url)
    assert response.status_code == 200

    data = {}
    response = client.post(url, data=data)
    assert response.status_code == 200
    assert all(v == ['This field is required.']
               for v in response.context['form'].errors.values())

    data['username'] = faker.email()
    data['password'] = faker.word()

    response = client.post(url, data=data)
    assert response.status_code == 200

    assert response.context['form'].errors['__all__'] == [
        'Please enter a correct username and password. '
        'Note that both fields may be case-sensitive.']

    password = faker.word()
    user, _ = User.objects.get_or_create(
        username=faker.word(),
        email=faker.email()
    )
    user.set_password(password)
    user.save()

    data['username'] = user.email
    data['password'] = password

    response = client.post(url, data=data, follow=True)
    assert response.redirect_chain[0][0] == '/account/'
    assert response.redirect_chain[0][1] == 302

    data['username'] = user.username
    data['password'] = password

    response = client.post(url, data=data, follow=True)
    assert response.redirect_chain[0][0] == '/account/'
    assert response.redirect_chain[0][1] == 302


def test_registration(client, faker):
    url = reverse('register')
    response = client.get(url)
    assert response.status_code == 200

    data = {}
    response = client.post(url, data=data)
    assert response.status_code == 200
    assert all(v == ['This field is required.']
               for v in response.context['form'].errors.values())

    user, _ = User.objects.get_or_create(
        username=faker.word(),
        email=faker.email()
    )
    password = faker.word()

    data = {
        'email': user.email,
        'password1': password,
        'password2': faker.word(),
        'username': user.username
    }
    response = client.post(url, data=data)
    assert response.status_code == 200
    errors = response.context['form'].errors
    assert errors['username'] == ['A user with that username already exists.']
    assert errors['email'] == ['User already exist.']
    assert errors['password2'] == ['The two password fields didn’t match.']

    data['email'] = faker.word()
    response = client.post(url, data=data)
    assert response.status_code == 200
    errors = response.context['form'].errors
    assert errors['email'] == ['Enter a valid email address.']

    email = faker.email()
    data['email'] = email
    data['username'] = faker.word()
    data['password2'] = password
    response = client.post(url, data=data)
    assert response.status_code == 200
    errors = response.context['form'].errors
    assert errors['password2'] == ['This password is too short. '
                                   'It must contain at least 8 characters.']

    password = faker.password()
    data['password1'] = password
    data['password2'] = password
    response = client.post(url, data=data, follow=True)
    assert response.status_code == 200

    user, _ = User.objects.get_or_create(email=email)
    login_data = {'username': data['username'],
                  'password': password}

    url = reverse('login')
    response = client.get(url)
    assert response.status_code == 200

    response = client.post(url, data=login_data, follow=True)
    assert response.redirect_chain[0][0] == '/account/'
    assert response.redirect_chain[0][1] == 302


def test_edit(client, faker, login_client):
    client, user = login_client()
    url = reverse('edit')
    profile = Profile.objects.create(user=user)
    response = client.get(url)
    assert response.status_code == 200
    assert not profile.date_of_birth

    data = {'first_name': 'Jake'}
    assert user.first_name != data['first_name']
    response = client.post(url, data=data)
    assert response.status_code == 200
    user.refresh_from_db()
    assert user.first_name == data['first_name']

    data['date_of_birth'] = '2023-01-20'
    assert profile.date_of_birth != data['date_of_birth']
    response = client.post(url, data=data)
    assert response.status_code == 200
    profile.refresh_from_db()
    assert profile.date_of_birth.strftime('%Y-%m-%d') == data['date_of_birth']
