# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## Project Overview

This is a Japanese hazard information LINE chatbot and REST API built with Python and AWS Lambda. It provides disaster risk information (earthquakes, floods, landslides, etc.) based on user input of addresses or coordinates.

## Architecture

- **Entry Point**: `lambda_function.py` - AWS Lambda handler
- **Core Modules** (in `app/` directory):
  - `input_parser.py` - Input type detection (coordinates, addresses)
  - `geocoding.py` - Address to coordinates conversion using Google Geocoding API
  - `hazard_api_client.py` - REST API client for external hazard information service
  - `display_formatter.py` - Hazard information formatting for LINE display
  - `line_handler.py` - LINE Messaging API integration
  - `geojsonhelper.py` - GeoJSON data processing utilities

## Key APIs and Data Sources

- **External Hazard REST API**: Primary source for all hazard information (via `HAZARD_MAP_API_URL`)
- **Google Geocoding API**: Address to coordinates conversion (fallback for input processing)
- **LINE Messaging API**: Chatbot interface

### Legacy Data Sources (Removed)
- Previously used J-SHIS API and 国土地理院 WMS directly
- Now replaced by external REST API integration

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Testing
```bash
# Run tests using pytest
pytest

# Run specific test files
pytest tests/test_lambda_function.py tests/test_hazard_info.py -v

# Using venv Python directly (Windows)
.venv\Scripts\pytest.exe
```

### Environment Variables Required
- `HAZARD_MAP_API_URL` - External hazard information REST API endpoint URL
- `LINE_CHANNEL_ACCESS_TOKEN` - LINE Developers channel access token
- `LINE_CHANNEL_SECRET` - LINE Developers channel secret  
- `GOOGLE_API_KEY` - Google Cloud Platform Geocoding API key (fallback for input processing)

## Input Processing Flow

1. **Input Detection**: `input_parser.parse_input_type()` identifies input as:
   - `latlon`: Coordinates (e.g., "35.6586, 139.7454")
   - `address`: Japanese address string
   - `invalid_url`: URLs (rejected)

2. **Coordinate Resolution**:
   - Coordinates: Direct use
   - Address: Geocode to coordinates

3. **Hazard Data Retrieval**: `hazard_api_client.HazardAPIClient.get_hazard_info()` fetches data from external REST API

## REST API Usage

The Lambda function supports both LINE Bot webhooks and direct HTTP requests:

### Parameters
- `lat`, `lon`: Coordinates (required if no `input`)
- `input`: Address or coordinate string
- `datum`: Coordinate system (`wgs84` or `tokyo`, default: `wgs84`)
- `hazard_types`: Comma-separated list to fetch specific hazard types only

### Available Hazard Types
- `earthquake`: Earthquake probability
- `flood`: Flood depth
- `tsunami`: Tsunami depth  
- `high_tide`: High tide depth
- `large_fill_land`: Large-scale fill areas
- `landslide`: Landslide warning areas

## Code Conventions

- Python type hints are used throughout
- Japanese comments and variable names in hazard processing
- Error handling with descriptive Japanese messages for LINE users
- Modular design with clear separation of concerns
- Coordinate system conversion support (WGS84/Tokyo datum)

## Key Files to Understand

- `lambda_function.py:36-50` - REST API integration and display formatting
- `app/hazard_api_client.py` - External REST API client implementation
- `app/display_formatter.py` - Hazard data formatting for LINE display
- `app/input_parser.py:11-30` - Input validation patterns
- `要件定義.md` - Japanese requirements specification
- `HazardInfo_RESTAPI.md` - External REST API specification and usage examples