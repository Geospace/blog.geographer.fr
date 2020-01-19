import os

import urllib.parse
from pelican import signals, contents

# Generate an XML sitemap for the blog

FILENAME = 'sitemap.xml'

EXCLUDE_SLUGS = [
    '404',
    'posts',  # The post index, does not really have content
    'internet-error',  # The WPA internet error page, not relevant
]

# TODO: Get custom frequencies from configuration file
CHANGE_FREQUENCIES = {
    'resume': 'yearly',
    '_index': 'daily',
    '_articles': 'monthly',
    '_pages': 'monthly',
    '_default': 'weekly'
}

# TODO: Get custom frequencies from configuration file
PRIORITIES = {
    'hexpresso-fix': 0.6,
    '_default': 0.5
}

DATE_TEMPLATE = '\n    <lastmod>{}</lastmod>'

URL_TEMPLATE = '''  <url>
    <loc>{loc}</loc>{lastmod}
    <changefreq>{changefreq}</changefreq>
    <priority>{priority}</priority>
  </url>'''

SITEMAP_TEMPLATE = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{}
</urlset>
'''


def get_content_priority(content):
    if content.slug in PRIORITIES:
        return PRIORITIES[content.slug]

    return PRIORITIES['_default']


def get_content_change_frequency(content):
    if content.slug in CHANGE_FREQUENCIES:
        return CHANGE_FREQUENCIES[content.slug]

    if isinstance(content, contents.Article):
        return CHANGE_FREQUENCIES['_articles']

    if isinstance(content, contents.Page):
        return CHANGE_FREQUENCIES['_pages']

    return CHANGE_FREQUENCIES['_default']


def get_content_last_date(content):
    # Prioritize the last update date
    if hasattr(content, 'modified'):
        return content.modified

    if hasattr(content, 'date'):
        return content.date

    return None


class SitemapGenerator():
    def __init__(self, context, settings, path, theme, output_path):
        self.context = context
        self.output_path = output_path

    def generate_output(self, writer):
        # Final file path
        path = os.path.join(self.output_path, FILENAME)

        # Extract pages and articles
        content = \
            self.context['articles'] + \
            self.context['pages']

        # Remove the content that must be excluded
        content = [c for c in content if c.slug not in EXCLUDE_SLUGS]

        # Store all the url blocks
        buffer = []

        # Iterate over all pages, articles, mixed
        for c in content:
            # Date can be YYYY-MM-DD or nothing
            date = get_content_last_date(c)
            if date is not None:
                date = DATE_TEMPLATE.format(date.strftime('%Y-%m-%d'))
            else:
                date = ''

            # Join site url and content slug
            url = urllib.parse.urljoin(self.context['SITE_URL'], c.slug)
            # Update frequency
            frequency = get_content_change_frequency(c)
            # Document priority
            priority = get_content_priority(c)

            # Store the URL block
            buffer.append(URL_TEMPLATE.format(
                loc=url,
                lastmod=date,
                changefreq=frequency,
                priority=priority
            ))

        # TODO: Do not forget the index

        # Join all the URL blocks into the final template
        sitemap = SITEMAP_TEMPLATE.format('\n'.join(buffer))

        # Write sitemap to disk
        with open(path, 'w+') as f:
            f.write(sitemap)


def get_generators(generators):
    return SitemapGenerator


def register():
    signals.get_generators.connect(get_generators)
