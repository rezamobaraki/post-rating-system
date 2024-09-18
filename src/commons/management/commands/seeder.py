from django.core.management import BaseCommand

from accounts.factories.user import UserFactory
from books.factories.book import BookFactory
from books.factories.bookmark import BookmarkFactory
from books.factories.review import ReviewFactory


class Command(BaseCommand):
    help = 'Seeder is a command to seed the database'

    def add_arguments(self, parser):
        parser.add_argument('-u', '--user', type=int, help='Number of User to create')
        parser.add_argument('-p', '--post', type=int, help='Number of Post to create')
        parser.add_argument('-r', '--rate', type=int, help='Number of Rate to create')

    def handle(self, *args, **options):
        self.stdout.write('Starting to seed the database...')
        user_count = options['user']
        post_count = options['post']
        rate_count = options['rate']

        user_instances = []
        user_data_output = []
        post_instances = []
        rate_instances = []

        admin_user = UserFactory()
        admin_user.is_superuser = True
        admin_user.is_staff = True
        admin_user.save()
        user_data_output.append(
            f'\nAdmin User Details:\n'
            f'  Email: {admin_user.email}\n'
            f'  Password: new_password\n'
        )

        if user_count:
            for i in range(user_count):
                user = UserFactory()
                user_data_output.append(
                    f'\nUser-{user.id} Details:\n'
                    f'  Email: {user.email}\n'
                    f'  Password: new_password\n'
                )
                user_instances.append(user)
                self.print_progress_bar(i + 1, user_count, prefix='User')

        if post_count:
            for i in range(post_count):
                book = BookFactory()
                post_instances.append(book)
                self.print_progress_bar(i + 1, post_count, prefix='Book')

        if rate_count:
            if post_instances and user_instances:
                total_reviews = min(rate_count, len(post_instances) * len(user_instances))
                iteration = 0
                for book in post_instances:
                    for user in user_instances:
                        if iteration < rate_count:
                            rate_instances.append(ReviewFactory(book=book, user=user))
                            iteration += 1
                            self.print_progress_bar(iteration, total_reviews, prefix='Review')
            else:
                self.stdout.write(self.style.WARNING('Please create some users and posts first'))


        for output in user_data_output:
            self.stdout.write(self.style.NOTICE(output))

        self.stdout.write(self.style.SUCCESS('Database seeded successfully'))

    def print_progress_bar(self, iteration, total, prefix='applying', suffix='', length=20):
        """
        Call in a loop to create a terminal progress bar.
        @params:
            iteration   - Required  : current iteration (Int)
            total       - Required  : total iterations (Int)
            prefix      - Optional  : prefix string (Str)
            suffix      - Optional  : suffix string (Str)
            length      - Optional  : character length of bar (Int)
        """
        percent = 100 * (iteration / float(total))
        filled_length = int(length * iteration // total)
        bar = '⣿' * filled_length + ' ' * (length - filled_length)

        if iteration < total:
            color_start = '\033[94m'
        else:
            color_start = '\033[92m'

        color_end = '\033[0m'

        progress = f'{prefix} [{color_start}{bar}{color_end}] {percent:.1f}% {suffix}'
        self.stdout.write(f'\r{progress}', ending='')
        if iteration == total:
            self.stdout.write('\n')
