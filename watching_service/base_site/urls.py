from django.urls import path
from .views import feed, film_page, edit_film, delete_film, \
    add_film, add_test, catalog, \
    register, login_view, feed_update, \
    get_streaming_video, edit_media, \
    logout_view, edit_video, get_image, \
    delete_video, get_poster_image, feed_delete


urlpatterns = [
    path('', feed),
    path('film/<int:film_id>', film_page),
    path('add-film', add_film),
    path('edit-film/<int:film_id>', edit_film),
    path('delete-film/<int:film_id>', delete_film),
    path('edit-film-media/<int:film_id>', edit_media),
    path('add-film/test', add_test),
    path('catalog', catalog),
    path('register', register),
    path('login', login_view),
    path('logout', logout_view),
    path('stream/<int:video_id>', get_streaming_video),
    path('images/<int:video_id>', get_image),
    path('images/p/<int:film_id>', get_poster_image),
    path('edit-video/<int:video_id>', edit_video),
    path('delete-video/<int:video_id>', delete_video),
    path('feed-update', feed_update),
    path('delete-feed/<int:film_id>', feed_delete)
]
