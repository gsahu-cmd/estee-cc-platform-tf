elc_oidc_identity_provider_id = "op-rgJN"

elc_oidc_identity_pools = {
  pool1 = {
    display_name   = "gyan-pool1"
    description    = "Identity pool 1"
    identity_claim = "claims.client_id"
    filter         = "'webmethods' in claims.aud && claims.iss == 'https://diamond-qa.elcompanies.com/as'"
  }

  pool2 = {
    display_name   = "gyan-pool2"
    description    = "Identity pool 2"
    identity_claim = "claims.client_id"
    filter         = "'webmethods' in claims.aud && claims.iss == 'https://diamond-qa.elcompanies.com/as'"
  }

  pool3 = {
    display_name   = "gyan-pool3"
    description    = "Identity pool 3"
    identity_claim = "claims.client_id"
    filter         = "claims.iss == 'https://diamond-qa.elcompanies.com/as'"
  }
}