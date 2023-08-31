from django.contrib.auth import get_user_model
from django.urls import reverse

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

    data['email'] = faker.email()
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

    url = reverse('login')
    response = client.get(url)
    assert response.status_code == 200
