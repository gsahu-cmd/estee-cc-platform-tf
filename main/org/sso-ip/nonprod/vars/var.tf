oidc_identity_provider_id = "op-rgJN"
platform_environment             = "nonprod"

elc_service_accounts = {
  elc-sa-tf = {
    elc_sa_display_name = "elc-sa-tf"
    elc_sa_description  = "Service account via terraform testing"
  }
}

elc_oidc_display_name     = "PingOne-nonprod"
elc_oidc_description      = "PingID Identity Provider for ELC NonProd Workload Identity"
elc_oidc_issuer_uri       = "https://diamond-qa.elcompanies.com/as"
elc_oidc_jwks_uri         = "https://diamond-qa.elcompanies.com/as/jwks"
