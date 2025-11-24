# Flutter Authentication Integration Guide

This guide explains how to use the Django backend authentication endpoints from a Flutter application using the `pbp_django_auth` package.

## Overview

The Django backend now provides JSON-based authentication endpoints that are compatible with Flutter's `pbp_django_auth` package. These endpoints complement the existing HTML-based authentication without replacing them.

## Endpoints

All authentication endpoints are prefixed with `/auth/json/`:

- **POST** `/auth/json/login/` - User login
- **POST** `/auth/json/signup/` - User registration
- **POST** `/auth/json/logout/` - User logout

## Installation

### Django Backend (Already Configured)

The following packages have been added to `requirements.txt`:
```
django-cors-headers==4.3.1
```

### Flutter Application

Add the following dependency to your `pubspec.yaml`:
```yaml
dependencies:
  pbp_django_auth: ^1.0.0
```

## Usage Examples

### 1. Setup in Flutter

First, initialize the `CookieRequest` in your Flutter app:

```dart
import 'package:pbp_django_auth/pbp_django_auth.dart';
import 'package:provider/provider.dart';

void main() {
  runApp(
    Provider(
      create: (_) => CookieRequest(),
      child: MyApp(),
    ),
  );
}
```

### 2. Login

```dart
import 'package:pbp_django_auth/pbp_django_auth.dart';
import 'package:provider/provider.dart';

Future<void> login(BuildContext context) async {
  final request = context.read<CookieRequest>();
  
  final response = await request.login(
    "http://your-domain.com/auth/json/login/",
    {
      'username': usernameController.text,
      'password': passwordController.text,
    }
  );
  
  if (response['status']) {
    // Login successful
    String username = response['username'];
    String message = response['message'];
    
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (context) => HomePage()),
    );
    
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('$message Welcome, $username!')),
    );
  } else {
    // Login failed
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Login Failed'),
        content: Text(response['message']),
        actions: [
          TextButton(
            child: Text('OK'),
            onPressed: () => Navigator.pop(context),
          ),
        ],
      ),
    );
  }
}
```

### 3. Signup

```dart
import 'package:pbp_django_auth/pbp_django_auth.dart';
import 'package:provider/provider.dart';

Future<void> signup(BuildContext context) async {
  final request = context.read<CookieRequest>();
  
  final response = await request.post(
    "http://your-domain.com/auth/json/signup/",
    {
      'username': usernameController.text,
      'password1': password1Controller.text,
      'password2': password2Controller.text,
      'email': emailController.text,
      'first_name': firstNameController.text,
      'last_name': lastNameController.text,
      'account_type': 'BUYER', // or 'SELLER'
    }
  );
  
  if (response['status']) {
    // Signup successful
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Success'),
        content: Text('Account created! Please login.'),
        actions: [
          TextButton(
            child: Text('OK'),
            onPressed: () {
              Navigator.pop(context);
              Navigator.pushReplacement(
                context,
                MaterialPageRoute(builder: (context) => LoginPage()),
              );
            },
          ),
        ],
      ),
    );
  } else {
    // Signup failed
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Signup Failed'),
        content: Text(response['message']),
        actions: [
          TextButton(
            child: Text('OK'),
            onPressed: () => Navigator.pop(context),
          ),
        ],
      ),
    );
  }
}
```

### 4. Logout

```dart
import 'package:pbp_django_auth/pbp_django_auth.dart';
import 'package:provider/provider.dart';

Future<void> logout(BuildContext context) async {
  final request = context.read<CookieRequest>();
  
  final response = await request.logout(
    "http://your-domain.com/auth/json/logout/"
  );
  
  if (response['status']) {
    // Logout successful
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (context) => LoginPage()),
    );
    
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(response['message'])),
    );
  }
}
```

## API Response Format

All endpoints return JSON responses in the following format:

### Success Response
```json
{
  "status": true,
  "username": "testuser",
  "message": "Operation successful!"
}
```

### Error Response
```json
{
  "status": false,
  "message": "Error description"
}
```

## Field Requirements

### Login
- **username** (required): User's username
- **password** (required): User's password

### Signup
- **username** (required): Desired username
- **password1** (required): Password
- **password2** (required): Password confirmation (must match password1)
- **email** (optional): User's email address
- **first_name** (optional): User's first name
- **last_name** (optional): User's last name
- **account_type** (optional): Either 'BUYER' or 'SELLER' (defaults to 'BUYER')

### Logout
No fields required. The endpoint uses the session cookie to identify the user.

## Error Handling

The endpoints validate input and return appropriate error messages:

1. **Missing Required Fields**: "Username and password are required."
2. **Invalid Credentials**: "Invalid username or password."
3. **Password Mismatch**: "Passwords do not match."
4. **Username Exists**: "Username already exists."
5. **Invalid Account Type**: "Invalid account type. Must be one of: BUYER, SELLER."
6. **Invalid Method**: "Invalid request method."

## CORS Configuration

The backend is configured to handle CORS for cross-origin requests:

- **Development**: CORS allows all origins
- **Production**: CORS should be restricted to your Flutter app's domain

## Security Considerations

1. **HTTPS**: Always use HTTPS in production to protect credentials
2. **Error Messages**: Generic error messages are returned in production to avoid exposing sensitive information
3. **Session Security**: Session cookies are marked as secure and HTTP-only in production
4. **CSRF Protection**: CSRF tokens are handled automatically by the `pbp_django_auth` package

## Testing

You can test the endpoints using curl:

```bash
# Signup
curl -X POST http://localhost:8000/auth/json/signup/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password1": "TestPass123!", "password2": "TestPass123!", "email": "test@example.com", "account_type": "BUYER"}'

# Login
curl -X POST http://localhost:8000/auth/json/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "TestPass123!"}' \
  -c cookies.txt

# Logout
curl -X POST http://localhost:8000/auth/json/logout/ \
  -b cookies.txt
```

## Additional Features

### Cart Transfer
When a user logs in via the JSON endpoint, their guest cart (if any) is automatically transferred to their user account, maintaining consistency with the web-based login.

### Profile Creation
Upon signup, the system automatically creates:
1. A User account
2. A Customer profile (for e-commerce functionality)
3. A Profile with the specified account type and personal information

## Troubleshooting

### CORS Errors
If you encounter CORS errors in production, ensure that:
1. Your Flutter app's domain is added to `CORS_ALLOWED_ORIGINS` in `settings.py`
2. `CORS_ALLOW_ALL_ORIGINS` is set to `False` in production

### Session Issues
If sessions aren't persisting:
1. Verify that cookies are being saved and sent by your Flutter app
2. Check that `CORS_ALLOW_CREDENTIALS` is set to `True`
3. Ensure your app is using HTTPS in production

### Authentication Failures
If authentication fails:
1. Verify the endpoint URL is correct
2. Check that all required fields are provided
3. Ensure passwords meet Django's validation requirements
4. Review the error message returned by the API

## Support

For issues or questions:
1. Check the Django logs for detailed error information
2. Verify your network requests in Flutter's debug console
3. Test the endpoints directly with curl to isolate issues
4. Review the test cases in `apps/authentication/tests.py` for examples
