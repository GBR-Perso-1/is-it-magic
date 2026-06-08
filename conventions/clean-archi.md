# Clean Architecture (.NET) — Conventions

> How a clean-architecture .NET codebase is organised, so changes land in the right place.
> Guidance for planning and implementation — not enforced line-rules.

## Layers (dependencies point inward only: API → Application → Domain)

- **Domain** — entities, value objects, domain events. No dependencies.
- **Application** — commands, queries (CQRS), validators, interfaces. Depends on Domain only.
- **Infrastructure** — persistence (EF Core), external services, repositories. Implements Application interfaces.
- **API** — thin controllers (delegate to the mediator; no business logic), DTOs, middleware. Depends on Application.

Infrastructure is never referenced by Application or Domain.

## Where things go

- New entity → `Domain/Entities/`
- New command/query → `Application/Features/{Entity}/`
- New validator → alongside its command in `Application/Features/{Entity}/`
- New endpoint → `API/Controllers/{Entity}Controller.cs`
- New persistence config → `Infrastructure/Persistence/Configurations/{Entity}Configuration.cs`

## Naming

- Commands `{Verb}{Entity}Command`; Queries `Get{Entity}Query` / `List{Entities}Query`
- Handlers `{Command/Query}Handler`; Validators `{Command/Query}Validator`
- Repositories `I{Entity}Repository` (interface) / `{Entity}Repository` (impl)

## Handler conventions

- Query/Command + its Handler live in the same file — never split.
- Controllers stay thin — delegate to the mediator.
- Query → DTO projection inside the query (single SQL round-trip). Load-then-map only for a polymorphic hierarchy where a shared projection would force formula duplication.
- Extract shared logic into services — no cross-handler duplication.
