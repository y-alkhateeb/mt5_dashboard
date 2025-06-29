# Trading Robot Admin System

## Overview

The Trading Robot Admin system is a Django-based web application designed to manage trading robot licenses, client information, and trading configurations for MT5 (MetaTrader 5) trading robots. The system provides both a web interface for administrators and a REST API for trading robot validation and configuration management.

## Project Structure

```
trading_admin/
├── core/                     # Core application (dashboard, health checks)
├── licenses/                 # License and client management
├── configurations/           # Trading configuration management
├── trading_admin/           # Main Django project settings
├── templates/               # HTML templates
├── static/                  # Static files (CSS, JS, images)
├── requirements.txt         # Python dependencies
├── manage.py               # Django management script
└── railway.json            # Railway deployment configuration
```

## Core Applications

### 1. Core App (`core/`)
- **Purpose**: Dashboard views, API documentation, health checks
- **Key Files**:
  - `views.py`: Dashboard view with license statistics
  - `api_views.py`: API documentation and health check endpoints
  - `urls.py`: URL routing for dashboard and API docs

### 2. Licenses App (`licenses/`)
- **Purpose**: Manages trading licenses and client information
- **Key Models**:
  - `Client`: Client information (name, country, email, phone)
  - `License`: Trading licenses with system binding and usage tracking
- **Key Features**:
  - License validation for trading robots
  - System hash binding (primary account identifier)
  - Account hash tracking (login change monitoring)
  - Usage statistics and expiration management

### 3. Configurations App (`configurations/`)
- **Purpose**: Manages trading robot configurations (Fibonacci levels, timeouts, etc.)
- **Key Model**:
  - `TradingConfiguration`: MT5-specific trading parameters
- **Key Features**:
  - Fibonacci level configuration
  - Session timing settings
  - Timeout configurations for different order types
  - Symbol validation settings

## API Documentation

### Base URL
- **Local Development**: `http://localhost:8000/api/`
- **Production**: `https://your-domain.railway.app/api/`

### Authentication
- **Method**: Session Authentication or Basic Authentication
- **Required**: For all admin endpoints
- **Exception**: Bot validation endpoint is public

## API Endpoints

### 1. Bot Validation API (Public)

#### Validate Trading Robot License
- **Endpoint**: `POST /api/validate/`
- **Purpose**: Validates trading robot license and returns configuration
- **Authentication**: None required
- **Content-Type**: `application/json`

**Request Body**:
```json
{
  "license_key": "e1f1016bdf764b8b82ede144a5ccd978",
  "system_hash": "unique_trading_account_identifier_hash",
  "account_trade_mode": 0,
  "broker_server": "broker.example.com",
  "account_hash": "optional_account_login_hash",
  "timestamp": "2025-06-29T10:00:00Z"
}
```

**Request Parameters**:
- `license_key` (string, required): 32-character license key
- `system_hash` (string, required): Primary trading account identifier
- `account_trade_mode` (integer, required): 0=Demo, 1=Restricted, 2=Live
- `broker_server` (string, optional): Broker server address
- `account_hash` (string, optional): Account login hash for tracking
- `timestamp` (datetime, required): Request timestamp

**Success Response** (200):
```json
{
  "success": true,
  "message": "License validated successfully",
  "configuration": {
    "inp_AllowedSymbol": "US30",
    "inp_StrictSymbolCheck": true,
    "inp_SessionStart": "08:45",
    "inp_SessionEnd": "10:00",
    "inp_FibLevel_1_1": 1.325,
    "inp_FibLevel_1_05": 1.05,
    "inp_FibLevel_1_0": 1.0,
    "inp_FibLevel_PrimaryBuySL": -0.05,
    "inp_FibLevel_PrimarySellSL": 1.05,
    "inp_FibLevel_HedgeBuy": 1.05,
    "inp_FibLevel_HedgeSell": -0.05,
    "inp_FibLevel_HedgeBuySL": 0.0,
    "inp_FibLevel_HedgeSellSL": 1.0,
    "inp_FibLevel_0_0": 0.0,
    "inp_FibLevel_Neg_05": -0.05,
    "inp_FibLevel_Neg_1": -0.325,
    "inp_FibLevel_HedgeBuyTP": 1.3,
    "inp_FibLevel_HedgeSellTP": -0.3,
    "inp_PrimaryPendingTimeout": 30,
    "inp_PrimaryPositionTimeout": 60,
    "inp_HedgingPendingTimeout": 30,
    "inp_HedgingPositionTimeout": 60
  },
  "expires_at": "2026-06-21T04:15:23.549Z"
}
```

