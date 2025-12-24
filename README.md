# DynamicModelApi - Example README

## Overview

`DynamicModelApi` is a RESTful API module for Odoo that allows dynamic access to any model (`GET`, `POST`, `PUT`, `DELETE`) with proper permission checks. The API uses **HTTP routes** and handles JSON bodies directly, making it browser- and `curl`-friendly.

---

## Base URL
http://<odoo-host>:8069/api_gateway/v1/models/

- Replace `<odoo-host>` with your Odoo instance address.
- Model names are Odoo technical model names, e.g., `hr.department`, `res.partner`.

---

## Endpoints

### 1. GET — Retrieve Records

**Parameters:**

- `page` (optional, default=1): Page number for pagination.
- `limit` (optional, default=20, max=100): Records per page.
- `fields` (optional): Comma-separated list of fields to return.

**Example:**

```bash
    curl -X GET "http://localhost:8069/api_gateway/v1/models/hr.department?page=1&limit=5&fields=name,manager_id"

```
Respond data: 
```json

    {
        "model": "hr.department",
        "page": 1,
        "limit": 5,
        "total": 12,
        "result": [
            {"id": 1, "name": "HR", "manager_id": [2, "John Doe"]},
            {"id": 2, "name": "IT", "manager_id": [3, "Jane Smith"]}
        ]
    }

```

### 2. POST — Create Record

```bash
curl --location 'http://localhost:8069/api_gateway/v1/models/hr.department' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOjksImV4cCI6MTc2NTk0NzE2N30.QzZV3MXje3rIzpVsEdRhgm-KbcuTtVs96E0H6DQ8hFk' \

--data '{
  "jsonrpc": "2.0",
  "method": "call",
  "params": {
      "data":{
          "name":"Good"
      }
  }
}
'

```
Respond data: 
```json
    {
        "jsonrpc": "2.0",
        "id": null,
        "result": "<_Response 10 bytes [200 OK]>"
    }

```


### 2. PUT, PATH — Create Record

```bash

curl --location --request PUT 'http://localhost:8069/api_gateway/v1/models/hr.department/3' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOjksImV4cCI6MTc2NTk0NzE2N30.QzZV3MXje3rIzpVsEdRhgm-KbcuTtVs96E0H6DQ8hFk' \
--data '{
  "jsonrpc": "2.0",
  "method": "call",
  "params": {
      "data":{
          "name":"Sale 4444"
      }
  }
}
'
```

Respond data: 
```json
    {
        "jsonrpc": "2.0",
        "id": null,
        "result": "<_Response 10 bytes [200 OK]>"
    }

```
## Get Domain Domain Filter Example

```
1️⃣ JSON-BASED DOMAIN (✅ RECOMMENDED)
➤ OR condition
http://localhost:8069/api_gateway/v1/models/res.users
?domain=[["login","=","admin"],"|",["active","=",true],["share","=",false]]
&page=1
&limit=20


➡️ Domain built:

["|", ("login", "=", "admin"), ("active", "=", True), ("share", "=", False)]

2️⃣ CSV DOMAIN WITH LOGICAL OPERATOR |
➤ name ILIKE "john" OR active = true
http://localhost:8069/api_gateway/v1/models/res.users
?domain_field=name,active
&domain_operator=ilike,=
&domain_value=john,true
&domain_logic=|
&page=1
&limit=10


➡️ Domain built:

["|", ("name", "ilike", "john"), ("active", "=", True)]

3️⃣ CSV DOMAIN WITH AND (&)
➤ internal users AND active
http://localhost:8069/api_gateway/v1/models/res.users
?domain_field=share,active
&domain_operator==,=
&domain_value=false,true
&domain_logic=&


➡️ Domain built:

["&", ("share", "=", False), ("active", "=", True)]

4️⃣ IN OPERATOR WITH LIST VALUES
➤ multiple logins
http://localhost:8069/api_gateway/v1/models/res.users
?domain_field=login
&domain_operator=in
&domain_value=admin|demo|test


➡️ Domain built:

[("login", "in", ["admin", "demo", "test"])]

5️⃣ MIX: IN + AND LOGIC
http://localhost:8069/api_gateway/v1/models/res.users
?domain_field=login,active
&domain_operator=in,=
&domain_value=admin|demo,true
&domain_logic=&


➡️ Domain built:

["&", ("login", "in", ["admin", "demo"]), ("active", "=", True)]

6️⃣ NO DOMAIN (ALL USERS)
http://localhost:8069/api_gateway/v1/models/res.users?page=1&limit=50


➡️ Domain built:

[]
```