/*import {
  to = confluent_tag.master_data
  id = "lsrc-w7o1x0g/master_data"
}*/


/*
  This file is used to import the existing Confluent Cloud environment into Terraform state.
  It should not be modified or deleted, as it is required for the import process.

import {
  to = confluent_environment.elc_nonprod_eastus2
  id = "env-mgzk07"
}

import {
  to = confluent_kafka_cluster.elc_nonprod_eastus2_core_enterprise
  id = "env-mgzk07/lkc-nvo97m6"   # format: <env_id>/<cluster_id>
}

import {
  to = confluent_gateway.elc_nonprod_eastus2_access_gateway
  id = "env-mgzk07/gw-ov05ww"
}

import {
  to = confluent_access_point.elc_nonprod_eastus2_access_point
  id = "env-mgzk07/ap-4lgwy2"   # format: <env_id>/<access_point_id>
}

import {
  to = confluent_identity_provider.elc_nonprod_eastus2_workload_identity
  id = "op-rgJN"
}

import {
  to = confluent_identity_pool.elc_nonprod_eastus2_identity_pool
  id = "op-rgJN/pool-d9JVz"  # format: <identity_provider_id>/<identity_pool_id>
}
*/