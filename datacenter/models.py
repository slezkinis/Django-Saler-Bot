from django.db import models
from django.utils import timezone


class Category(models.Model):
    name_ru = models.CharField('Название на русском', max_length=100)
    name_en = models.CharField('Название на английском', max_length=100)

    class Meta:
        verbose_name = 'Геолокация'
        verbose_name_plural = 'Геолокации'


    def __str__(self) -> str:
        return self.name_ru


class Source(models.Model):
    name = models.CharField('Название', max_length=100)

    class Meta:
        verbose_name = 'Источник'
        verbose_name_plural = 'Источники'

    def __str__(self) -> str:
        return self.name

     
class Product(models.Model):
    name_ru = models.CharField('Название на русском', max_length=100)
    name_en = models.CharField('Название на английском', max_length=100)
    source = models.ForeignKey(Source, models.CASCADE, related_name='products', verbose_name='Источник', null=True)
    description_ru = models.TextField('Описание на русском')
    description_en = models.TextField('Описание на английском')
    price = models.DecimalField(verbose_name='Цена в $', max_digits=5, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name='К какой категории привязан')

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
    
    def __str__(self) -> str:
        return self.name_ru


class User(models.Model):
    LANGUAGES = (
        ('ru', 'Русский'),
        ('en', 'Английский')
    )
    tg_id = models.IntegerField('TG id')
    username = models.CharField('Имя пользователя', max_length=100, blank=True, null=True)
    selected_language = models.CharField('Язык', choices=LANGUAGES, default='ru', max_length=100)
    money = models.DecimalField(verbose_name='Кол-во $', max_digits=5, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = 'Покупатель'
        verbose_name_plural = 'Покупатели'
    
    def __str__(self) -> str:
        if self.username:
            return f'{self.username}_{self.tg_id}'
        return self.tg_id


class Account(models.Model):
    file = models.FileField('Файл с кредами', upload_to='accounts/')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='accounts', verbose_name='К какому товару привязан')
    is_enabled = models.BooleanField('Активен ли аккаунт', default=True)
    
    class Meta:
        verbose_name = 'Продаваемый аккаунт'
        verbose_name_plural = 'Продаваемые аккаунты'

    def __str__(self) -> str:
        return f'{self.file.name}_{self.product.name_ru}'


class Order(models.Model):
    STATUS = (
        ('user_in_checking', 'Пользователь проверяет/OK'),
        ('not_ok', 'Аккаунт невалиден'),
        ('admin_in_checking', 'Админ проверяет на валидность'),
        ('canceled', 'Заявка отклонена')
    )
    user = models.ForeignKey(User, models.CASCADE, related_name='orders', verbose_name='Пользователь')
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, related_name='orders', null=True, verbose_name='Продаваемый аккаунт')
    status = models.CharField('Статус', choices=STATUS, default='user_in_checking', max_length=100)
    buy_time = models.DateTimeField(
        'Время покупки',
        default=timezone.now,
        db_index=True
    )

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self) -> str:
        return f'{self.user}_{self.account.file.name}_{self.status}'

# Settings

class Setting(models.Model):
    time_to_check = models.IntegerField('Время проверки аккаунта в минутах')
    _singleton = models.BooleanField(default=True, editable=False, unique=True)

    class Meta:
        verbose_name = 'Настройки'
        verbose_name_plural = 'Настройки'

    def __str__(self) -> str:
        return 'Время для пользователя на проверку аккаунта'
