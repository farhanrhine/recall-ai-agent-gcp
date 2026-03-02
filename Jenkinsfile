pipeline {
    agent any

    environment {
        DOCKER_HUB_REPO = "farhanrhine/recall-ai-agent-gcp" // replace with your DockerHub repo name
        DOCKER_HUB_CREDENTIALS_ID = "dockerhub-token"      // replace with the actual credentials ID you created in Jenkins
        IMAGE_TAG = "v${BUILD_NUMBER}" // using build number as tag to ensure uniqueness for each build. This prevents Argo CD from ignoring changes when image tag stays same.
    }

    stages {

        stage('Checkout Github') {
            steps {
                echo 'Checking out code from GitHub...'
                checkout scmGit(
                    branches: [[name: '*/main']],
                    extensions: [],
                    userRemoteConfigs: [[
                        credentialsId: 'github-token',
                        url: 'https://github.com/farhanrhine/recall-ai-agent-gcp.git'
                    ]]
                ) 
                // change this line when you **Generate Pipeline Script**
                // NOTE: use // not # because Groovy does NOT support # comments. Using # can break pipeline parsing.
            }   
        }        

        stage('Build Docker Image') { 
            steps {
                script {
                    echo 'Building Docker image...'
                    dockerImage = docker.build("${DOCKER_HUB_REPO}:${IMAGE_TAG}")
                }
            } 
            // simple its build docker image inside jenkins.
            // This builds the image locally inside Jenkins agent (GCP VM Docker engine).
        } 

        stage('Push Image to DockerHub') { 
            steps {
                script {
                    echo 'Pushing Docker image to DockerHub...'
                    docker.withRegistry('https://registry.hub.docker.com' , DOCKER_HUB_CREDENTIALS_ID) {
                        dockerImage.push("${IMAGE_TAG}")
                    }
                } 
                // simple its push docker image using DOCKER_HUB_CREDENTIALS_ID which we created in Jenkins.
                // This credential is used to authenticate with DockerHub securely.
            }
        } 
        // at stage 3 uncomment everything when enabling full pipeline.

        // stage('Update Deployment YAML with New Tag') {
        //     steps {
        //         script {
        //             sh """
        //             sed -i "s|image: .*|image: ${DOCKER_HUB_REPO}:${IMAGE_TAG}|" manifests/deployment.yaml
        //             """
        //         } 
        //         // this is easy way (stackoverflow trick) to update image tag in deployment.yaml.
        //         // BEFORE: it was hardcoded:
        //         // sed -i 's|image: farhanrhine/...|image: farhanrhine/...:${IMAGE_TAG}|'
        //         // PROBLEM: if repo name changes, pipeline breaks.
        //         // NOW: using ${DOCKER_HUB_REPO} makes it dynamic and reusable.
        //         // This is important because Argo CD will detect change in Git and sync new image to Kubernetes.
        //     }
        // }

        // stage('Commit Updated YAML') {
        //     steps {
        //         script {
        //             withCredentials([usernamePassword(
        //                 credentialsId: 'github-token', 
        //                 usernameVariable: 'GIT_USER', 
        //                 passwordVariable: 'GIT_PASS'
        //             )]) {

        //                 // Using triple double quotes (""") so Groovy resolves ${IMAGE_TAG}
        //                 // Shell variables ${GIT_USER} and ${GIT_PASS} are escaped with \$ 
        //                 // so SHELL resolves them, not Groovy.

        //                 sh """
        //                 git config user.name "farhanrhine"
        //                 git config user.email "mohammadfarhanalam09@gmail.com"

        //                 git add manifests/deployment.yaml
        //                 git commit -m "Update image tag to ${IMAGE_TAG}" || echo "No changes to commit"

        //                 git remote set-url origin https://\${GIT_USER}:\${GIT_PASS}@github.com/farhanrhine/recall-ai-agent-gcp.git
        //                 git push origin HEAD:main
        //                 """
        //             }
        //         }
        //     }
        //     // BEFORE: directly pushing using full URL in git push command.
        //     // NOW: using git remote set-url then git push origin.
        //     // WHY: cleaner structure and easier debugging.
        //     // This follows GitOps pattern: Git is source of truth, not kubectl set image.
        // }

        // stage('Install Kubectl & ArgoCD CLI Setup') {
        //     steps {
        //         sh '''
        //         echo 'installing Kubectl & ArgoCD cli...'
        //         curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
        //         chmod +x kubectl
        //         mv kubectl /usr/local/bin/kubectl
        //         curl -sSL -o /usr/local/bin/argocd https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
        //         chmod +x /usr/local/bin/argocd
        //         '''
        //     } 
        //     // simple its install kubectl and argocd cli inside jenkins agent temporary.
        //     // You can also build custom Jenkins agent image with these pre-installed.
        //     // This is shortcut way for learning purpose.
        // }

        // stage('Apply Kubernetes & Sync App with ArgoCD') {
        //     steps {
        //         script {
        //             kubeconfig(credentialsId: 'kubeconfig', serverUrl: 'https://192.168.49.2:8443') { 
        //                 sh '''
        //                 argocd login 34.45.193.5:31704 \
        //                 --username admin \
        //                 --password $(kubectl get secret -n argocd argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d) \
        //                 --insecure

        //                 argocd app sync recall-ai-agent-gcp
        //                 '''
        //             } 
        //             // Replace credentialsId with your actual Jenkins secret ID.
        //             // Replace serverUrl with value from: kubectl cluster-info
        //             // This stage completes GitOps flow:
        //             // 1. Image built & pushed
        //             // 2. deployment.yaml updated in Git
        //             // 3. ArgoCD reads Git and syncs cluster
        //         }
        //     }
        // }
    }
}