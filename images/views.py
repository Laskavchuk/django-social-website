from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from images.model_forms import ImageCreateForm
from images.models import Image


@login_required
def image_create(request):
    """
    1. Для создания экземпляра формы необходимо предоставить начальные
    данные через HTTP-запрос методом GET. Эти данные будут состоять
    из атрибутов url и  title изображения с  внешнего веб-сайта. Оба параметра
    будут заданы в запросе GET
    2. После того как форма передана на обработку с помощью HTTP-запроса
    методом POST, она валидируется методом form.is_valid(). Если данные
    в форме валидны, то создается новый экземпляр Image путем сохранения формы
    методом form.save(commit=False). Новый экземпляр в базе
    данных не сохраняется, если commit=False.
    3. В новый экземпляр изображения добавляется связь с текущим пользователем,
    который выполняет запрос: new_image.user = request.user. Так мы будем
    знать, кто закачивал каждое изображение.
    4. Объект Image сохраняется в базе данных.
    5. Наконец, с  помощью встроенного в  Django фреймворка сообщений
    создается сообщение об успехе, и  пользователь перенаправляется на
    канонический URL-адрес нового изображения. Мы еще не реализовали
    метод get_absolute_url() модели Image; мы сделаем это позже.
    :param request:
    :return:
    """
    if request.method == 'POST':
        # орма отправлена
        form = ImageCreateForm(data=request.POST)
        if form.is_valid():
            # данные в форме валидны
            cd = form.cleaned_data
            new_image = form.save(commit=False)
            # назначить текущего пользователя элементу
            new_image.user = request.user
            new_image.save()
            messages.success(request, 'Image added successfully')
            # перенаправить к представлению детальной
            # информации о только что созданном элементе
            return redirect(new_image.get_absolute_url())
    else:
        # скомпоновать форму с данными,
        # предоставленными букмарклетом методом GET
        form = ImageCreateForm(data=request.GET)
    context = {'section': 'images', 'form': form}
    return render(request, 'images/image/create.html', context)


def image_detail(request, id, slug):
    image = get_object_or_404(Image, id=id, slug=slug)
    context = {'section': 'image',
               'image': image}
    return render(request, 'images/image/detail.html', context)


@login_required
@require_POST
def image_like(request):
    image_id = request.POST.get('id')
    try:
        image = Image.objects.get(id=image_id)
        if request.user in image.users_like.all():
            image.users_like.remove(request.user)
        else:
            image.users_like.add(request.user)
        return redirect(request.META.get('HTTP_REFERER'))
    except Image.DoesNotExist:
        return JsonResponse({'status': 'error'})


def image_list(request):
    images = Image.objects.all()
    paginator = Paginator(images, 8)
    page = request.GET.get('page')
    images_only = request.GET.get('images_only')
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        images = paginator.page(1)
    except EmptyPage:
        if images_only:
            return HttpResponse('')
        images = paginator.page(paginator.num_pages)
    if images_only:
        return render(request, 'images/image/list_images.html', {
            'section': 'images',
            'images': images}
                      )
    return render(request, 'images/image/list.html', {
            'section': 'images',
            'images': images}
                      )
