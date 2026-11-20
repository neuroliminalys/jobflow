FRANCE_TRAVAIL_URL="https://api.francetravail.io/partenaire/rome-competences/v1/competences/competence"
FRANCE_TRAVAIL_SECRET="60b8160cec96e3212dcf4133279814bb71d4be017e8ad8b0c875e03497343d7a"
# Optional when FRANCE_TRAVAIL_SECRET is an OAuth client secret.
FRANCE_TRAVAIL_CLIENT_ID="PAR_iajumphackathonsimplo_e498b089faba736b6d06c12ff7bd9319994aeec18048274393b66263c92ded34"


For every skill:
1. Query the France Travail ROME 4.0 skills catalog.
2. Select the closest official skill.
3. Never invent an identifier.
4. Exclude skills that cannot be matched confidently.