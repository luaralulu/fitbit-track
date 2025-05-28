# Fitbit Stats Extract

A Python application to extract and store Fitbit data using Supabase.

## Setup

1. Clone the repository:

```bash
git clone <your-new-repo-url>
cd fitbit-stats-extract
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your credentials:

```bash
cp .env.example .env
```

Then edit `.env` with your actual credentials.

## Security Best Practices

1. Never commit sensitive data to git:

   - Keep all credentials in `.env` file
   - Add `.env` to `.gitignore`
   - Use environment variables in production

2. Rotate credentials regularly:

   - Fitbit API tokens
   - Supabase credentials
   - Any other API keys

3. Use secure storage:
   - Store tokens in Supabase
   - Use environment variables
   - Never hardcode credentials

## Development

1. Run tests:

```bash
pytest
```

2. Run the sync script:

```bash
python script.py
```

## License

MIT

## Features

- Automated daily Fitbit data extraction
- Secure storage in Supabase database
- Handles authentication and token refresh
- Comprehensive error handling
- Detailed logging
- Unit tests with pytest

## Prerequisites

- Python 3.9 or higher
- PostgreSQL (for local development)
- Fitbit Developer Account
- Supabase Account

## Configuration

Create a `.env` file in the root directory with the following variables:

```env
# Fitbit API Credentials
FITBIT_CLIENT_ID=your_client_id
FITBIT_CLIENT_SECRET=your_client_secret

# Supabase Configuration
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
SUPABASE_USER_EMAIL=your_user_email
SUPABASE_USER_PASSWORD=your_user_password
```

### Obtaining Credentials

1. **Fitbit API Credentials**:

   - Go to [Fitbit Developer Dashboard](https://dev.fitbit.com/apps)
   - Create a new application
   - Note down the Client ID and Client Secret
   - Use `gather_keys_oauth2.py` to obtain access and refresh tokens

2. **Supabase Credentials**:
   - Go to your [Supabase Dashboard](https://app.supabase.com)
   - Create a new project or select existing one
   - Get the project URL and service role key from Project Settings
   - Create a user account for the application

## Database Setup

1. Run the Supabase migrations:

```bash
psql -U postgres -d postgres -f supabase_migrations.sql
```

## Usage

Run the main script to sync Fitbit data:

```bash
python script.py
```

The script will:

1. Authenticate with Supabase
2. Get the last recorded date
3. Fetch Fitbit data for missing dates
4. Store the data in Supabase
5. Handle any errors and log the process

## Testing

Run the test suite:

```bash
python -m pytest tests/
```

Run tests with coverage report:

```bash
python -m pytest tests/ --cov=.
```

## Project Structure

```
fitbit-stats-extract/
├── backups/              # Database backup files
├── tests/               # Test files
├── .env                 # Environment variables (not in git)
├── .gitignore          # Git ignore file
├── fitbit_auth.py      # Fitbit authentication utilities
├── fitbit_daily_data.py # Fitbit data extraction
├── fitbit_utils.py     # Fitbit utility functions
├── gather_keys_oauth2.py # OAuth2 token gathering
├── requirements.txt    # Project dependencies
├── script.py          # Main application script
├── supabase_migrations.sql # Database schema
└── supabase_utils.py  # Supabase utilities
```

## Error Handling

The application includes comprehensive error handling for:

- Authentication failures
- API rate limits
- Network issues
- Data validation
- Database operations

All errors are logged with appropriate context for debugging.
