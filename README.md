# ops-console

## Infrastructure

All BigQuery datasets and the landing bucket's lifecycle rule are declared in Terraform
under `infra/`. Auth uses Application Default Credentials.

```bash
gcloud auth application-default login
cd infra
cp terraform.tfvars.example terraform.tfvars   # then fill in real values
terraform init
terraform plan -out=tfplan
terraform apply tfplan
```

The landing bucket was created by hand and is brought into state by the `import` block
in `infra/storage.tf`. The first plan should show it as **import + update in-place**
(lifecycle rule only) — never a replacement.
