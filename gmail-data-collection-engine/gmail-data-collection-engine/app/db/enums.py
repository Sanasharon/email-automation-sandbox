from enum import Enum

class AuthMode(str, Enum):
    desktop_oauth = "desktop_oauth"
    web_oauth = "web_oauth"

class SyncStatus(str, Enum):
    connected = "connected"
    syncing = "syncing"
    error = "error"
    disabled = "disabled"

class SyncType(str, Enum):
    full = "full"
    incremental = "incremental"

class SyncRunStatus(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    partial_failure = "partial_failure"
    failed = "failed"

class RecordStatus(str, Enum):
    active = "active"
    archived = "archived"
    deleted = "deleted"

class ProcessingStatus(str, Enum):
    collected = "collected"
    parsed = "parsed"
    completed = "completed"
    failed = "failed"

class AIProcessingStatus(str, Enum):
    not_started = "not_started"
    pending = "pending"
    completed = "completed"
    failed = "failed"

class DownloadStatus(str, Enum):
    pending = "pending"
    downloading = "downloading"
    uploaded = "uploaded"
    failed = "failed"

class LogLevel(str, Enum):
    info = "info"
    warning = "warning"
    error = "error"
    debug = "debug"
