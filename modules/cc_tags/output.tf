output "tags" {
  description = "Complete tag information (name, ID, and description)"
  value = {
    for name, tag in confluent_tag.tags :
    name => {
      id          = tag.id
      name        = tag.name
      description = tag.description
    }
  }
}
