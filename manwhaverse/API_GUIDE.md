# Manwhaverse API Guide

## Base URL

```
http://localhost:8081
```

> **Note:** Ensure the backend server is running before making API calls.

---

## Endpoints Overview

| Method | Endpoint                      | Description                          |
|--------|-------------------------------|--------------------------------------|
| GET    | `/api/manwhas/featured`       | Get the featured manwha              |
| GET    | `/api/manwhas/popular`        | Get list of popular manwhas          |
| GET    | `/api/manwhas/{id}`           | Get manwha details by URL ID         |
| GET    | `/api/manwhas/details?id={id}`| Get manwha details (query param)     |
| GET    | `/api/manwhas/{id}/chapters`  | Get chapters for a manwha            |
| GET    | `/api/manwhas/chapters?id={id}`| Get chapters (query param)          |
| GET    | `/api/chapters/{id}`          | Get a single chapter by ID           |

---

## Detailed Endpoints

### 1. Get Featured Manwha

**GET** `/api/manwhas/featured`

Returns a single featured manwha.

**Response:**
```json
{
  "url": "solo-leveling",
  "title": "Solo Leveling",
  "lastChapter": 179,
  "description": "10 years ago, after the 'Gate' that connected...",
  "bannerImage": "/downloads/banners/solo-leveling.jpg",
  "author": "Chugong",
  "status": "Completed",
  "views": "50M",
  "genres": "Action, Adventure, Fantasy",
  "chapters": null
}
```

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - No featured manwha available

---

### 2. Get Popular Manwhas

**GET** `/api/manwhas/popular`

Returns a list of popular manwhas.

**Response:**
```json
[
  {
    "url": "solo-leveling",
    "title": "Solo Leveling",
    "lastChapter": 179,
    "description": "...",
    "bannerImage": "/downloads/banners/solo-leveling.jpg",
    "author": "Chugong",
    "status": "Completed",
    "views": "50M",
    "genres": "Action, Adventure, Fantasy",
    "chapters": null
  },
  {
    "url": "tower-of-god",
    "title": "Tower of God",
    "lastChapter": 550,
    "description": "...",
    "bannerImage": "/downloads/banners/tower-of-god.jpg",
    "author": "SIU",
    "status": "Ongoing",
    "views": "45M",
    "genres": "Action, Adventure, Fantasy",
    "chapters": null
  }
]
```

**Status Codes:**
- `200 OK` - Success (may return empty array `[]`)

---

### 3. Get Manwha Details

**GET** `/api/manwhas/{id}`

Get detailed information about a specific manwha.

**Path Parameters:**
| Name | Type   | Description                      |
|------|--------|----------------------------------|
| id   | string | The URL slug of the manwha       |

**Example:**
```
GET /api/manwhas/solo-leveling
```

**Response:**
```json
{
  "url": "solo-leveling",
  "title": "Solo Leveling",
  "lastChapter": 179,
  "description": "10 years ago, after the 'Gate' that connected...",
  "bannerImage": "/downloads/banners/solo-leveling.jpg",
  "author": "Chugong",
  "status": "Completed",
  "views": "50M",
  "genres": "Action, Adventure, Fantasy",
  "chapters": null
}
```

**Alternative (Query Parameter):**
```
GET /api/manwhas/details?id=solo-leveling
```

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - Manwha not found

---

### 4. Get Chapters for a Manwha

**GET** `/api/manwhas/{id}/chapters`

Get all chapters for a specific manwha.

**Path Parameters:**
| Name | Type   | Description                      |
|------|--------|----------------------------------|
| id   | string | The URL slug of the manwha       |

**Example:**
```
GET /api/manwhas/solo-leveling/chapters
```

**Response:**
```json
[
  {
    "id": 1,
    "title": "Chapter 1: Prologue",
    "number": 1.0,
    "releaseDate": "2018-03-25",
    "images": [
      {
        "id": 1,
        "pageNumber": 1,
        "imagePath": "/downloads/solo-leveling/1/001.jpg"
      },
      {
        "id": 2,
        "pageNumber": 2,
        "imagePath": "/downloads/solo-leveling/1/002.jpg"
      }
    ]
  },
  {
    "id": 2,
    "title": "Chapter 2",
    "number": 2.0,
    "releaseDate": "2018-03-25",
    "images": [...]
  }
]
```

