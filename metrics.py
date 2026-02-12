import os

from prometheus_client import Counter, Gauge, Histogram


SERVICE_NAME = "store-api"
SERVICE_VERSION = "v1"

REQUEST_DURATION_BUCKETS = (
    0.005,
    0.01,
    0.025,
    0.05,
    0.1,
    0.25,
    0.5,
    1.0,
    2.5,
    5.0,
)

SERVICE_INFO = Gauge(
    "service_info",
    "Static service metadata.",
    ["service", "version"],
)

HTTP_REQUESTS_IN_FLIGHT = Gauge(
    "http_requests_in_flight",
    "Current number of in-flight HTTP requests.",
    ["service", "method", "route"],
)

HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total number of HTTP requests.",
    ["service", "method", "route", "status_code"],
)

HTTP_REQUESTS_ERRORS_TOTAL = Counter(
    "http_requests_errors_total",
    "Total number of error HTTP requests (4xx, 5xx).",
    ["service", "method", "route", "status_code"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds.",
    ["service", "method", "route"],
    buckets=REQUEST_DURATION_BUCKETS,
)

STORES_CREATED_TOTAL = Counter(
    "stores_created_total",
    "Total number of stores created.",
    ["service"],
)

ITEMS_CREATED_TOTAL = Counter(
    "items_created_total",
    "Total number of items created.",
    ["service"],
)

TAGS_CREATED_TOTAL = Counter(
    "tags_created_total",
    "Total number of tags created.",
    ["service"],
)

STORE_SEARCH_TOTAL = Counter(
    "store_search_total",
    "Total number of store search requests.",
    ["service"],
)

STORE_ITEM_LINK_TOTAL = Counter(
    "store_item_link_total",
    "Total number of store-item link operations.",
    ["service"],
)

STORE_ITEM_UNLINK_TOTAL = Counter(
    "store_item_unlink_total",
    "Total number of store-item unlink operations.",
    ["service"],
)

ITEM_TAG_LINK_TOTAL = Counter(
    "item_tag_link_total",
    "Total number of item-tag link operations.",
    ["service"],
)

ITEM_TAG_UNLINK_TOTAL = Counter(
    "item_tag_unlink_total",
    "Total number of item-tag unlink operations.",
    ["service"],
)

USERS_REGISTERED_TOTAL = Counter(
    "users_registered_total",
    "Total number of registered users.",
    ["service"],
)

USER_LOGIN_TOTAL = Counter(
    "user_login_total",
    "Total number of successful user logins.",
    ["service"],
)

TOKEN_REFRESH_TOTAL = Counter(
    "token_refresh_total",
    "Total number of successful token refreshes.",
    ["service"],
)

LOGOUT_TOTAL = Counter(
    "logout_total",
    "Total number of successful user logouts.",
    ["service"],
)


def configure_service_metrics():
    global SERVICE_NAME
    global SERVICE_VERSION

    SERVICE_NAME = os.getenv("SERVICE_NAME", SERVICE_NAME)
    SERVICE_VERSION = os.getenv("SERVICE_VERSION", SERVICE_VERSION)
    SERVICE_INFO.labels(service=SERVICE_NAME, version=SERVICE_VERSION).set(1)


def service_name():
    return SERVICE_NAME
