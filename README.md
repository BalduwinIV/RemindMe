# RemindMe
RemindMe - Flask web-application в котором можно записывать пометки и напоминания, а также создавать собственный TODO list. Интерфейс минималистичный и интуитивно понятен. Для использования необходимо зарегистрироваться или войти в свой аккаунт.

Технологии:
  - Flask
  - SQLAlchemy
  - werkzeug
  - WTForms
  - Bootstrap 4

Структура: <br />
-data (Работа с БД) <br />
&nbsp;&nbsp;&nbsp;&nbsp;__all_models.py <br />
&nbsp;&nbsp;&nbsp;&nbsp;db_session.py <br />
&nbsp;&nbsp;&nbsp;&nbsp;users.py <br />
-db <br />
&nbsp;&nbsp;&nbsp;&nbsp;data.sqlite (Сама БД) <br />
-static <br />
&nbsp;&nbsp;&nbsp;&nbsp;-css <br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;style.css <br />
&nbsp;&nbsp;&nbsp;&nbsp;-img (Фотографии в Features) <br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;feature_img.png <br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;release_img.png <br />
-templates <br />
&nbsp;&nbsp;&nbsp;&nbsp;base.html <br />
&nbsp;&nbsp;&nbsp;&nbsp;content.html (/notes) <br />
&nbsp;&nbsp;&nbsp;&nbsp;create_note.html (/create_note) <br />
&nbsp;&nbsp;&nbsp;&nbsp;create_task.html (/create_task) <br />
&nbsp;&nbsp;&nbsp;&nbsp;features.html (/features) <br />
&nbsp;&nbsp;&nbsp;&nbsp;index.html (/) <br />
&nbsp;&nbsp;&nbsp;&nbsp;login.html (/login) <br />
&nbsp;&nbsp;&nbsp;&nbsp;permission.html (Защита от посторонних пользователей) <br />
&nbsp;&nbsp;&nbsp;&nbsp;profile.html (/profile) <br />
&nbsp;&nbsp;&nbsp;&nbsp;register.html (/register) <br />
&nbsp;&nbsp;&nbsp;&nbsp;tasks.html (/tasks) <br />
main.py (Весь backend) <br />
notes_api.py (Notes API) <br />
users_api.py (Users API) <br />

API: <br />
&nbsp;&nbsp;&nbsp;&nbsp;[GET] /api/notes - Все записки <br />
&nbsp;&nbsp;&nbsp;&nbsp;[POST] /api/notes/ - Добавить записку <br />
&nbsp;&nbsp;&nbsp;&nbsp;[GET] /api/notes/<int:note_id> - Конкретная записка <br />
&nbsp;&nbsp;&nbsp;&nbsp;[PUT] /api/notes/<int:note_id> - Изменить записку <br />
&nbsp;&nbsp;&nbsp;&nbsp;[DELETE] /api/notes/<int:note_id> - Удалить записку <br />
  <br />
&nbsp;&nbsp;&nbsp;&nbsp;[GET] /api/users - Все пользователи <br />
&nbsp;&nbsp;&nbsp;&nbsp;[POST] /api/users/check_password - Проверить пароль у пользователя <br />
&nbsp;&nbsp;&nbsp;&nbsp;[POST] /api/users/ - Добавить пользователя <br />
&nbsp;&nbsp;&nbsp;&nbsp;[GET] /api/users/<int:user_id> - Конкретный пользователь <br />
&nbsp;&nbsp;&nbsp;&nbsp;[PUT] /api/users/<int:user_id> - Изменить данные пользователя <br />
&nbsp;&nbsp;&nbsp;&nbsp;[DELETE] /api/users/<int:user_id> - Удалить пользователя <br />
