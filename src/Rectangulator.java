trigger:
- master  # Adjust as needed

pool:
  vmImage: 'ubuntu-latest'

jobs:
- job: BuildJob
  pool:
    name: ${{ variables['agentPoolName'] }}  # Dynamic agent pool

  steps:
  - task: Bash@3
    inputs:
      targetType: inline
      script: |
        # Get the current repo name dynamically in bash
        currentRepoName=$(echo $BUILD_REPOSITORY_NAME)
        currentJobName=$(echo $SYSTEM_DEFINITIONNAME)  # Use system definition name for job name

        # Initialize match flags
        repoMatch=false
        jobMatch=false

        # Check if `app-name.yml` exists in the same directory and match repo
        if [ -f "./app-name.yml" ]; then
          if grep -q "$currentRepoName" ./app-name.yml; then
            repoMatch=true
          fi
        fi

        # Check if `job-name.yml` exists and matches the job name
        if [ -f "./job-name.yml" ]; then
          if grep -q "$currentJobName" ./job-name.yml; then
            jobMatch=true
          fi
        fi

        # Print out the repo name, job name, and match results
        echo "Repo Name: $currentRepoName"
        echo "Job Name: $currentJobName"
        echo "Repo Match: $repoMatch"
        echo "Job Match: $jobMatch"

        # Decide on the agent pool and print the result
        if [[ "$repoMatch" == "true" || "$jobMatch" == "true" ]]; then
          echo "Using 'main' pool"
          echo "##vso[task.setvariable variable=agentPoolName]main"
        else
          echo "Using 'Prod' pool"
          echo "##vso[task.setvariable variable=agentPoolName]Prod"
        fi

  - task: Bash@3
    inputs:
      targetType: 'inline'
      script: |
        echo "Selected Agent Pool: ${{ variables['agentPoolName'] }}"
