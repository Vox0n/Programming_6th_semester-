# Сайт на Hugo с автоматической публикацией через SourceCraft

Готовый сайт можно посмотреть здесь:
[https://prog6.sourcecraft.site/lb1/](https://prog6.sourcecraft.site/lb1/)
Ссылка на репозиторий 
[https://sourcecraft.dev/prog6/lb1/browse/.sourcecraft/ci.yaml?rev=main&range=l4c12l4c12](https://sourcecraft.dev/prog6/lb1/browse/.sourcecraft/ci.yaml?rev=main&range=l4c12l4c12)
## О чём этот проект

Этот сайт сделан с помощью генератора статических сайтов Hugo.
Исходники хранятся в репозитории SourceCraft.
При каждом изменении кода сайт автоматически пересобирается и публикуется.

## Как это работает 

1. **Проверка оформления текстов.** Специальная программа смотрит все файлы с расширением `.md` и проверяет, что они написаны по правилам Markdown.
2. **Проверка ссылок.** Другая программа проходит по всем ссылкам внутри текстов и смотрит, не ведут ли они на несуществующие страницы.
3. **Сборка и публикация.** Если проверки прошли успешно, сервер скачивает Hugo, собирает из текстов готовые HTML-страницы и загружает их в ветку `release`. Платформа SourceCraft автоматически публикует эту ветку в интернет.


## Код 


```yaml

on:
  push:
    workflows: [build-site]
    filter:
      branches: main

# Здесь описано, что именно делать при пуше
on:
  push:
    workflows: build-and-publish-hugo
    filter:
      branches: main

workflows:
  build-and-publish-hugo:
    tasks:
      - name: build-and-deploy
        cubes:
          - name: lint-markdown
            image: docker.io/tmknom/markdownlint:latest
            script:
              - markdownlint 'content/**/*.md' 

          - name: build-hugo-site
            image: docker.io/hugomods/hugo:latest
            script:
              - hugo version
              - hugo --gc --minify

          - name: publish-to-release-branch
            script:
              - git checkout -b release
              - git add ./public
              - "git commit -m \"feat: автоматическое обновление сайта\""
              - "git push origin release -f"
      


