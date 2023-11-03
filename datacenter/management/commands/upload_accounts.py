from django.core.management.base import BaseCommand
from datacenter.models import *
from django.core.files.base import ContentFile


import csv


class Command(BaseCommand):
    help = 'Загрузить аккаунты для товара'

    def add_arguments(self, parser):
        parser.add_argument(
            'product',
            help='ID товара, в который нужно загрузить аккаунты',
            type=str,
        )
        parser.add_argument(
            'path',
            help='Путь до .txt файла, в котором лежат аккаунты',
            type=str,
        )
    def handle(self, *args, **options):
        path = options['path']
        product_id = options['product']
        if '.txt' not in path:
            print('[Error] Путь до файла указан неверно! Нужно укзать путь до файла. Пример: /home/accounts.txt')
            return
        try:
            file = open(path, 'r')
            file.close()
        except OSError:
            print('[Error] Путь указан неверно. Не найдена папка, в которую нужно положить файл! Проверь')
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            print(f'[ERROR] Товар с ID {product_id} не найден!')
            return
        with open(path, 'r') as file:
            accounts = file.readlines()
        for account_data in accounts:
            account_data = account_data.replace('\n', '').split()
            file = ContentFile(''.join(account_data))
            account = Account.objects.create(
                product=product
            )
            account.file.save(f'account_{account.id}_{account_data[0]}.txt', content=file, save=True)
        print(f'Создано {len(accounts)} шт аккаунтов для товара {product.name_ru}')
