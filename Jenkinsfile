@Library('lib')_

pythonPipeline {
  package_name            = 'clms_metadata'
  python_version          = ['3.10', '3.12']
  create_tag_job          = true
  run_tests               = true
  build_container_image   = true
  docker_deploy           = false
  docker_registry_prod    = 'vito-docker.artifactory.vgt.vito.be'
  dev_hosts               = ['nifi-dev-01.vgt.vito.be', 'nifi-dev-02.vgt.vito.be', 'nifi-dev-03.vgt.vito.be']
}