@Library('lib')_

pythonPipeline {
  package_name            = 'clms_metadata'
  python_version          = ['3.10', '3.12']
  create_tag_job          = true
  run_tests               = true
  extras_require          = 'dev'
  build_container_image   = true
  docker_registry_prod    = 'vito-docker.artifactory.vgt.vito.be'
  enable_uv               = true
  enable_caching          = true
}