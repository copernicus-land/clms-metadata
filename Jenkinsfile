@Library('lib')_

pythonPipeline {
  package_name            = 'clms_metadata'
  python_version          = ['3.10']
  create_tag_job          = true
  run_tests               = true
  build_container_image   = true
  extra_container_volumes = [
    '/data/MTDA/:/data/MTDA/:ro'
  ]
  docker_deploy           = false
  dev_hosts               = ['nifi-dev-01.vgt.vito.be', 'nifi-dev-02.vgt.vito.be', 'nifi-dev-03.vgt.vito.be']
}