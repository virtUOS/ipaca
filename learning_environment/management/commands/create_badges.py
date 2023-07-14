from django.core.management import BaseCommand
from django_gamification.models import BadgeDefinition, Category


class Command(BaseCommand):
    help = 'create badges'

    def handle(self, *args, **options):

        gold_badges = Category.objects.create(name='Gold Badges', description='These are the top badges')
        silver_badges = Category.objects.create(name='Silver Badges', description='These are the secondary badges')

        BadgeDefinition.objects.create(
            name='Badge of Awesome',
            description='You proved your awesomeness',
            points=50,
            category=gold_badges,
        )

        BadgeDefinition.objects.create(
            name='Badge of Coolness',
            description='You proved your coolness',
            points=50,
            category=silver_badges,
        )

