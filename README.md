进入social_book文件夹
下载对应版本的Python和Django
Python=3.8.20
Django=3.2.24
进入settings.py配置数据库

`根目录`下使用
```py
python manage.py makemigrations # 准备迁移，产生core/migrations下的迁移文件
python manage.py migrate # 迁移数据库
python manage.py runserver # 本地启动
```
