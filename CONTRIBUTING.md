# Contributing to QR File Transfer

**Owner**: Development Team  
**Review trigger**: Before each release, or when development workflow changes

---

## Development Setup

### Prerequisites

- Python 3.9+
- macOS: `brew install zbar`
- Linux: `sudo apt-get install libzbar0`
- Windows: no additional system deps

### Install

```bash
git clone git@github.com:jibeex/qr-file-transfer.git
cd qr-file-transfer
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### Run tests

```bash
pytest                          # all tests
pytest tests/unit               # unit only
pytest --cov=qr_transfer        # with coverage
```

---

## Code Standards

- **Style**: PEP 8, enforced via `flake8` (see `requirements.txt`)
- **Types**: Type hints on all public functions
- **Docstrings**: Google-style, required on public API
- **Error handling**: Use the exception hierarchy in `errors.py`; never catch bare `Exception`

---

## Documentation Standards

### WHAT vs HOW separation

| Document | Contains | Does NOT contain |
|---|---|---|
| `docs/REQUIREMENTS.md` | User requirements, acceptance criteria, constraints | Library names, algorithms, data structures |
| `docs/DESIGN.md` | Architecture, component design, algorithms, tech choices | Business requirements, user stories |
| `docs/adr/` | One decision per file, immutable once accepted | Multiple decisions in one file |
| `docs/specs/` | Stable reference specs (wire format, CLI contract) | Rationale, alternatives |

**The test**: "Does this describe WHAT or HOW?"  
- WHAT → `REQUIREMENTS.md`  
- HOW → `DESIGN.md` or `docs/adr/`

### When to write an ADR

Write a new ADR in `docs/adr/` when:
- Choosing between competing technologies or approaches
- Making a decision that is hard to reverse
- Selecting a default that affects performance or compatibility

ADR format: see `docs/adr/001-default-grid-size.md` as a template.

### Enforcement check

```bash
# Verify no implementation details leaked into requirements
grep -i "sha-256\|h\.264\|mp4\|gzip\|crc32\|opencv\|pyzbar\|class\|module" docs/REQUIREMENTS.md
```

---

## Pull Request Process

1. Branch from `main`: `git checkout -b feature/your-feature`
2. Write tests first (TDD preferred)
3. Ensure all tests pass and coverage stays ≥ 80%
4. Update relevant docs (ADR if a design decision was made, DESIGN.md if architecture changed)
5. Open PR with a description covering: what, why, testing done

---

## Commit Messages

```
type(scope): short summary (≤72 chars)

Body: why, not what. Reference issue numbers.
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `chore`

---

## Release Checklist

- [ ] All tests pass
- [ ] CHANGELOG.md updated under `[Unreleased]`
- [ ] Version bumped in `src/qr_transfer/__init__.py` and `requirements.txt`
- [ ] ADRs up to date
- [ ] DESIGN.md reflects current implementation
