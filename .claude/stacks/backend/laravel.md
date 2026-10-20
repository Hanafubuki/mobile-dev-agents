# Backend stack guide: Laravel (PHP)

Read by `be-architect`, `be-planner`, `be-developer`, `be-tester` and `be-reviewer` when the
Project profile in `CLAUDE.md` names this guide. It maps the generic DDD rules in the skills to
Laravel.

## Layout

Paths are relative to the backend folder in the profile.

```
app/
  Domain/<Context>/
    Entities/          Aggregates and entities (plain PHP, invariants enforced in methods)
    ValueObjects/      Immutable, self-validating (Email, Money, UserId…)
    Repositories/      Interfaces only (e.g. OrderRepository)
    Events/            Domain events (OrderPlaced)
    Services/          Domain services for logic that spans aggregates
    Exceptions/        Domain exceptions with meaningful names
  Application/<Context>/
    Actions/           One use case per class, single public handle()/__invoke()
    DTOs/              final readonly input/output data objects
    Queries/           Read-side query objects when reads are non-trivial
  Infrastructure/<Context>/
    Persistence/       Eloquent models + repository implementations + mappers
    Providers/         Binds Domain interfaces to Infrastructure implementations
    External/          Adapters to third-party services (behind Domain/Application interfaces)
  Http/
    Controllers/Api/V1/   Thin: FormRequest → DTO → Action → Resource
    Requests/             Validation + toDto()
    Resources/            API output shape
routes/api.php            Versioned (/api/v1/…)
database/migrations/
tests/Unit/Domain/…  tests/Unit/Application/…  tests/Feature/Api/…
```

## Idioms

- `declare(strict_types=1);` in every PHP file. Typed properties, parameters and returns.
  `final` classes by default.
- DTOs are `final readonly class` with typed promoted properties and named constructors
  (`fromRequest`, `fromModel`).
- Controllers: FormRequest validates → `$request->toDto()` → Action → API Resource.
- Domain: no facades, no Eloquent, no `request()`/`auth()` helpers.
- Repositories: Eloquent implementation bound to the Domain interface in a service provider.
- Domain exceptions mapped to HTTP responses in the exception handler (`bootstrap/app.php`
  `withExceptions` on Laravel 11+, `app/Exceptions/Handler.php` before).
- Authorisation through Policies/Gates; validation through FormRequests; config via
  `config()`, never `env()` outside config files.
- Auth: Sanctum unless the project already uses something else.
- Eager load to avoid N+1; paginate lists with API Resource collections.
- Style: PSR-12 via Laravel Pint.

## Testing

- Pest if the repo uses it, otherwise PHPUnit.
- Feature tests use `RefreshDatabase` or `LazilyRefreshDatabase`.
- Assert response shapes with `assertJsonStructure` / `assertExactJson`.
- Factories for every Eloquent model a test needs.

## Default commands

```
php artisan test --filter=<Name>   # tests for one slice
php artisan test                   # full suite (or vendor/bin/pest)
vendor/bin/pint --test             # format check
vendor/bin/phpstan analyse         # Larastan, if configured
php artisan serve                  # run locally
```

## Review checklist additions

- `strict_types` in every file, `final` by default, Pint and PHPStan clean.
- No Eloquent model, facade or helper used inside `app/Domain`.
- API Resources produce exactly the contract's shape; routes under `/api/v1`.
- `$fillable`/`$guarded` set so mass assignment is safe.
- Migrations have a working `down()`.
