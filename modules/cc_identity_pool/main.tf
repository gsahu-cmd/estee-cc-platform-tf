resource "confluent_identity_pool" "pool" {
  for_each = var.elc_mod_oidc_identity_pools

  identity_provider {
    id = var.elc_mod_oidc_identity_provider_id
  }

  display_name   = each.value.display_name
  description    = each.value.description
  identity_claim = each.value.identity_claim
  filter         = each.value.filter
}
