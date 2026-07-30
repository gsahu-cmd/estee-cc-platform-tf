resource "confluent_service_account" "service_account" {
  for_each = var.elc_mod_service_accounts

  display_name = each.value.elc_mod_sa_display_name
  description  = each.value.elc_mod_sa_description
}
