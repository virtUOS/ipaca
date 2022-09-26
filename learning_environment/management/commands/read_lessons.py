from django.core.management.base import BaseCommand, CommandError
import glob
import re
import json5
from learning_environment.models import Lesson
from learning_environment.its.base import Json5ParseException

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        num_lessons_created = 0
        for filename in glob.glob("data/lessons/lesson_*.json5"):
            with open(filename, "r", encoding="UTF-8") as f:
                lesson_json5 = f.read()
                try:
                    Lesson.check_json5(lesson_json5)
                except Json5ParseException as e:
                    print("Lesson {} invalid. Error message: \n{}".format(filename, e))

                Lesson.create_from_json5(lesson_json5)
                num_lessons_created += 1

        self.stdout.write(self.style.SUCCESS('Successfully created {} lessons.'.format(num_lessons_created)))