terraform {
	required_providers {
		confluent = {
			source  = "confluentinc/confluent"
			version = "~> 2.76"  # Allows patch updates (2.76.x), blocks 2.77+
		}
	}
}