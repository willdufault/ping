"""Status of a service in a region. Values are the capitalized strings stored
in DynamoDB, so get_service_statuses returns them unchanged."""

from enum import StrEnum


class Status(StrEnum):
    HEALTHY = "Healthy"
    DEGRADED = "Degraded"
    OUTAGE = "Outage"
    UNKNOWN = "Unknown"