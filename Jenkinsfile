#!/usr/bin/env groovy

import static uk.gov.landregistry.jenkins.pipeline.ClosureUtils.applicationPipelineConfig

// See https://internal-git-host/common-code/jenkins-pipelines/-/blob/master/vars/pythonExtendedPipeline.groovy
// Any parameter being set to the same as the default could be removed; it is there for clarity and learning purposes only
pythonExtendedPipeline applicationPipelineConfig {
  // dockerImageName 'flask-skeletonxl-api' // Default is same value as projectName
  // releaseBranchPrefix 'release/' // Default. Used for hotifixing the matching helm-chart release branch
  // unitTestModules ([]) // Default

  s2iImageName "stp-s2i-python-extended-postgis:3.9"

  devOpsNamespace 'llc-devops'
  dockerRegistry 'docker-registry/local-land-charges'
  projectName 'local-authority-api'
  pythonVersion '3.9'
  unitTestEnvironmentFile './unit-test-env.sh' // Default is /dev/null
  trunkBranch 'develop'
  
  helmProject {
    chartPath 'local-land-charges/charts/local-authority-api'
    chartRepository 'git@internal-git-host:llc-beta/helm-charts.git'
    gitCredentialsId 'llc-deploy-key'
    trunkHelmUpdateBranch 'integration' // Target for updating the version, ignored in release branch hotfix scenario
  }

}
