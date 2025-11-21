@Library('lib')_

pythonPipeline {
  package_name            = 'clms_metadata'
  python_version          = ['3.12']
  create_tag_job          = true
  run_tests               = true
  extras_require          = 'dev,ci'
  build_container_image   = true
  docker_registry_prod    = 'vito-docker.artifactory.vgt.vito.be'
  enable_uv               = true
  enable_caching          = true
  venv_rpm_deps           = ['gdal-3.11.3', 'gdal-python312-3.11.3']
}