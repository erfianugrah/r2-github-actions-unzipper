# R2 GitHub Actions Unzipper

A GitHub Actions workflow that automatically unzips compressed files stored in Cloudflare R2 buckets.

## Features

- Automatically detects and extracts zip files from R2 storage
- Replaces original zip files with extracted content in your R2 bucket
- Multi-stage workflow with parallel processing for improved performance
- Scheduled runs with configurable trigger times
- Direct integration with Cloudflare R2 object storage

## Usage

1. Add this workflow to your GitHub repository
2. Configure your Cloudflare R2 credentials as GitHub repository secrets
3. Set up the workflow to run on your desired schedule

This will automatically process zip files in your R2 bucket at scheduled intervals or on demand.

## Configuration

The workflow requires the following GitHub repository secrets:

- `R2_ACCESS_KEY_ID`: Your Cloudflare R2 access key ID
- `R2_SECRET_ACCESS_KEY`: Your Cloudflare R2 secret access key
- `R2_ACCOUNT_ID`: Your Cloudflare account ID
- `R2_BUCKET_NAME`: The name of your R2 bucket

Additional configuration options are available in the workflow file.

## License

[MIT](LICENSE)