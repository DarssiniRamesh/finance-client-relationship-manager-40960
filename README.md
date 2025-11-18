# Project Repository

This is the initial README file for the project.

## Environment Configuration

Two containers are used: a FastAPI backend (`crm_backend`) and a React frontend (`crm_frontend`).

### Backend (.env at crm_backend/.env)

Required variables:
- DATABASE_URL=sqlite:///./crm.db
- JWT_SECRET=<REPLACE_WITH_STRONG_SECRET>
- JWT_EXPIRES_IN=3600
- CORS_ALLOW_ORIGINS=*
- CORS_ALLOW_CREDENTIALS=true
- CORS_ALLOW_METHODS=*
- CORS_ALLOW_HEADERS=*
- DEV_AUTH_BYPASS=true (only for dev)
- DEV_AUTH_USER_EMAIL=dev@example.com

Notes:
- In production, set proper CORS_ALLOW_ORIGINS to your frontend origin.
- Disable DEV_AUTH_BYPASS and ensure JWT_SECRET is a strong secret.

### Frontend (.env at crm_frontend/.env)

- REACT_APP_API_BASE=http://localhost:3001

Point to your backend host/port or preview URL as needed.
