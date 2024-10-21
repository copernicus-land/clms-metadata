@Library('lib')_

pythonPipeline {
  package_name            = 'clms_metadata'
  python_version          = '3.10'
  create_tag_job          = true
  run_tests               = false
  build_container_image   = false
  extra_container_volumes = [
    '/data/MTDA/:/data/MTDA/:ro'
  ]
}