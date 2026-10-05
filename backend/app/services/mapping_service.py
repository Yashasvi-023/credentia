def map_template_fields(
    placeholders: list[str],
    columns: list[str]
) -> dict:

    column_set = set(columns)
    placeholder_set = set(placeholders)

    mapped = []
    missing = []
    unused_columns = []

    for placeholder in placeholders:

        if placeholder in column_set:
            mapped.append(placeholder)
        else:
            missing.append(placeholder)

    for column in columns:

        if column not in placeholder_set:
            unused_columns.append(column)

    return {
        "mapped": mapped,
        "missing": missing,
        "unused_columns": unused_columns
    }