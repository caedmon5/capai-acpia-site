#!/usr/bin/env python3
"""
Build script for the CAPAI-ACPIA flat-file site.

Reads YAML data from data/, renders Jinja2 templates from templates/,
and writes flat HTML files to the project root.

Usage:
    python build.py
"""

import os
import glob as globmod
import yaml
from jinja2 import Environment, FileSystemLoader

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, 'data')
TEMPLATES = os.path.join(ROOT, 'templates')


def load_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f)


def load_collection(subdir):
    """Load all YAML files in a data subdirectory, return sorted list."""
    items = []
    pattern = os.path.join(DATA, subdir, '*.yaml')
    for path in globmod.glob(pattern):
        item = load_yaml(path)
        item.setdefault('_file', os.path.basename(path))
        items.append(item)
    items.sort(key=lambda x: x.get('order', 999))
    return items


def build():
    env = Environment(loader=FileSystemLoader(TEMPLATES), autoescape=False)

    # Load site config
    site = load_yaml(os.path.join(DATA, 'site.yaml'))

    # Load collections
    members = load_collection('members')
    events = load_collection('events')
    research_items = load_collection('research')
    media_items = load_collection('media')

    # Categorize events
    upcoming = [e for e in events if e.get('status') == 'upcoming']
    past = [e for e in events if e.get('status') == 'past']
    featured_event = next((e for e in events if e.get('featured')), None)

    # Load page configs
    pages = {}
    for path in globmod.glob(os.path.join(DATA, 'pages', '*.yaml')):
        name = os.path.splitext(os.path.basename(path))[0]
        pages[name] = load_yaml(path)

    # Common context
    common = {'site': site}

    # Build index
    render(env, 'index.html', 'index.html', {
        **common,
        'active_page': 'index',
        'featured_event': featured_event,
        'upcoming_events': upcoming,
        'research_items': research_items,
    })

    # Build members
    render(env, 'members.html', 'members.html', {
        **common,
        'active_page': 'members',
        'page': pages.get('members', {}),
        'members': members,
    })

    # Build events listing
    render(env, 'events.html', 'events.html', {
        **common,
        'active_page': 'events',
        'page': pages.get('events', {}),
        'upcoming_events': upcoming,
        'past_events': past,
    })

    # Build individual event pages
    for ev in events:
        render(env, 'event-detail.html', f"event-{ev['slug']}.html", {
            **common,
            'active_page': 'events',
            'event': ev,
        })

    # Build research
    render(env, 'research.html', 'research.html', {
        **common,
        'active_page': 'research',
        'page': pages.get('research', {}),
        'research_items': research_items,
    })

    # Build teaching
    render(env, 'teaching.html', 'teaching.html', {
        **common,
        'active_page': 'teaching',
        'page': pages.get('teaching', {}),
    })

    # Build media
    render(env, 'media.html', 'media.html', {
        **common,
        'active_page': 'media',
        'page': pages.get('media', {}),
        'media_items': media_items,
    })

    # Build contact
    render(env, 'contact.html', 'contact.html', {
        **common,
        'active_page': 'contact',
        'page': pages.get('contact', {}),
    })

    print("Build complete.")


def render(env, template_name, output_name, context):
    template = env.get_template(template_name)
    html = template.render(**context)
    output_path = os.path.join(ROOT, output_name)
    with open(output_path, 'w') as f:
        f.write(html)
    print(f"  {output_name}")


if __name__ == '__main__':
    build()
