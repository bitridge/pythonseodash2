# API Documentation

## Authentication

All API endpoints require authentication using JWT tokens. Include the token in the Authorization header:
```
Authorization: Bearer <token>
```

## Endpoints

### Customer Management

#### List Customers
```
GET /api/customers/
```
Returns a list of customers the authenticated user has access to.

#### Get Customer Details
```
GET /api/customers/{id}/
```
Returns detailed information about a specific customer.

#### Create Customer
```
POST /api/customers/
```
Create a new customer account.

#### Update Customer
```
PUT /api/customers/{id}/
```
Update customer information.

### Project Management

#### List Projects
```
GET /api/projects/
```
Returns projects based on user role:
- Administrators: All projects
- Providers: Assigned projects
- Customers: Own projects

#### Create Project
```
POST /api/projects/
```
Create a new project for a customer.

#### Update Project
```
PUT /api/projects/{id}/
```
Update project details.

### SEO Logs

#### List SEO Logs
```
GET /api/seo-logs/
```
Returns SEO work logs based on user permissions.

#### Create SEO Log
```
POST /api/seo-logs/
```
Create a new SEO work log entry.

#### Upload Files
```
POST /api/seo-logs/{id}/files/
```
Upload files associated with an SEO log.

### Reports

#### Generate Report
```
POST /api/reports/generate/
```
Generate a new SEO report.

#### List Reports
```
GET /api/reports/
```
List available reports.

#### Download Report
```
GET /api/reports/{id}/download/
```
Download a specific report in PDF format.

### User Management

#### User Profile
```
GET /api/users/profile/
```
Get current user's profile information.

#### Update Profile
```
PUT /api/users/profile/
```
Update user profile information.

## Response Formats

### Success Response
```json
{
    "status": "success",
    "data": {
        // Response data
    }
}
```

### Error Response
```json
{
    "status": "error",
    "message": "Error description",
    "code": "ERROR_CODE"
}
```

## Rate Limiting

API requests are limited to:
- 100 requests per minute for authenticated users
- 60 requests per minute for anonymous users

## Pagination

List endpoints support pagination with the following parameters:
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)

## Filtering

Most list endpoints support filtering:
- `search`: Search term
- `status`: Filter by status
- `date_from`: Filter by date range start
- `date_to`: Filter by date range end

## Sorting

Use the `ordering` parameter to sort results:
- `ordering=field`: Ascending order
- `ordering=-field`: Descending order

## Error Codes

- `AUTH001`: Authentication required
- `AUTH002`: Invalid credentials
- `PERM001`: Permission denied
- `VAL001`: Validation error
- `NOT001`: Resource not found
- `SRV001`: Server error

## Versioning

The API is versioned using URL prefixing. Current version: v1
Example: `/api/v1/customers/` 