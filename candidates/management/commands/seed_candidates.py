import random
from django.core.management.base import BaseCommand
from faker import Faker
from candidates.models import Candidate

class Command(BaseCommand):
    help = 'Seed the database with 1 million candidate records'

    def handle(self, *args, **kwargs):
        fake = Faker()
        batch_size = 10000  # Number of records to insert in one batch
        total_records = 1000000  # Total number of candidates to seed

        genders = ['M', 'F', 'O']

        self.stdout.write(self.style.WARNING(f'Starting to seed {total_records} candidates...'))

        candidates = []
        for i in range(total_records):
            candidates.append(Candidate(
                name=fake.name(),
                age=random.randint(20, 50),
                gender=random.choice(genders),
                email=fake.unique.email(),
                phone_number=fake.unique.phone_number()
            ))

            # Insert in batches
            if len(candidates) == batch_size:
                Candidate.objects.bulk_create(candidates)
                self.stdout.write(self.style.SUCCESS(f'{len(candidates)} candidates seeded...'))
                candidates = []  # Reset the batch

        # Insert any remaining candidates
        if candidates:
            Candidate.objects.bulk_create(candidates)
            self.stdout.write(self.style.SUCCESS(f'Final {len(candidates)} candidates seeded...'))

        self.stdout.write(self.style.SUCCESS(f'Completed seeding {total_records} candidates!'))