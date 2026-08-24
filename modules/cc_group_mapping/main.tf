resource "confluent_group_mapping" "mapping" {
  for_each = var.elc_mod_group_mappings

  display_name = each.value.display_name
  description  = try(each.value.description, null)
  filter       = each.value.filter

  lifecycle {
    prevent_destroy = true
  }
}