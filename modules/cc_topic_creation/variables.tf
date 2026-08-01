variable "topics" {
  description = "A map of Kafka topic configurations"
  type        = map(object({ config : map(string), cluster_id : string, partitions_count : number }))
  default     = {}
}
variable "rest_endpoint" {
  description = "The REST endpoint for the Kafka cluster"
  type        = string
}