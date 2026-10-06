# The Final Quilt — Ministry Archive

A responsive fandom-style website for an original fictional universe, featuring lore, Primitive–Composite Mechanics, character profiles, a searchable glossary, and a story seed generator.

## Run locally

No dependencies or build step required. With Python 3:

```sh
cd /workspace/internetwomanagementministry
python3 -m http.server 8000 --bind 127.0.0.1 --directory site
```

You can also open `site/index.html` directly in a browser. The page runs entirely locally and does not connect to accounts or remote services.

## Publish

Upload the contents of `site/` to a static hosting service. On GitHub Pages, publish this directory using a Pages deployment workflow or copy its contents into the hosting provider's configured publish directory. Hosting access is needed to publish; running the local server does not publish the website.
