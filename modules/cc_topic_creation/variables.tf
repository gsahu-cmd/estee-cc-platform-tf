variable "topics" {
  description = "A map of Kafka topic configurations"
  type        = map(object({ config : map(string), environment_id : string, partitions_count : number }))
  default     = {}
}