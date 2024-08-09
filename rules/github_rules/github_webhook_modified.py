from global_filter_github import filter_include_event
from panther_base_helpers import deep_get, github_alert_context


def rule(event):
    if not filter_include_event(event):
        return False
    return event.get("action").startswith("hook.")


def title(event):
    repo = event.get("repo", "<UNKNOWN_REPO>")
    action = "modified"
    if event.get("action").endswith("destroy"):
        action = "deleted"
    elif event.get("action").endswith("create"):
        action = "created"

    # In Audit logs only type:repo webhooks are obvious, Org and App look the same.
    # GETs to /orgs/{org}/hooks or /repos/{owner}/{repo}/hooks will return type
    # App hooks don't return type and are defined by their API endpoint
    title_str = (
        f"Github webhook [{deep_get(event,'config','url',default='<UNKNOWN_URL>')}]"
        f" {action} by [{event.get('actor','<UNKNOWN_ACTOR>')}]"
    )
    if repo != "<UNKNOWN_REPO>":
        title_str += f" in repository [{repo}]"
    return title_str


def severity(event):
    if event.get("action").endswith("create"):
        return "MEDIUM"
    return "INFO"


def alert_context(event):
    ctx = github_alert_context(event)
    ctx["business"] = event.get("business", "")
    ctx["hook_id"] = event.get("hook_id", "")
    ctx["integration"] = event.get("integration", "")
    ctx["operation_type"] = event.get("operation_type", "")
    ctx["url"] = deep_get(event, "config", "url", default="<UNKNOWN_URL>")
    return ctx