**Error Response** (400/401):
```json
{
  "success": false,
  "message": "Invalid license key"
}
```

### 2. Admin API Endpoints (Authenticated)

#### License Management

##### List All Licenses
- **Endpoint**: `GET /api/admin/licenses/`
- **Purpose**: Get paginated list of all licenses
- **Authentication**: Required

**Response**:
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "license_key": "e1f1016bdf764b8b82ede144a5ccd978",
      "client": {
        "id": 1,
        "first_name": "John",
        "last_name": "Smith",
        "country": "United States",
        "email": "john@example.com",
        "full_name": "John Smith"
      },
      "system_hash": null,
      "account_hash": null,
      "account_trade_mode": 0,
      "broker_server": null,
      "expires_at": "2026-06-21T04:15:23.549Z",
      "is_active": true,
      "status": "Not Bound",
      "is_expired": false,
      "is_valid": true,
      "is_account_bound": false,
      "has_login_info": false,
      "account_hash_changes_count": 0,
      "usage_count": 0,
      "created_at": "2025-06-21T04:15:23.553Z"
    }
  ]
}
```

##### Create New License
- **Endpoint**: `POST /api/admin/licenses/`
- **Purpose**: Create a new trading license

**Request Body**:
```json
{
  "client": 1,
  "account_trade_mode": 0,
  "expires_at": "2026-06-21T10:00:00Z",
  "is_active": true
}
```

##### Get License Details
- **Endpoint**: `GET /api/admin/licenses/{id}/`
- **Purpose**: Get detailed information about a specific license

##### Update License
- **Endpoint**: `PUT /api/admin/licenses/{id}/`
- **Purpose**: Update license information

##### Get Active Licenses
- **Endpoint**: `GET /api/admin/licenses/active/`
- **Purpose**: Get all active licenses

##### Get Expired Licenses
- **Endpoint**: `GET /api/admin/licenses/expired/`
- **Purpose**: Get all expired licenses

##### License Configuration Management
- **Endpoint**: `GET /api/admin/licenses/{id}/configuration/`
- **Purpose**: Get trading configuration for specific license

- **Endpoint**: `PUT /api/admin/licenses/{id}/configuration/`
- **Purpose**: Update trading configuration for specific license

#### Client Management

##### List All Clients
- **Endpoint**: `GET /api/admin/clients/`
- **Purpose**: Get paginated list of all clients

**Response**:
```json
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "first_name": "John",
      "last_name": "Smith",
      "country": "United States",
      "email": "john@example.com",
      "phone": null,
      "full_name": "John Smith"
    }
  ]
}
```

##### Create New Client
- **Endpoint**: `POST /api/admin/clients/`
- **Purpose**: Create a new client

**Request Body**:
```json
{
  "first_name": "Jane",
  "last_name": "Doe",
  "country": "Canada",
  "email": "jane@example.com",
  "phone": "+1-555-0123"
}
```

#### Configuration Management

##### List All Configurations
- **Endpoint**: `GET /api/configurations/`
- **Purpose**: Get all trading configurations
- **Query Parameters**: 
  - `license_id`: Filter by license ID

##### Create New Configuration
- **Endpoint**: `POST /api/configurations/`
- **Purpose**: Create a new trading configuration

##### Update Configuration
- **Endpoint**: `PUT /api/configurations/{id}/`
- **Purpose**: Update trading configuration

### 3. System Endpoints

#### API Documentation
- **Endpoint**: `GET /api/docs/`
- **Purpose**: Get API documentation and endpoint information
- **Authentication**: Required

#### Health Check
- **Endpoint**: `GET /api/health/`
- **Purpose**: System health monitoring
- **Authentication**: Required

**Response**:
```json
{
  "status": "healthy",
  "database": "connected",
  "total_licenses": 5,
  "timestamp": "2025-06-29T10:00:00Z"
}
```

## Data Models

### License Model
- **Primary Identifier**: `system_hash` (trading account identifier)
- **Secondary Tracking**: `account_hash` (login change tracking)
- **Key Features**:
  - Automatic license key generation
  - System binding on first use
  - Account hash history tracking
  - Usage statistics
  - Expiration management

### Client Model
- **Purpose**: Store client information
- **Unique Constraint**: `(first_name, last_name, country)`
- **Key Fields**: Name, country, email, phone

### TradingConfiguration Model
- **Purpose**: Store MT5 trading parameters
- **Key Features**:
  - Fibonacci level configuration
  - Session timing settings
  - Timeout configurations
  - Symbol validation

## Security Features

### License Validation Security
1. **System Hash Binding**: Each license binds to a unique trading account
2. **Account Mode Validation**: Ensures consistent trading mode
3. **Expiration Checking**: Automatic expiration validation
4. **Usage Tracking**: Monitors license usage patterns

### Account Tracking
1. **Primary Binding**: `system_hash` locks license to specific trading account
2. **Login Monitoring**: `account_hash` tracks account login changes
3. **History Tracking**: Complete history of account hash changes
4. **Change Detection**: Automatic detection of account login changes

## Configuration Parameters

### Fibonacci Levels
- **inp_FibLevel_1_1**: Fibonacci Level 1.1 (default: 1.325)
- **inp_FibLevel_1_05**: Buy Entry Level (default: 1.05)
- **inp_FibLevel_1_0**: Session High (default: 1.0)
- **inp_FibLevel_0_0**: Session Low (default: 0.0)
- **inp_FibLevel_Neg_05**: Sell Entry Level (default: -0.05)
- **inp_FibLevel_Neg_1**: Sell TP Level (default: -0.325)

### Stop Loss & Take Profit
- **inp_FibLevel_PrimaryBuySL**: Primary Buy Stop Loss
- **inp_FibLevel_PrimarySellSL**: Primary Sell Stop Loss
- **inp_FibLevel_HedgeBuySL**: Hedging Buy Stop Loss
- **inp_FibLevel_HedgeSellSL**: Hedging Sell Stop Loss
- **inp_FibLevel_HedgeBuyTP**: Hedging Buy Take Profit
- **inp_FibLevel_HedgeSellTP**: Hedging Sell Take Profit

### Trading Sessions
- **inp_SessionStart**: Session start time (HH:MM format)
- **inp_SessionEnd**: Session end time (HH:MM format)

### Timeouts (Minutes)
- **inp_PrimaryPendingTimeout**: Primary order timeout
- **inp_PrimaryPositionTimeout**: Primary position timeout
- **inp_HedgingPendingTimeout**: Hedging order timeout
- **inp_HedgingPositionTimeout**: Hedging position timeout

### Symbol Settings
- **inp_AllowedSymbol**: Allowed trading symbol
- **inp_StrictSymbolCheck**: Enable strict symbol validation

## Error Handling

### Common Error Codes
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error

### License Validation Errors
- "Invalid license key": License not found
- "License is expired": License past expiration date
- "License is inactive": License deactivated
- "Account not authorized": System hash mismatch
- "Account trade mode mismatch": Mode doesn't match license
- "No trading configuration assigned": Missing configuration

## Deployment Information

### Railway Deployment
- **Platform**: Railway.app
- **Database**: PostgreSQL
- **Web Server**: Gunicorn
- **Static Files**: WhiteNoise
- **Configuration**: `railway.json`

### Environment Variables
- `SECRET_KEY`: Django secret key
- `DEBUG`: Debug mode (False in production)
- `ALLOWED_HOSTS`: Allowed hostnames
- `DATABASE_URL`: PostgreSQL connection string

### Management Commands
- `python manage.py migrate`: Run database migrations
- `python manage.py collectstatic`: Collect static files
- `python manage.py createsuperuser`: Create admin user
- `python manage.py create_sample_data`: Create sample data
- `python manage.py cleanup_expired`: Clean up expired licenses
- `python manage.py generate_report`: Generate usage reports

## Web Interface

### Admin Panel
- **URL**: `/admin/`
- **Features**: Complete CRUD operations for all models
- **Authentication**: Django admin authentication

### Dashboard
- **URL**: `/dashboard/`
- **Features**: License statistics, charts, recent licenses
- **Authentication**: Login required

## API Rate Limiting

Currently, no rate limiting is implemented. For production use, consider implementing:
- Rate limiting for bot validation endpoint
- Request throttling for admin endpoints
- IP-based restrictions for sensitive operations

## Future Enhancements

### Planned Features
1. Real-time license usage monitoring
2. Advanced reporting and analytics
3. Multi-tenant support
4. API rate limiting
5. License usage alerts
6. Advanced permission system

### Scalability Considerations
1. Caching layer for frequent validation requests
2. Load balancing for high-traffic scenarios