**Alternative (Query Parameter):**
```
GET /api/manwhas/chapters?id=solo-leveling
```

**Status Codes:**
- `200 OK` - Success (may return empty array `[]`)

---

### 5. Get Single Chapter

**GET** `/api/chapters/{id}`

Get details for a single chapter including all images.

**Path Parameters:**
| Name | Type   | Description                      |
|------|--------|----------------------------------|
| id   | number | The chapter ID (database ID)     |

**Example:**
```
GET /api/chapters/1
```

**Response:**
```json
{
  "id": 1,
  "title": "Chapter 1: Prologue",
  "number": 1.0,
  "releaseDate": "2018-03-25",
  "images": [
    {
      "id": 1,
      "pageNumber": 1,
      "imagePath": "/downloads/solo-leveling/1/001.jpg"
    },
    {
      "id": 2,
      "pageNumber": 2,
      "imagePath": "/downloads/solo-leveling/1/002.jpg"
    }
  ]
}
```

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - Chapter not found

---

## Data Models

### Manwha

| Field        | Type     | Description                           |
|--------------|----------|---------------------------------------|
| url          | string   | Unique URL slug (primary key)         |
| title        | string   | Display title                         |
| lastChapter  | integer  | Latest chapter number                 |
| description  | string   | Full description                      |
| bannerImage  | string   | Path to banner image                  |
| author       | string   | Author name                           |
| status       | string   | "Ongoing" or "Completed"              |
| views        | string   | View count (e.g., "50M")              |
| genres       | string   | Comma-separated genres                |
| chapters     | array    | List of chapters (null in list views) |

### Chapter

| Field       | Type     | Description                           |
|-------------|----------|---------------------------------------|
| id          | number   | Unique database ID                    |
| title       | string   | Chapter title                         |
| number      | number   | Chapter number (can be decimal: 1.5)  |
| releaseDate | string   | Release date (YYYY-MM-DD format)      |
| images      | array    | List of ChapterImage objects          |

### ChapterImage

| Field      | Type     | Description                           |
|------------|----------|---------------------------------------|
| id         | number   | Unique database ID                    |
| pageNumber | integer  | Page order number                     |
| imagePath  | string   | Path to the image file                |

---

## Static Files (Images)

Images are served from the `/downloads/` path. To access an image:

```
http://localhost:8081/downloads/{imagePath}
```

**Example:**
```
http://localhost:8081/downloads/solo-leveling/1/001.jpg
```

---

## CORS Configuration

The backend allows requests from:
- `http://localhost:5174`

Allowed methods: `GET`, `POST`, `PUT`, `DELETE`, `OPTIONS`

---

## Example Frontend API Client

```javascript
const API_BASE = 'http://localhost:8081/api';

const api = {
  // Get featured manwha
  getFeatured: () => fetch(`${API_BASE}/manwhas/featured`).then(r => r.json()),
  
  // Get popular manwhas
  getPopular: () => fetch(`${API_BASE}/manwhas/popular`).then(r => r.json()),
  
  // Get manwha details
  getManwha: (id) => fetch(`${API_BASE}/manwhas/${encodeURIComponent(id)}`).then(r => r.json()),
  
  // Get chapters for a manwha
  getChapters: (id) => fetch(`${API_BASE}/manwhas/${encodeURIComponent(id)}/chapters`).then(r => r.json()),
  
  // Get single chapter
  getChapter: (id) => fetch(`${API_BASE}/chapters/${id}`).then(r => r.json()),
};

export default api;
```

---

## Error Handling

All endpoints return standard HTTP status codes:

| Status | Description                          |
|--------|--------------------------------------|
| 200    | Success                              |
| 404    | Resource not found                   |
| 500    | Internal server error                |

For errors, the response body may be empty or contain an error message.
