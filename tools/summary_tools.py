"""Summary helpers for completed workflow runs."""


def generate_project_summary(request, files, test_results, review_output, documentation):
    parts = [
        f"Request: {request}",
        f"Generated files: {', '.join(sorted((files or {}).keys())) or 'none'}",
    ]
    if test_results:
        parts.append(f"Test status: {test_results.get('status', 'unknown')}")
    if review_output:
        parts.append("Code review completed.")
    if documentation:
        parts.append("Documentation generated.")
    return "\n".join(parts)
