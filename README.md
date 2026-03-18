# Multi-Tenant Shop Management System (Django + DRF)

A scalable backend system built with **Django** and **Django REST Framework (DRF)** that supports **multi-tenant shop management**.  
The application is designed to allow multiple independent businesses (tenants) to operate within a single system while maintaining **data isolation, security, and scalability**.

---

## Overview

This project demonstrates how to design and implement a **multi-tenant backend architecture** using Django.  
Each tenant (shop/business) operates independently within the same application, making it suitable for **SaaS-style platforms**.

The focus of this project is on:
- Backend system design
- Multi-tenant architecture
- RESTful API development
- Relational database modeling

---

## Key Features

- Multi-tenant architecture with tenant-based data isolation  
- RESTful API design using Django REST Framework  
- Modular Django application structure  
- Custom user authentication system  
- Shop-specific data and operations  
- Scalable backend design for multiple clients  

---

## Multi-Tenancy Design

This system follows a **shared database, shared schema** approach.

- Each record is associated with a tenant identifier  
- All queries are scoped to the active tenant  
- Data is securely isolated between tenants  

### Why this approach?
- Efficient resource usage  
- Easier deployment and scaling  
- Centralized system management  

---

## Tech Stack

- **Backend:** Django  
- **API Layer:** Django REST Framework (DRF)  
- **Language:** Python  
- **Database:** Relational (PostgreSQL / MySQL / SQLite for development)  
- **Version Control:** Git  

---

## Project Structure


- api/ # Core API logic
- authapp/ # Authentication logic
- custom_user/ # Custom user model
- shop/ # Tenant (shop) management
- inventory/ # Inventory per tenant
- orders/ # Orders and transactions
- manage.py
- requirements.txt


---

## Getting Started

### 1. Clone the repository


git clone https://github.com/Petermchikho/Multi-Tenant-Shop-Management-System-Django-DRF.git

cd Multi-Tenant-Shop-Management-System-Django-DRF


### 2. Create a virtual environment


python -m venv venv
venv\Scripts\activate # Windows
source venv/bin/activate # Linux/Mac


### 3. Install dependencies


pip install -r requirements.txt


### 4. Run migrations


python manage.py makemigrations
python manage.py migrate


### 5. Start the server


python manage.py runserver


---

## API Overview

The system exposes RESTful endpoints for:

- Authentication (login/register)  
- Tenant (shop) management  
- Inventory management  
- Orders and transactions  

Example endpoints:


POST /api/auth/login/
GET /api/shops/
POST /api/inventory/


---

## Security Considerations

- Tenant-level data isolation  
- Authenticated access to protected endpoints  
- Input validation and structured error handling  
- Separation of concerns across modules  

---

## Future Improvements

- Role-based access control (RBAC)  
- JWT authentication  
- Tenant-specific subdomains  
- Analytics and reporting per tenant  
- Docker and CI/CD integration  
- Performance optimization (caching, indexing)  

---

## About This Project

This project was built to demonstrate **backend engineering principles** including:

- Designing scalable systems  
- Implementing multi-tenant architectures  
- Structuring maintainable Django applications  
- Building production-style REST APIs  

---

## Author

Peter Charles Mchikho  
Backend Developer (Django, APIs, Systems)

---

## License

This project is intended for educational and portfolio purposes.
