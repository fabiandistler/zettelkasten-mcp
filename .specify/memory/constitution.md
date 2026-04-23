# Zettelkasten MCP Constitution

## Core Principles

### I. Atomic Notes
Every note MUST contain exactly one discrete idea. Notes are the fundamental unit of knowledge in the Zettelkasten system. This constraint ensures reusability, linkability, and clarity of purpose. Notes that contain multiple ideas MUST be split into separate atomic notes and linked together.

### II. Bidirectional Linking
Every meaningful relationship between notes MUST be represented as a link on both notes (symmetric relationship). This ensures the knowledge graph is navigable in both directions and maintains referential integrity. Orphan notes with no links are discouraged unless intentionally created as fleeting notes.

### III. Semantic Link Types
Links MUST use semantic types that express the nature of the relationship. Link types are not interchangeable: `reference`, `extends`, `refines`, `contradicts`, `questions`, `supports`, and `related` each have distinct meaning. Choosing the correct link type is required for maintaining knowledge quality.

### IV. Dual Storage Architecture
Notes MUST be stored in Markdown format as the source of truth. Markdown files MUST remain human-readable, editable outside the system, and version-controllable. SQLite serves as an indexing layer only and MAY be rebuilt from Markdown files at any time. Data loss prevention: the Markdown source MUST always be preserved.

### V. MCP Protocol Compliance
All tools MUST follow the MCP protocol specification. Tool names MUST use the `zk_` prefix for organization. Tools MUST support both JSON and human-readable output formats where applicable. Error messages MUST be informative and actionable.

## Technology Constraints

### Required Stack
- **Language**: Python 3.11+
- **MCP SDK**: Python MCP SDK (`mcp[cli]`)
- **Storage**: SQLite for indexing; Markdown files for persistence
- **Testing**: pytest with coverage reporting
- **Package Manager**: uv

### Data Integrity
- The Markdown source file is always the source of truth
- SQLite index MUST be rebuildable from Markdown files at any time
- No operation that would cause data loss is acceptable
- Manual edits to Markdown files MUST be recoverable via rebuild

## Development Workflow

### Code Quality Gates
- All new functionality MUST have corresponding tests
- Tests MUST pass before merging
- Code coverage MUST be maintained or improved
- Type hints MUST be used throughout
- Docstrings REQUIRED for public APIs

### Test Organization
- Unit tests for models and services
- Integration tests for MCP server tools
- Contract tests for data storage layer
- All tests in `tests/` directory

## Governance

### Amendment Procedure
1. Proposals for constitution changes MUST be documented in a spec
2. Changes MUST be reviewed and approved before ratification
3. Backward-incompatible changes increment MAJOR version
4. Additive changes increment MINOR version
5. Clarifications increment PATCH version

### Compliance Verification
- All pull requests and reviews MUST verify constitution compliance
- Complexity that violates principles MUST be justified
- Deviations from principles MUST be documented with rationale

**Version**: 1.0.0 | **Ratified**: TODO(initial): Not yet ratified - this is the initial constitution | **Last Amended**: 2026-04-23