# PriceWatch.pt – Guia de Deploy Azure

## Pré-requisitos (instalar uma vez)

```bash
# Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Terraform
sudo apt-get install -y gnupg software-properties-common
wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor | sudo tee /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform

# Docker (para build das imagens)
# https://docs.docker.com/engine/install/
```

---

## Fase 1 – Autenticar no Azure

```bash
az login
# Abre o browser, faz login com a conta amadeuspsgmail@...
# Confirma a subscrição activa:
az account show
az account set --subscription "e29cc6cc-0939-4119-9342-cf8f92a46ac2"
```

---

## Fase 2 – Preparar terraform.tfvars

```bash
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
# Edita terraform.tfvars e preenche:
#   db_password       → password forte para o PostgreSQL
#   anthropic_api_key → a tua chave sk-ant-...
# Os campos b2c_client_id e b2c_client_secret ficam para depois (Fase 4)
```

---

## Fase 3 – Criar infra base (sem B2C ainda)

```bash
cd infra/terraform
terraform init
terraform plan -out=tfplan
terraform apply tfplan
```

Recursos criados (~8 min):
- Resource Group `pricewatch-production-rg`
- Virtual Network + subnets
- Azure PostgreSQL Flexible Server
- Azure Cache for Redis
- Azure Container Registry (ACR)
- Container Apps Environment
- Azure Key Vault com os secrets
- Azure Functions (scrape timer)

---

## Fase 4 – Configurar Azure AD B2C (manual, ~10 min)

O tenant B2C é criado pelo Terraform, mas a app registration tem de ser feita uma vez no portal:

1. **Abre o portal** → pesquisa "Azure AD B2C" → selecciona o tenant `pricewatchpt`
2. **Muda para o tenant B2C** (canto superior direito → "Mudar directório")
3. **Cria atributo personalizado**
   - Azure AD B2C → Atributos de utilizador → Adicionar
   - Nome: `plan` | Tipo: `String`
4. **Cria User Flow**
   - Fluxos de utilizador → Novo fluxo → "Inscrever-se e entrar"
   - Nome: `B2C_1_signupsignin`
   - Em "Atributos do utilizador" → marcar `plan` (recolher + devolver no token)
5. **Regista a aplicação frontend**
   - Registos de aplicativos → Novo registo
   - Nome: `pricewatch-frontend`
   - Tipo de conta: "Contas em qualquer fornecedor de identidade"
   - URI de redirecionamento (SPA):
     - `https://<url-container-app>/dashboard`
     - `http://localhost:3000/dashboard`
   - Em "Autenticação" → activar "Tokens de ID"
   - **Copia o "ID do aplicativo (cliente)"** → vai para `b2c_client_id` no tfvars
6. **Cria client secret**
   - Certificados e segredos → Novo segredo do cliente
   - **Copia o valor** → vai para `b2c_client_secret` no tfvars

---

## Fase 5 – Aplicar B2C ao Terraform

```bash
# Actualiza terraform.tfvars com b2c_client_id e b2c_client_secret
terraform apply
```

---

## Fase 6 – Build e push das imagens Docker

```bash
# Login no ACR
ACR=$(terraform output -raw acr_login_server)
az acr login --name $ACR

# Build API
cd ../../backend
docker build -t $ACR/pricewatch/api:latest .
docker push $ACR/pricewatch/api:latest

# Build Worker (com Playwright)
docker build --build-arg INSTALL_PLAYWRIGHT=true -t $ACR/pricewatch/worker:latest .
docker push $ACR/pricewatch/worker:latest
```

---

## Fase 7 – Migrações da base de dados

```bash
# Corre as migrações Alembic via Container Apps job (ou temporariamente via Docker local)
DATABASE_URL="postgresql://pricewatch:<password>@$(terraform output -raw postgres_fqdn)/pricewatch?sslmode=require" \
  docker run --rm \
  -e DATABASE_URL \
  $ACR/pricewatch/api:latest \
  alembic upgrade head
```

---

## Fase 8 – Deploy do Frontend

```bash
cd ../../frontend
# Build da imagem Next.js standalone
docker build -t $ACR/pricewatch/frontend:latest .
docker push $ACR/pricewatch/frontend:latest

# Ou usar Vercel/Azure Static Web Apps para o frontend (mais simples):
# vercel --prod
```

---

## URLs finais

```bash
cd infra/terraform
terraform output api_url        # URL da API (Container App)
terraform output acr_login_server  # URL do registry
```

---

## Custos estimados (West Europe, ~prod mínimo)

| Recurso | SKU | €/mês |
|---------|-----|-------|
| PostgreSQL Flexible | B_Standard_B1ms | ~€14 |
| Azure Cache for Redis | C1 Basic | ~€16 |
| Container Apps (API) | 0.5 vCPU / 1GB | ~€20 |
| Container Apps (Worker) | 1 vCPU / 2GB | ~€35 |
| Azure AD B2C | Até 50K MAU | Grátis |
| Container Registry | Basic | ~€5 |
| Azure Functions | Consumption | ~€0 |
| Key Vault | Standard | ~€5 |
| **Total** | | **~€95/mês** |
