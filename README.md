# aviate
# Candidate Management API

The Candidate Management API is a Django-based application for managing candidate records. It provides endpoints for creating, retrieving, updating, deleting, and searching candidates. The project leverages Django REST Framework (DRF) for building a robust and scalable API.

---

## Features

- Create, update, delete, and retrieve candidate records.
- Search candidates by name with relevancy scoring.
- Pagination support for listing results.
- Validation for fields like email, phone number, age, and gender.
- Custom exception handling for clear and consistent error responses.

---

## Requirements

- Python 3.8+
- Django 4.2+
- Django REST Framework 3.14+
- SQLite (default) or any other Django-supported database.

---

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/candidate-management-api.git
cd candidate-management-api