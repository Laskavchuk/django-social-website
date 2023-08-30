from django import forms
from django.core.files.base import ContentFile
from django.utils.text import slugify

from .models import Image
import requests


class ImageCreateForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['title', 'url', 'description']
        widgets = {
            'url': forms.HiddenInput
        }

    def clean_url(self):
        cd = self.cleaned_data
        url = cd['url']
        valid_extension = ['jpg', 'png', 'jpeg']
        extension = url.rsplit('.', 1)[1].lower()
        if extension not in valid_extension:
            raise forms.ValidationError('The given URL does not '
                                        'match valid image extensions.')
        return url

    def save(self, force_insert=False, force_update=False, commit=True):

        """
        1. Новий екземпляр зображення створюється шляхом виклику методу save()
        форми з commit=False.
        2. URL-адреса зображення витягується зі словника clean_data форми.
        3 Ім'я зображення генерується шляхом комбінування назви зображення з
        початковим розширенням файлу зображення.
        4. Бібліотека Python requests використовується для скачування
        зображення шляхом надсилання HTTP-запиту методом GET з використанням
        URL-адреси зображення. Відповідь зберігається в об'єкті response.
        5. Викликається метод save() поля image, передаючи йому об'єкт
        ContentFile, екземпляр якого заповнений вмістом завантаженого файлу.
        Таким шляхом файл зберігається в каталог media проекту.
        Параметр save=False передається для того, щоб уникнути збереження
        об'єкта в базі даних.
        6. Для того щоб залишити ту саму поведінку, що і в початковому
        методі save() модельної форми, форма зберігається в базі даних тільки
        у тому разі, якщо параметр commit дорівнює True.

        :param force_insert: вказує, чи потрібно примусово вставити новий запис
        в базу даних.
        :param force_update:вказує, чи потрібно примусово оновити існуючий
        запис в базі даних.
        :param commit: вказує, чи потрібно здійснити збереження (запис) в базу
        даних одразу після виклику методу save()
        :return: image
        """

        image = super().save(commit=False)
        image_url = self.cleaned_data['url']
        name = slugify(image.title)
        extension = image_url.rsplit('.', 1)[1].lower()
        image_name = f'{name}.{extension}'
        # download image from the given URL
        response = requests.get(image_url)
        image.image.save(image_name,
                         ContentFile(response.content),
                         save=False)
        if commit:
            image.save()
        return image





