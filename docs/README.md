# tachi Documentation

This directory contains the Docusaurus-based documentation site for tachi.

## Structure

```
docs/
├── tachi-site/          # Docusaurus site
│   ├── docs/           # Documentation pages
│   ├── src/            # React components and styles
│   └── static/         # Static assets
└── build-docs.sh       # Build script
```

## Local Development

1. Navigate to the docs site:
   ```bash
   cd tachi-site
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start development server:
   ```bash
   npm start
   ```

4. View at http://localhost:3000

**Note**: The site is configured in docs-only mode. The documentation is served at the root path.

## Building

Use the build script:
```bash
./build-docs.sh
```

Or manually:
```bash
cd tachi-site
npm run build
```

## Documentation Pages

- **intro.md** - Introduction and overview
- **quickstart.md** - Getting started guide
- **configuration.md** - Configuration reference
- **deployment-strategies.md** - Strategy explanations
- **examples.md** - Real-world examples
- **developer-guide.md** - Contributing guide
- **commands.md** - CLI command reference
- **troubleshooting.md** - Common issues and solutions

## Deployment

The site can be deployed to GitHub Pages:

```bash
cd tachi-site
npm run deploy
```

This requires:
- `organizationName` and `projectName` in `docusaurus.config.ts`
- Write access to the repository
- GitHub Pages enabled for the repository

## Customization

- **Colors**: Edit `src/css/custom.css`
- **Navigation**: Edit `docusaurus.config.ts`
- **Homepage**: Edit `src/pages/index.tsx`
- **Features**: Edit `src/components/HomepageFeatures/index.tsx`

## Contributing

When adding new documentation:

1. Create markdown file in `docs/`
2. Add frontmatter with `sidebar_position`
3. Use clear headings and examples
4. Test locally before committing
5. Ensure all links work