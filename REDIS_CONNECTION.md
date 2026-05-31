# Redis Connection Configuration

## Problem

When running `mic2e-agent` locally and connecting to remote Redis, you need to configure the Redis connection.

## Solution

Set the `REDIS_HOST` and `REDIS_PORT` environment variables to point to the remote Redis instance.

### Option 1: Separate Variables (Recommended)

```bash
export REDIS_HOST="192.168.20.245"
export REDIS_PORT="6379"
```

Or create a `.env` file in `mic2e-agent/`:
```
REDIS_HOST=192.168.20.245
REDIS_PORT=6379
```

### Option 2: Combined Format (Backward Compatible)

```bash
export REDIS_HOST="192.168.20.245:6379"
```

## Port Information

From your `docker ps` output:
- Redis container port: `6379` (internal)
- Redis host mapping: `0.0.0.0:6379->6379/tcp` (exposed on port 6379)

**Important**: When connecting from your local machine to the remote host, use port `6379` (the actual Redis port), not `3379` (which is only used in local docker-compose for port mapping).

## Connection Test

After setting the environment variables, the service will log:
```
Connecting to Redis at 192.168.20.245:6379
```

If you see connection errors, verify:
1. Redis is running on the remote host: `docker ps | grep redis`
2. Network connectivity: `telnet 192.168.20.245 6379`
3. Firewall allows connections on port 6379

## Comparison with Other Services

| Service | Database | Connection Pattern |
|---------|----------|-------------------|
| `mic2e-web` | Postgres | `postgresql://user:pass@192.168.20.245:5432/mic2e` |
| `mic2e-storage` | MongoDB | `mongodb://192.168.20.245:27017/mic2e` |
| `mic2e-agent` | Redis | `REDIS_HOST=192.168.20.245` + `REDIS_PORT=6379` |

All services connect directly to the remote host using the actual database ports (not the mapped ports from docker-compose).

