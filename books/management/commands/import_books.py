import json
from django.core.management.base import BaseCommand
from books.models import *
import uuid
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Import books from JSON file'
    MAX_SLUG_LENGTH = 50
    MAX_TITLE_LENGTH = 50
    
    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to JSON file')
    
    def handle(self, *args, **options):
        with open(options['json_file'], 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, dict) and 'books' in data:
            data = data['books']
        if not isinstance(data, list):
            self.stderr.write(self.style.ERROR("JSON file must contain a list of books or a dict with key 'books'."))
            return
        
        for item in data:
            # Create/get authors
            authors = []
            for author_data in item.get('authors', []):
                author_slug = (author_data.get('slug') or slugify(author_data['name']))[:self.MAX_SLUG_LENGTH]
                author, created = Author.objects.get_or_create(     
                    id=author_data['id'],
                    defaults={
                        'name': author_data['name'][:self.MAX_TITLE_LENGTH],
                        'slug': author_slug
                    }
                )
                authors.append(author)
            
            # Create/get category
            category_data = item.get('categories', {})
            category = None
            if category_data:
                category_slug = (category_data.get('slug') or slugify(category_data['name']))[:self.MAX_SLUG_LENGTH]
                # Đảm bảo slug là duy nhất
                base_slug = category_slug
                i = 1
                while Category.objects.filter(slug=category_slug).exists():
                    category_slug = f"{base_slug}-{i}"
                    if len(category_slug) > self.MAX_SLUG_LENGTH:
                        category_slug = category_slug[:self.MAX_SLUG_LENGTH - len(f"-{i}")] + f"-{i}"
                    i += 1
                category, created = Category.objects.get_or_create(
                    id=category_data['id'],
                    defaults={
                        'name': category_data['name'][:self.MAX_TITLE_LENGTH],
                        'slug': category_slug,
                        'is_leaf': category_data.get('is_leaf', True)
                    }
                )
            
            # Create book
            book_id = item.get('id')
            try:
                book_id = item.get('id')
                book_uuid = uuid.UUID(str(book_id))
                slug = (item.get('slug') or slugify(item['name']))[:self.MAX_SLUG_LENGTH]
                title = item['name'][:self.MAX_TITLE_LENGTH]
                book, created = Book.objects.get_or_create(
                    id=book_uuid,
                    defaults={
                        'title': title,
                        'slug': slug,
                        'description': item.get('description', ''),
                        'list_price': item['list_price'],
                        'original_price': item.get('original_price', item['list_price']),
                        'rating_average': item.get('rating_average', 0),
                        'quantity_sold': item.get('quantity_sold', {}).get('value', 0),
                        'quantity_sold_text': item.get('quantity_sold', {}).get('text', ''),
                    }
                )
            except (ValueError, TypeError):
                slug = (item.get('slug') or slugify(item['name']))[:self.MAX_SLUG_LENGTH]
                title = item['name'][:self.MAX_TITLE_LENGTH]
                book, created = Book.objects.get_or_create(
                    title=title,
                    slug=slug,
                    defaults={
                        'description': item.get('description', ''),
                        'list_price': item['list_price'],
                        'original_price': item.get('original_price', item['list_price']),
                        'rating_average': item.get('rating_average', 0),
                        'quantity_sold': item.get('quantity_sold', {}).get('value', 0),
                        'quantity_sold_text': item.get('quantity_sold', {}).get('text', ''),
                    }
                )
            
            if created:
                # Add authors
                book.authors.set(authors)
                if category:
                    book.categories.add(category)
                
                # Add images
                for img_data in item.get('images', []):
                    BookImage.objects.create(
                        book=book,
                        base_url=img_data['base_url'],
                        large_url=img_data.get('large_url', ''),
                        medium_url=img_data.get('medium_url', ''),
                        small_url=img_data.get('small_url', ''),
                        thumbnail_url=img_data.get('thumbnail_url', ''),
                is_gallery=img_data.get('is_gallery', True)
            )
        self.stdout.write(self.style.SUCCESS(f'Successfully imported {len(data)} books'))