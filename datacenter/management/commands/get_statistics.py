from django.core.management.base import BaseCommand
from datacenter.models import *

import csv


class Command(BaseCommand):
    help = 'Получить статистку'

    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            help='Путь до .csv файла, куда будет выгружена информация',
            type=str,
            default='statistics.csv'
        )
    def handle(self, *args, **options):
        path = options['path']
        if '.csv' not in path:
            print('[ERROR] Путь до файла указан неверно! Нужно укзать путь до файла. Пример: /home/test.csv')
            return
        try:
            file = open(path, 'w')
            file.close()
        except OSError:
            print('[ERROR] Путь указан неверно. Не найдена папка, в которую нужно положить файл! Проверь')
        with open(path, 'w', newline='') as csvfile:
            fieldnames = ['Источник', 'Кол-во заказов', 'Общая сумма в $']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for source in Source.objects.all():
                data = dict()
                orders = Order.objects.filter(account__product__source=source)
                data['Источник'] = source.name
                data['Кол-во заказов'] = orders.count()
                price = 0
                for order in orders:
                    print(order.account.product.price)
                    price += order.account.product.price
                data['Общая сумма в $'] = price
                writer.writerow(data)
        print('Статистика загружена в файл', path)