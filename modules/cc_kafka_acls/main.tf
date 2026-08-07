resource "confluent_kafka_acl" "acl" {
  for_each = var.elc_mod_kafka_acls

  resource_type = each.value.resource_type
  resource_name = each.value.resource_name
  pattern_type  = each.value.pattern_type
  principal     = each.value.principal
  host          = each.value.host
  operation     = each.value.operation
  permission    = each.value.permission

  lifecycle {
    prevent_destroy = true
  }
}