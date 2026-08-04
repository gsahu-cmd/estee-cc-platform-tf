elc_identity_pool_role_bindings = {
  app1_orders_write = {
    identity_pool_id       = "pool-abc123"
    role_name              = "DeveloperWrite"
    resource_kind          = "topic"
    resource_name          = "orders"
    kafka_cluster_id       = "lkc-123456"
    kafka_cluster_rbac_crn = "crn://confluent.cloud/organization=<org-id>/environment=env-123456/cloud-cluster=lkc-123456"
  }

/*
  app1_orders_read = {
    identity_pool_id       = "pool-abc123"
    role_name              = "DeveloperRead"
    resource_kind          = "topic"
    resource_name          = "orders"
    kafka_cluster_id       = "lkc-123456"
    kafka_cluster_rbac_crn = "crn://confluent.cloud/organization=<org-id>/environment=env-123456/cloud-cluster=lkc-123456"
  }

  app1_orders_group_read = {
    identity_pool_id       = "pool-abc123"
    role_name              = "DeveloperRead"
    resource_kind          = "consumer_group"
    resource_name          = "app1-orders-cg"
    kafka_cluster_id       = "lkc-123456"
    kafka_cluster_rbac_crn = "crn://confluent.cloud/organization=<org-id>/environment=env-123456/cloud-cluster=lkc-123456"
  }

  app1_connector_read = {
    identity_pool_id       = "pool-abc123"
    role_name              = "DeveloperRead"
    resource_kind          = "connector"
    resource_name          = "orders-s3-sink"
    kafka_cluster_rbac_crn = "crn://confluent.cloud/organization=<org-id>/environment=env-123456/cloud-cluster=lkc-123456"
  }

  app1_env_admin = {
    identity_pool_id = "pool-abc123"
    role_name        = "EnvironmentAdmin"
    resource_kind    = "environment"
    environment_crn  = "crn://confluent.cloud/organization=<org-id>/environment=env-123456"
  }
  */
}
