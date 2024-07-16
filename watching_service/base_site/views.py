from django.shortcuts import render, HttpResponseRedirect
from django.http import HttpResponseNotFound, StreamingHttpResponse, FileResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import permission_required
from .models import Feed, Film, Video
import string
import random
import datetime
from .forms import FilmForm, FilmMediaForm, FeedForm
from .services import open_file
from django.shortcuts import get_object_or_404
# Create your views here.


def page_list(quantity, current_page):
    """
    Делает список для выбора страниц на сайте
    """
    pages = ['1']
    allowed_range = 2

    if current_page - allowed_range > 1 and quantity > allowed_range * 2 + 1:
        pages.append('...')

    while current_page - allowed_range <= 0:
        current_page += 1

    while current_page + allowed_range > quantity:
        current_page -= 1

    for page_offset in range(allowed_range * 2 + 1):
        if quantity >= (current_page - allowed_range + page_offset) > 1:
            pages.append(str(current_page - allowed_range + page_offset))

    if (current_page + allowed_range) < quantity:
        pages.append('...')
        pages.append(str(quantity))
    return pages


def fill_random_staff():
    f_data = Film()
    f_updated = Feed()
    f_data.title = ''.join(random.choices(string.ascii_uppercase +
                             string.digits, k=7))
    unique_string = ''.join(random.choices(string.ascii_uppercase +
                             string.digits, k=7))
    f_data.type = unique_string
    f_data.genres = ''.join(random.choices(string.ascii_uppercase +
                             string.digits, k=7))
    f_data.description = ''.join(random.choices(string.ascii_uppercase +
                             string.digits, k=7))
    f_data.release_date = ''.join(random.choices(string.ascii_uppercase +
                             string.digits, k=7))
    f_data.poster_img_link = ''.join(random.choices(string.ascii_uppercase +
                             string.digits, k=7))
    f_data.save()
    f_updated.film_id = Film.objects.all().filter(type=unique_string)[0]
    f_updated.update_date = datetime.datetime.now()
    f_updated.save()


