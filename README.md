# Datadog Saved View Links

A lightweight AWS SAM-based service that generates redirectable URLs for Datadog dashboard saved views.

## Quick Start

### Prerequisites
- Python 3.12+
- AWS SAM CLI
- Docker Desktop (for local testing)

### Local Development

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd datadog-savedview-links
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   pip install -r test-requirements.txt
   ```

2. **Build and test locally**:
   ```bash
   sam build
   sam local start-api
   ```

3. **Test the endpoint**:
   ```bash
   curl http://127.0.0.1:3000/dashboard/test-123
   ```

   Expected response:
   ```
   Datadog Saved View Links service ready for dashboard test-123
   ```

### Testing

Run unit tests:
```bash
pytest -v
```

Run tests with coverage:
```bash
pytest --cov=src --cov-report=html
```

### Deployment

1. **Configure deployment settings**:
   ```bash
   cp samconfig.toml.example samconfig.toml
   # Edit samconfig.toml with your settings:
   # - DatadogApiKey: Your Datadog API key
   # - DatadogAppKey: Your Datadog Application key  
   # - DatadogSite: Your Datadog site (e.g., us5.datadoghq.com)
   ```

2. **Deploy to AWS**:
   ```bash
   sam build
   sam deploy
   ```

   > **Note**: `samconfig.toml` contains sensitive information and is not committed to version control.

The deployed API URL will be shown in the CloudFormation outputs.

## Project Structure

```
datadog-savedview-links/
├── template.yaml          # AWS SAM template
├── src/
│   ├── handler.py          # Lambda entry point
│   ├── datadog_client.py   # Datadog API client
│   └── utils.py            # URL building utilities
├── tests/                  # Test suite
├── requirements.txt        # Production dependencies
├── test-requirements.txt   # Development dependencies
└── README.md              # This file
```

## Architecture

```
User → API Gateway → Lambda (Python 3.12/ARM64) → Datadog API → Redirect (302)
```

**Key Features:**
- **ARM64/Graviton2**: Optimized for better performance and lower cost
- **Python 3.12**: Latest Python runtime with improved performance
- **Serverless**: Auto-scaling Lambda with minimal cold start
- **Regional**: Deployed close to your users for low latency

## Development Workflow

This project follows Test-Driven Development (TDD):

1. Write failing tests first
2. Implement minimal code to pass tests
3. Refactor and improve
4. Repeat

## Environment Variables

| Name | Description | Default |
|------|-------------|---------|
| `DATADOG_API_KEY` | Datadog API key | `REPLACE_ME` |
| `DATADOG_APP_KEY` | Datadog application key | `REPLACE_ME` |
| `DATADOG_SITE` | Datadog site domain | `datadoghq.com` |
| `LOG_LEVEL` | Logging level | `INFO` |

## Contributing

1. Create a feature branch
2. Write tests for new functionality
3. Implement the feature
4. Ensure all tests pass
5. Submit a pull request

## License

See LICENSE file for details.