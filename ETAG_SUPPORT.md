# ETag Support for Optimistic Concurrency Control

The Twilio Python SDK now supports accessing ETag headers from API responses, enabling optimistic concurrency control to prevent update conflicts.

## Overview

ETags (Entity Tags) are HTTP headers that represent a specific version of a resource. When combined with conditional request headers like `If-Match`, they allow you to ensure that updates only succeed if the resource hasn't changed since you last retrieved it.

## Accessing ETags

### Instance Resources

All `InstanceResource` objects now have an `etag` property that returns the ETag header value from the most recent API response:

```python
from twilio.rest import Client

client = Client()

# Fetch a resource - ETag is automatically captured
config = client.messaging.v1.domain_configs('DM123').fetch()

# Access the ETag
etag = config.etag  # Returns the ETag value, e.g., '"W/abc123"'

if etag:
    print(f"Resource ETag: {etag}")
else:
    print("No ETag available for this resource")
```

### Page Resources

Paginated responses also preserve headers, including ETags:

```python
# Get a page of resources
page = client.messaging.v1.domain_configs.list().next_page()

# Access page-level headers
page_etag = page.headers.get('ETag')
total_count = page.headers.get('X-Total-Count')
```

## Optimistic Concurrency Control

Use ETags with the `if_match` parameter (available on supported resources) to implement optimistic concurrency control:

```python
# Step 1: Fetch the current resource and its ETag
task = client.taskrouter.workspaces('WS123').tasks('TK456').fetch()
current_etag = task.etag

# Step 2: Perform conditional update using the ETag
# This will only succeed if the resource hasn't changed
try:
    updated_task = task.update(
        if_match=current_etag,
        assignment_status='completed',
        reason='Customer request completed'
    )
    print(f"Update successful! New ETag: {updated_task.etag}")
    
except TwilioRestException as e:
    if e.status == 412:  # Precondition Failed
        print("Update failed: Resource was modified by another process")
        # Fetch latest version and retry if needed
    else:
        raise
```

## Supported Operations

ETag headers are captured for the following operations:

- **fetch()** - Individual resource retrieval
- **update()** - Resource modifications  
- **create()** - Resource creation
- **list()** - Paginated resource listing (page-level headers)

## Services with if_match Support

The following Twilio services currently support the `if_match` parameter for conditional updates:

- **TaskRouter Tasks** - Prevent task assignment conflicts
- **Conversations** - Avoid message update conflicts
- *(Other services that support conditional requests)*

## Backward Compatibility

This feature is fully backward compatible:

- Existing code continues to work unchanged
- The `etag` property returns `None` if no ETag is available
- All existing methods maintain their original signatures
- No performance impact on existing functionality

## Error Handling

When using conditional requests, handle these specific scenarios:

```python
from twilio.base.exceptions import TwilioRestException

try:
    result = resource.update(if_match=etag, ...)
except TwilioRestException as e:
    if e.status == 412:
        # Precondition Failed - resource was modified
        print("Resource changed, please fetch latest version")
    elif e.status == 428:
        # Precondition Required - if_match is required but not provided
        print("This operation requires an ETag for safety")
    else:
        # Other error
        raise
```

## Best Practices

1. **Always check for ETag availability** before using conditional requests
2. **Handle 412 Precondition Failed** errors gracefully by refetching and retrying
3. **Use ETags for critical updates** where data consistency is important
4. **Cache ETags** when you need to perform multiple operations on the same resource

## Implementation Notes

- ETags are case-insensitive (handles both "ETag" and "etag" headers)
- The `etag` property returns the raw header value including quotes
- Headers are preserved in both sync and async operations
- Page-level headers are accessible via the `headers` property on Page objects