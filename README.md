# Bambooshi

Digital menu for [Bambooshi](https://bambooshi.ttmenus.com/) — Chaguanas.

## Structure

Project content and theme content are merged via Hugo module mounts: site `content/` is mounted first, then `themes/_menus_ttms/content` (dashboard, locations, api, etc.).

```
├── content/            # Menu sections and items
├── data/               # locations.yaml, mappin.yaml
├── static/             # Branding, CSS, manifest, _headers, _redirects
├── themes/_menus_ttms/ # Hugo theme (git submodule)
├── hugo.toml           # Site configuration
├── netlify.toml        # Netlify deployment
└── build_menu.sh       # Build script
```

## Local Development

```bash
git submodule update --init --recursive
hugo server -D
```

## Building

```bash
./build_menu.sh
```

Build output goes to `public/`. The theme submodule is pinned for Netlify/CI; local builds may refresh it to latest `master` when `NETLIFY` and `CI` are unset.
