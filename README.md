# devops_bot Docker
Для запуска бота нужно использовать команду: <br>
**docker-compose up --build -d**<br>

Либо можно отдельно собрать образы с помощью Dockerfile-ов:<br>
**docker build -t название_образа путь_до_Dockerfile**<br>
И затем запустить docker-compose: <br>
**docker-compose up -d**
**НО** для этого надо закомментировать строки **build** в docker-compose.yml
