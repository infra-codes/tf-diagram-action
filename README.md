Make Input File : terraform show -json terraform.tfstate > { location }

# Generate Terraform Diagram Action

This GitHub Action parses a terraform.tfstate file and generates an infrastructure diagram using [diagrams.mingrammer.com](https://diagrams.mingrammer.com/).

## Inputs

| Name          | Required | Description                        |
|---------------|----------|------------------------------------|
| tfstate_path  | ✅        | Path to terraform.tfstate.json     |
| output_path   | ✅        | Path to save diagram (PNG)         |
| cloud_provider| ✅        | Where did you make terraform (PNG) |

## Example

```yaml
- uses: your-username/tf-diagram-action@v1
  with:
    tfstate_path: ./infra/terraform.tfstate.json
    output_path: ./output/diagram.png
    cloud_provider: oci