def feed(request):
    feed_quantity = Feed.objects.count()
    page_number = int(request.GET.get('page', 1))
    films_per_page = 5
    print(feed_quantity)
    if page_number > (feed_quantity / films_per_page + 1) or page_number < 0:
        return HttpResponseRedirect('/')
    start_index = 0 + films_per_page * (page_number - 1)
    film_indexes = Feed.objects.order_by('-update_date')\
        [start_index:films_per_page * page_number]
    film_data = []
    for one_film in film_indexes:
        film_data.append(
            (Film.objects.get(id=one_film.serializable_value("film_id")),
             one_film)
        )
    pages_to_render = page_list(feed_quantity // films_per_page, page_number)
    transfer_data = {"feed_data": film_data,
                     "pages": pages_to_render}
    return render(request, "feed_main_page.html", context=transfer_data)


def film_page(request, film_id):
    some_film = get_object_or_404(Film, id=film_id)
    videos = Video.objects.filter(film_id=film_id).order_by('episode_number')
    transfer_data = {"some_film": some_film,
                     "videos": videos}
    a = render(request, 'film_page.html', context=transfer_data)
    return a


@permission_required("base_site.add_film", login_url="/login")
def edit_film(request, film_id):
    film_data = get_object_or_404(Film, id=film_id)
    if request.method == "POST":
        form = FilmForm(request.POST, request.FILES, instance=film_data)
        edited_film = form.save(commit=False)
        edited_film.poster_img.name = f"p{film_id}"
        form.save()
        return HttpResponseRedirect(f"/edit-film/{film_id}")
    else:
        form = FilmForm(instance=film_data)
        transfer_data = {"film_data": film_data,
                         "form": form}
        return render(request, "edit_film_information.html", transfer_data)


@permission_required("base_site.add_film", login_url="/login")
def add_film(request):
    if request.method == "GET":
        films_per_page = 15
        film_name = request.GET.get('q', '')
        print(film_name)
        if film_name != "":
            film_quantity = Film.objects.filter(
                title__icontains=film_name).order_by("id").count()
            page_number = int(request.GET.get('page', 1))
            print(film_quantity)
            if page_number > film_quantity / films_per_page + 1 or page_number < 0:
                return HttpResponseRedirect('/add-film')
            start_index = 0 + films_per_page * (page_number - 1)
            film_list = Film.objects.filter(
                title__icontains=film_name).order_by('id')\
                [start_index:films_per_page * page_number]
        else:
            film_quantity = Film.objects.order_by("id").count()
            page_number = int(request.GET.get('page', 1))
            if page_number > film_quantity / films_per_page + 1 or page_number < 0:
                return HttpResponseRedirect('/add-film')
            start_index = 0 + films_per_page * (page_number - 1)
            film_list = Film.objects.order_by('id')\
                [start_index:films_per_page * page_number]
        film_form = FilmForm()
        pages_to_render = page_list(film_quantity // films_per_page + 1, page_number)
        transfer_data = {"film_list": film_list,
                         "form": film_form,
                         "pages": pages_to_render,
                         "last_queue": film_name}
        return render(request, "add_film.html", context=transfer_data)
    elif request.method == "POST":
        film_data = FilmForm(request.POST, request.FILES)
        film_data.save()
        return HttpResponseRedirect("/add-film")


@permission_required("base_site.delete_film")
def delete_film(request, film_id):
    try:
        some_film = Film.objects.get(id=film_id)
        some_film.delete()
        return HttpResponseRedirect("/add-film")
    except:
        return HttpResponseNotFound("Something went wrong")


@permission_required("base_site.add_film", login_url="/login")
def edit_media(request, film_id):
    if request.method == "GET":
        film = Film.objects.get(id=film_id)
        v_quantity = Video.objects.filter(film_id=film_id).count()

        videos_per_page = 5
        page_number = int(request.GET.get('page', 1))
        if page_number > v_quantity / videos_per_page + 1 or page_number < 0:
            return HttpResponseRedirect(f'/edit-film-media/{film_id}')
        start_index = 0 + videos_per_page * (page_number - 1)

        video_list = Video.objects.filter(film_id=film_id).order_by(
            'episode_number')[start_index:videos_per_page * page_number]
        pages_to_render = page_list(v_quantity // videos_per_page + 1, page_number)
        film_media = FilmMediaForm(initial={"film_id": film_id})
        transfer_data = {"video_list": video_list,
                         "form": film_media,
                         "pages": pages_to_render,
                         "film": film,
                         "film_id": film_id}
        return render(request, "edit_media.html", context=transfer_data)
    elif request.method == "POST":
        film_data = FilmMediaForm(request.POST, request.FILES)
        film_data.save()
        return HttpResponseRedirect(f"/edit-film-media/{film_id}")


@permission_required("base_site.add_film", login_url="/login")
def add_test(request):
    fill_random_staff()
    return HttpResponseRedirect("/add-film")


def catalog(request):
    if request.method == "GET":
        films_per_page = 15
        film_name = request.GET.get('q', '')
        print(film_name)
        if film_name != "":
            film_quantity = Film.objects.filter(title__icontains=film_name
                                                ).order_by("id").count()
            page_number = int(request.GET.get('page', 1))
            print(film_quantity)
            if page_number > film_quantity / films_per_page + 1 or page_number < 0:
                return HttpResponseRedirect('/add-film')
            start_index = 0 + films_per_page * (page_number - 1)
            film_list = Film.objects.filter(title__icontains=film_name).order_by('id')\
                [start_index:films_per_page * page_number]
        else:
            film_quantity = Film.objects.order_by("id").count()
            page_number = int(request.GET.get('page', 1))
            if page_number >= film_quantity / films_per_page + 1 or page_number < 0:
                return HttpResponseRedirect('/add-film')
            start_index = 0 + films_per_page * (page_number - 1)
            film_list = Film.objects.order_by('id')\
                [start_index:films_per_page * page_number]
        film_form = FilmForm()
        pages_to_render = page_list(film_quantity // films_per_page + 1, page_number)
        transfer_data = {"film_list": film_list,
                         "form": film_form,
                         "pages": pages_to_render,
                         "last_queue": film_name}
        return render(request, "catalog.html", context=transfer_data)


def register(request):
    if request.method == "POST":
        user_creation_form = UserCreationForm(request.POST)
        if user_creation_form.is_valid():
            print("user created")
            user_creation_form.save()
            return HttpResponseRedirect("/")
    user_creation_form = UserCreationForm()
    transfer_data = {"user_creation_form": user_creation_form}
    return render(request, "register.html", context=transfer_data)


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username,
                            password=password)
        if user is not None:
            print(user.username)
            login(request, user)
        next_link = request.POST["next"]
        print(next_link)
        return HttpResponseRedirect(f"{next_link}")

    next_link = request.GET.get("next", "")
    user_auth_form = AuthenticationForm()
    transfer_data = {"user_creation_form": user_auth_form,
                     "next": next_link}
    return render(request, "login.html", context=transfer_data)


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(f"{request.GET.get('next', '')}")


def get_streaming_video(request, video_id):
    file, status_code, content_length, content_range = open_file(request, video_id)
    response = StreamingHttpResponse(file, status=status_code, content_type='video/mp4')
    response['Accept-Ranges'] = 'bytes'
    response['Content-Length'] = str(content_length)
    response['Cache-Control'] = 'no-cache'
    response['Content-Range'] = content_range
    return response


def get_image(request, video_id):
    image_path = Video.objects.get(id=video_id).image.path
    return FileResponse(open(image_path, "rb"))


def get_poster_image(request, film_id):
    image_path = Film.objects.get(id=film_id).poster_img.path
    return FileResponse(open(image_path, "rb"))


@permission_required("base_site.add_film", login_url="/login")
def edit_video(request, video_id):
    if request.method == "POST":
        video = get_object_or_404(Video, pk=video_id)
        form = FilmMediaForm(request.POST, request.FILES, instance=video)
        form.save()
        return HttpResponseRedirect(f"/edit-video/{video_id}")
    elif request.method == "GET":
        video = get_object_or_404(Video, pk=video_id)
        film = get_object_or_404(Film, pk=video.serializable_value("film_id"))
        form = FilmMediaForm(instance=video)
        transfer_data = {"form": form,
                         "video": video,
                         "film": film}
        return render(request, "edit_episode.html", context=transfer_data)


@permission_required("base_site.add_film", login_url="/login")
def delete_video(request, video_id):
    try:
        video = get_object_or_404(Video, pk=video_id)
        film = get_object_or_404(Film, pk=video.serializable_value("film_id"))
        video.delete()
        return HttpResponseRedirect(f"/edit-film-media/{film.id}")
    except:
        return HttpResponseNotFound("Something went wrong")


@permission_required("base_site.add_film", login_url="/login")
def feed_update(request):
    if request.method == "GET":
        feed_quantity = Feed.objects.count()
        page_number = int(request.GET.get('page', 1))
        films_per_page = 10
        if page_number > (feed_quantity / films_per_page + 1) or page_number < 0:
            return HttpResponseRedirect('/')
        start_index = 0 + films_per_page * (page_number - 1)
        film_indexes = Feed.objects.order_by('-update_date')\
            [start_index:films_per_page * page_number]
        film_data = []
        for one_film in film_indexes:
            try:
                film_data.append((Film.objects.get(
                    id=one_film.serializable_value("film_id")), one_film))
            except:
                pass
        pages_to_render = page_list(feed_quantity // films_per_page, page_number)

        form = FeedForm(initial={"update_date": datetime.datetime.now()})
        transfer_data = {"feed_data": film_data,
                         "pages": pages_to_render,
                         "form": form}
        return render(request, "feed_add.html", context=transfer_data)
    elif request.method == "POST":
        film = get_object_or_404(Film, id=request.POST["film_id"])
        try:
            feed_q = Feed.objects.get(film_id=film)
            feed_q.update_comment = request.POST["update_comment"]
            feed_q.save()
        except:
            Feed.objects.create(film_id=film,
                                update_date=datetime.datetime.now(),
                                update_comment=request.POST["update_comment"])
        return HttpResponseRedirect("feed-update")


@permission_required("base_site.add_film", login_url="/login")
def feed_delete(request, film_id):
    try:
        feed_note = get_object_or_404(Feed, film_id=film_id)
        feed_note.delete()
        return HttpResponseRedirect("/feed-update")
    except:
        return HttpResponseNotFound("Something went wrong")
