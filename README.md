**Данный эксперимент проводился на Ubuntu 24.04.1 LTS, все команды брались именно для данной ОС, и запускались только на ней**

#### Установка нужных вещей



Если не установлен docker, установить его можно через терминал введя следующие команды:

`sudo apt-get update`

`sudo apt-get install ca-certificates curl`

`sudo install -m 0755 -d /etc/apt/keyrings`

`sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc`

`sudo chmod a+r /etc/apt/keyrings/docker.asc`

`echo   "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \`

`$(. /etc/os-release && echo "$VERSION_CODENAME") stable" |   sudo tee /etc/apt/sources.list.d/docker.list > /dev/null`

`sudo apt-get update`

`sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin`

Далее на сайте https://docs.docker.com/desktop/setup/install/linux/ubuntu/ скачать DEB пакет Docker Desktop и ввести следующие команды:

`sudo apt-get update`

`sudo apt-get install ./docker-desktop-amd64.deb`

А теперь установим MinIO:

`wget https://dl.min.io/server/minio/release/linux-amd64/archive/minio_20241213221912.0.0_amd64.deb -O minio.deb`  
`sudo dpkg -i minio.deb`  

Также нам понадобятся некоторые образы, получаемые через данные команды:

`sudo docker pull python:3-slim`  

`sudo docker pull minio/minio`  

#### Основная часть

вводим в терминал:

`git clone <ссылка на данный репозиторий>`

Так мы скачаем данный репозиторий в папку с тем же именем. Заходим в нее через cd.

Часть настроек контейнеров предустановлена в файлах из данной директории.
Сделаем новую настройку - ограничение места на диске для хранилища.
Введем следующую команду, в данном случае ограничение будет составлять 100 МБ.

`sudo docker volume create --driver local --opt type=tmpfs --opt device=tmpfs --opt o=size=100m clouds_minio_data`  


Находясь в папке с *compose.yaml* и т.д. создадим наши контейнеры:

`sudo docker-compose build`  

В этой же папке создаем новую:

`mkdir files`  

В данную папку кидаем файлы, по объему в сумме превышающие 100 МБ. Создать их можно, например с помощью

`yes|head -<кол-во символов/2> > <имя файла>`

Для начала, например, загрузим три файла объемом 40 МБ.

Далее, когда файлы загружены пишем:

`sudo docker-compose up`  

В code.py через API MinIO для Python пытаемся послать файлы. Сначала подключаемся к нашему локальному MinIO через *minio()* (подключение по http), 
а дальше создаём mybucket (что-то вроде папки), и посылаем файлы по одному из директории files. Файлы разбиваются на блоки, 
отправляются на сервер. При ошибке code.py завершает свое выполнение с кодом 1.

Во время данных процедур в консоли мы увидим различную выходную информацию, а дальше сообщение об ошибке (имена файлов в примере были a, b, c):

`minio.error.S3Error: S3 operation failed; code: IncompleteBody, message: You did not provide the number of bytes specified by the Content-Length HTTP header., resource: /mybucket/a, request_id: 18141DC85142D0F8, host_id: dd9025bab4ad464b049177c95eb6ebf374d3b3fd1af9251148b658df7ac2e3e8, bucket_name: mybucket, object_name: a`

Теперь посмотрим на содержимое сервера MinIO, для этого:

Перейдем по данной ссылке **http://localhost:9001**.  
Логин для входа: **user1234**  
Пароль для входа: **password**  

Высветится окошко с mybucket, там мы увидим, что были добавленны только 2 файла из трех, третьему не хватило места, что мы и увидели в консоли.
В этом окошке мы можем почистить папку и удалить загруженные файлы из хранилища. 
Но после проделывания данной процедуры невместившиеся файлы не станут досылаться.
Выходит, что сервер просто игнорирует файлы, если памяти стало недостаточно.
 

code: IncompleteBody означает, что файл разбивался на блоки, 
но приложение не смогло заслать все блоки, что и означает "неполное тело".

Это был случай, когда размеры всех трех файлов были больше размера 1 блока.

После этого прожимаем ctrl+C и пишем команду:

`sudo docker-compose down`

Далее видоизменяем содержимое папки files. Пусть на этот раз в папке будут лежать два файла, один объемом 97 МБ, а второй 4 МБ. 
 
Снова запустим процесс загрузки файлов через

`sudo docker-compose up`  

Видим ошибку, но, если первым в хранилище добавился файл побольше, она будет уже другая:

`urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='minio', port=9000): Max retries exceeded with url: /mybucket/a (Caused by ResponseError('too many 500 error responses'))`

Снова зайдя по ссылке увидим, что в хранилище только 1 большой файл. Малеьнкий файл не разбивался на блоки, и, судя по ошибке, множество раз пытался благодаря code.py загрузиться в хранилку , что не вышло из-за лимита.

Окончив эксперимент, снова пропишем команду

`sudo docker-compose down`

После чего:

`sudo docker volume rm clouds_minio_data`

Тем самым освободив занятую нами память.

