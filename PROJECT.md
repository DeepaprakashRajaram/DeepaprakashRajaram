# GitHub Profile Generator

## Project Purpose
A self-generating GitHub profile that requires zero third-party requests. It uses Python and GitHub Actions to generate an animated ASCII Hero Renderer, contribution stats, and embedded fonts entirely within the repository.

## Architecture
- **Generator**: A collection of Python scripts in `scripts/` driven by a central `config.yaml`.
- **Input Assets**: User-provided images and fonts reside in `assets/input/`.
- **Generated Assets**: Reproducible artifacts are generated into `assets/generated/`.
- **Preview Pipeline**: Changes are first rendered into `preview/` for validation before overwriting live files.
- **Atomic Updates**: Generate → Validate → Preview → Replace.

## Directory Layout
- `assets/input/`: Source images, logos, and fonts.
- `assets/generated/`: Reproducible SVGs and ASCII files.
- `preview/`: Staging area for `README.md` and final assets before replacing live versions.
- `scripts/`: Generator scripts.
- `.backup/`: Stores the original state of user files to enable 100% rollback.
- `.github/workflows/`: Automation pipelines.

## Rollback Philosophy
The project is 100% reversible. A dedicated `rollback.py` script reads the project manifest and can completely restore the repository to its prior state by deleting generated files, restoring backups, and removing the project configuration.
