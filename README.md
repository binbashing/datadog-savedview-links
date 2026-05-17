Datadog Saved View Links  
*Create static URLs for Datadog Saved Views.*

[Saved Views](https://docs.datadoghq.com/dashboards/template_variables/#saved-views) are a powerful feature of Datadog dashboards — they let you save specific combinations of **template variables** so you can quickly switch between filtered views of your data.  

Unfortunately, Datadog doesn’t currently offer a way to **create links** that automatically apply those Saved View template variable settings when opening a dashboard. This tool aims to **bridge that gap**.

**Datadog Saved View Links** provides a simple, serverless redirect service that allows links like:

> `https://your-api.amazonaws.com/dashboard/prod-errors`

to redirect users directly to the correct Datadog dashboard with the corresponding **template variables applied**.

This can be useful when linking to dashboards from **runbooks**, **documentation**, **other tools**, or even **other dashboards** — giving your team a consistent and reliable way to navigate directly to the views that matter most.

## Quick Start

### Prerequisites
- Python 3.13+
- AWS SAM CLI
- AWS CLI configured with appropriate permissions

### Deployment

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd datadog-savedview-links
   ```

2. **Configure deployment settings**:
   ```bash
   cp samconfig.toml.example samconfig.toml
   # Edit samconfig.toml with your settings:
   # - DatadogApiKey: Your Datadog API key
   # - DatadogAppKey: Your Datadog Application key  
   # - DatadogSite: Your Datadog site (e.g., us5.datadoghq.com)
   ```

3. **Deploy to AWS**:
   ```bash
   sam build
   sam deploy
   ```

   > **Note**: `samconfig.toml` contains sensitive information and is not committed to version control.

The deployed API URL will be shown in the CloudFormation outputs.

### Usage

Once deployed, you can create shareable links like:
```
https://{your-api}.amazonaws.com/dashboard/{dashboard-id}?view={saved-view-name}
```

This will redirect to your Datadog dashboard with the saved view's template variables applied.


## Environment Variables

| Name | Description | Default |
|------|-------------|---------|
| `DATADOG_API_KEY` | Datadog API key | None |
| `DATADOG_APP_KEY` | Datadog application key | None |
| `DATADOG_SITE` | Datadog site domain | `datadoghq.com` |
| `LOG_LEVEL` | Logging level | `INFO` |

## Development

### Local Development

1. **Setup development environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   pip install -r test-requirements.txt
   ```

2. **Run tests**:
   ```bash
   pytest -v
   ```

3. **Run tests with coverage**:
   ```bash
   pytest --cov=src --cov-report=html
   ```

4. **Optional: Test local API** (requires Docker):
   ```bash
   sam build
   sam local start-api
   curl http://127.0.0.1:3000/dashboard/test-123
   ```

### Development Workflow

This project follows Test-Driven Development (TDD):

1. Write failing tests first
2. Implement minimal code to pass tests
3. Refactor and improve
4. Repeat

## Contributing

1. Create a feature branch
2. Write tests for new functionality
3. Implement the feature
4. Ensure all tests pass
5. Submit a pull request

## License

See LICENSE file for details.