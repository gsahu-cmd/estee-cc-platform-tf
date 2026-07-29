# Create multiple Confluent tags
resource "confluent_tag" "tags" {
  for_each = var.elc_mod_tags

  name        = each.key
  description = each.value

  lifecycle {
    prevent_destroy = true
  }
}
