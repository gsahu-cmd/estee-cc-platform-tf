oidc_identity_provider_id = "op-77G4"
platform_environment      = "prod"

elc_service_accounts = {
  elc-sa-tf = {
    elc_sa_display_name = "elc-sa-tf"
    elc_sa_description  = "Service account via terraform testing"
  }
}

elc_oidc_display_name     = "PingOne-prod"
elc_oidc_description      = "PingID Identity Provider for ELC Prod Workload Identity"
elc_oidc_issuer_uri       = "https://diamond.elcompanies.com/as"
elc_oidc_jwks_uri         = "https://diamond.elcompanies.com/as/jwks"
