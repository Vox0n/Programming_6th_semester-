import asyncio
import aiohttp
from flask import Flask, render_template, request

app = Flask(__name__)

# URL-адреса фейкового API, откуда мы будем брать данные
USERS_URL = "https://jsonplaceholder.typicode.com/users"
POSTS_URL = "https://jsonplaceholder.typicode.com/posts"


async def get_users(session):
    """
    Получает список всех пользователей из JSONPlaceholder.
    session — это "клиент", через который мы делаем HTTP-запросы.
    timeout=5 — если сервер не ответит за 5 секунд, считаем, что что-то пошло не так.
    Если произошла ошибка (нет интернета, сервер упал и т.п.) — возвращаем пустой список.
    """
    try:
        async with session.get(USERS_URL, timeout=5) as resp:
            return await resp.json()
    except:
        return []  # Пустой список лучше, чем ошибка, которая уронит всю программу


async def get_posts(session):
    """Получает все посты. Работает аналогично get_users."""
    try:
        async with session.get(POSTS_URL, timeout=5) as resp:
            return await resp.json()
    except:
        return []


async def get_user_name(session, user_id):
    """
    Получает имя одного пользователя по его ID.
    Нужно для того, чтобы подписать автора у каждого найденного поста.
    Если пользователь не найден или произошла ошибка — возвращаем "Неизвестен".
    """
    try:
        url = f"https://jsonplaceholder.typicode.com/users/{user_id}"
        async with session.get(url, timeout=5) as resp:
            data = await resp.json()
            return data.get('name', 'Неизвестен')
    except:
        return 'Неизвестен'


def filter_users(users, username=None, email=None):
    """
    Фильтрует список пользователей по username и email.
    Поиск без учёта регистра: приводим всё к нижнему регистру (lower()).
    Если пользователь подходит под все указанные условия — добавляем его в результат.
    """
    result = []
    for u in users:
        ok = True
        if username and username.lower() not in u.get('username', '').lower():
            ok = False
        if email and email.lower() not in u.get('email', '').lower():
            ok = False
        if ok:
            result.append(u)
    return result


def filter_posts(posts, title=None, body=None):
    """Фильтрует посты по заголовку и тексту. Принцип тот же, что и у filter_users."""
    result = []
    for p in posts:
        ok = True
        if title and title.lower() not in p.get('title', '').lower():
            ok = False
        if body and body.lower() not in p.get('body', '').lower():
            ok = False
        if ok:
            result.append(p)
    return result


async def search(username, email, title, body):
    """
    Самая важная функция: здесь происходит вся асинхронная магия.
    
    Шаги:
    1. Проверяем, какие данные нужны: пользователи или посты (или и то, и другое).
    2. Создаём асинхронные задачи только для нужных запросов.
    3. Запускаем их параллельно через asyncio.gather() — это позволяет не ждать
       каждый запрос по очереди, а выполнять их одновременно.
    4. После получения данных — фильтруем их.
    5. Для каждого найденного поста параллельно загружаем имя автора.
    """
    
    # Определяем, что ищем: пользователей (по username/email) и/или посты (по title/body)
    need_users = bool(username or email)
    need_posts = bool(title or body)
    
    # Если вообще ничего не заполнено — сразу возвращаем пустые списки
    if not need_users and not need_posts:
        return [], []
    
    users = []
    posts = []
    
    # Создаём сессию для HTTP-запросов. Она используется для всех запросов внутри этого блока.
    async with aiohttp.ClientSession() as session:
        tasks = []
        
        # Создаём задачи только для того, что реально нужно запросить
        if need_users:
            tasks.append(get_users(session))
        else:
            # Если пользователи не нужны — ставим "заглушку", которая мгновенно возвращает пустой список
            tasks.append(asyncio.sleep(0, result=[]))
            
        if need_posts:
            tasks.append(get_posts(session))
        else:
            tasks.append(asyncio.sleep(0, result=[]))
        
        # await asyncio.gather() — запускает все задачи параллельно и ждёт их завершения
        # Это ключевой момент: запросы к пользователям и постам выполняются одновременно!
        results = await asyncio.gather(*tasks)
        
        # Забираем результаты
        if need_users:
            users = results[0]
        if need_posts:
            posts = results[1]
    
    # Фильтруем полученные данные по критериям поиска
    if users:
        users = filter_users(users, username, email)
    
    if posts:
        posts = filter_posts(posts, title, body)
        
        # Если есть найденные посты — для каждого нужно узнать имя автора
        if posts:
            # Открываем новую сессию для запросов к /users/{id}
            async with aiohttp.ClientSession() as session:
                # Создаём список задач: по одной на каждый пост
                author_tasks = []
                for p in posts:
                    author_tasks.append(get_user_name(session, p.get('userId')))
                
                # И снова asyncio.gather — все запросы за именами авторов выполняются параллельно!
                # Это гораздо быстрее, чем запрашивать их по очереди.
                author_names = await asyncio.gather(*author_tasks)
                
                # Добавляем полученные имена к каждому посту
                for i, p in enumerate(posts):
                    p['author_name'] = author_names[i]
    
    return users, posts


@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Главная страница.
    GET — просто показываем форму.
    POST — пользователь отправил форму, обрабатываем поиск.
    """
    users = []
    posts = []
    error = None
    
    if request.method == 'POST':
        # Забираем данные из формы, удаляем лишние пробелы по краям
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        title = request.form.get('title', '').strip()
        body = request.form.get('body', '').strip()
        
        # Проверяем, что пользователь заполнил хотя бы одно поле
        if not any([username, email, title, body]):
            error = "Заполните хотя бы одно поле"
        else:
            # asyncio.run() — запускает асинхронную функцию внутри синхронного Flask-приложения
            # Это "мостик" между синхронным миром Flask и асинхронным миром asyncio
            users, posts = asyncio.run(search(username, email, title, body))
            
            # Обрезаем длинные тексты постов до 150 символов для красивого отображения
            for p in posts:
                if len(p.get('body', '')) > 150:
                    p['body_short'] = p['body'][:150] + '...'
                else:
                    p['body_short'] = p.get('body', '')
    
    # Отдаём HTML-шаблон, передавая в него результаты поиска или ошибку
    return render_template('index.html', 
                         users=users, 
                         posts=posts, 
                         error=error)


if __name__ == '__main__':
    # debug=True — автоматически перезагружает сервер при изменении кода
    app.run(debug=True)