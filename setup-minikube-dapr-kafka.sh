#!/bin/bash
# Script for deploying Todo AI Chatbot with Dapr and Kafka on Minikube
# Step 4: Local Deployment

set -e  # Exit on any error

echo "=== Todo AI Chatbot - Step 4: Local Deployment ==="
echo "Prerequisites: Minikube, kubectl, Helm, and Dapr CLI installed"
echo "Ensure Docker Desktop is running before starting."
echo ""

# Function to check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        echo "ERROR: Docker is not running or not accessible."
        echo "Please start Docker Desktop and run this script again."
        exit 1
    fi
    echo "✓ Docker is accessible"
}

# Function to check prerequisites
check_prerequisites() {
    echo "Checking prerequisites..."

    for cmd in minikube kubectl helm dapr; do
        if ! command -v $cmd &> /dev/null; then
            echo "ERROR: $cmd is not installed or not in PATH"
            exit 1
        fi
        echo "✓ $cmd found"
    done
}

# Function to start minikube
start_minikube() {
    echo "Starting minikube cluster..."

    if minikube status | grep -q "Stopped"; then
        minikube start --cpus=2 --memory=4096 --disk-size=20g --driver=docker
        minikube update-context
    fi

    # Wait for cluster to be ready
    kubectl wait --for=condition=Ready nodes --all --timeout=120s
    echo "✓ Minikube cluster is ready"
}

# Function to install dapr runtime
install_dapr() {
    echo "Installing Dapr runtime..."

    # Initialize dapr CLI if not done
    dapr status -k || {
        dapr init -k
    }

    # Wait for Dapr operator to be ready
    kubectl wait --for=condition=Ready pods --all -n dapr-system --timeout=180s
    echo "✓ Dapr runtime installed and ready"
}

# Function to install cert-manager (dependency for kafka operator)
install_cert_manager() {
    echo "Installing cert-manager..."

    # Check if cert-manager is already installed
    if ! helm status cert-manager &>/dev/null; then
        helm repo add jetstack https://charts.jetstack.io --force-update
        helm repo update
        helm install cert-manager jetstack/cert-manager --namespace cert-manager \
            --create-namespace --set installCRDs=true --wait --timeout=300s
    fi
    echo "✓ Cert-manager installed"
}

# Function to install Kafka (using Strimzi)
install_kafka() {
    echo "Installing Kafka using Strimzi..."

    # Check if Strimzi operator is already installed
    if ! helm status strimzi-kafka &>/dev/null; then
        helm repo add strimzi https://strimzi.io/charts/ --force-update
        helm repo update
        helm install strimzi-kafka strimzi/strimzi-kafka-operator --wait --timeout=300s
    fi

    # Create Kafka cluster
    cat <<EOF | kubectl apply -f -
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: todo-kafka-cluster
  namespace: default
spec:
  kafka:
    version: 3.6.0
    replicas: 1
    config:
      offsets.topic.replication.factor: 1
      transaction.state.log.replication.factor: 1
      transaction.state.log.min.isr: 1
      default.replication.factor: 1
      min.insync.replicas: 1
      inter.broker.protocol.version: "3.6"
    storage:
      type: jbod
      volumes:
      - id: 0
        type: persistent-claim
        size: 1Gi
        deleteClaim: false
  zookeeper:
    replicas: 1
    storage:
      type: persistent-claim
      size: 1Gi
      deleteClaim: false
  entityOperator:
    topicOperator: {}
    userOperator: {}
EOF

    echo "Waiting for Kafka cluster to be ready..."
    kubectl wait kafka/todo-kafka-cluster --for=condition=Ready --timeout=600s
    echo "✓ Kafka cluster is ready"
}

# Function to install PostgreSQL
install_postgresql() {
    echo "Installing PostgreSQL..."

    # Check if postgresql is already installed
    if ! helm status postgresql &>/dev/null; then
        helm repo add bitnami https://charts.bitnami.com/bitnami --force-update
        helm repo update

        # Install PostgreSQL with default credentials
        helm install postgresql bitnami/postgresql \
            --set auth.postgresPassword=postgres \
            --set auth.database=todoapp \
            --set persistence.enabled=true \
            --set persistence.size=1Gi \
            --wait --timeout=300s
    fi
    echo "✓ PostgreSQL installed and ready"
}

# Function to apply dapr components
apply_dapr_components() {
    echo "Applying Dapr components..."

    # Apply all Dapr components
    kubectl apply -f ./dapr-components/

    # Wait for components to be ready
    sleep 10

    # Check if all components are ready
    echo "Checking Dapr components status..."
    dapr components -k
    echo "✓ Dapr components applied"
}

# Function to create required kafka topics
create_kafka_topics() {
    echo "Creating required Kafka topics..."

    # Wait for Kafka topics CRD to be available
    kubectl wait --for=condition=Established crd/kafkatopics.kafka.strimzi.io --timeout=300s

    # Create Kafka topics for the application
    cat <<EOF | kubectl apply -f -
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-events
  labels:
    strimzi.io/cluster: todo-kafka-cluster
spec:
  partitions: 3
  replicas: 1
  config:
    retention.ms: 604800000
    compression.type: snappy
    min.insync.replicas: 1
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: reminders
  labels:
    strimzi.io/cluster: todo-kafka-cluster
spec:
  partitions: 3
  replicas: 1
  config:
    retention.ms: 604800000
    compression.type: snappy
    min.insync.replicas: 1
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-updates
  labels:
    strimzi.io/cluster: todo-kafka-cluster
spec:
  partitions: 3
  replicas: 1
  config:
    retention.ms: 86400000
    compression.type: snappy
    min.insync.replicas: 1
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-events-dlq
  labels:
    strimzi.io/cluster: todo-kafka-cluster
spec:
  partitions: 3
  replicas: 1
  config:
    retention.ms: 2592000000
    compression.type: snappy
    min.insync.replicas: 1
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: reminders-dlq
  labels:
    strimzi.io/cluster: todo-kafka-cluster
spec:
  partitions: 3
  replicas: 1
  config:
    retention.ms: 2592000000
    compression.type: snappy
    min.insync.replicas: 1
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-updates-dlq
  labels:
    strimzi.io/cluster: todo-kafka-cluster
spec:
  partitions: 3
  replicas: 1
  config:
    retention.ms: 604800000
    compression.type: snappy
    min.insync.replicas: 1
EOF

    echo "Waiting for Kafka topics to be ready..."
    sleep 30
    kubectl get kafkatopics
    echo "✓ Kafka topics created"
}

# Function to build and deploy the application
build_and_deploy_app() {
    echo "Building and deploying application images..."

    # Navigate to backend
    cd backend/

    # Build images
    docker build -t todo-app-backend:latest .
    docker build -f Dockerfile.worker -t todo-app-worker:latest .

    # For Minikube, we need to load the images into the cluster
    minikube image load todo-app-backend:latest
    minikube image load todo-app-worker:latest

    cd ..

    # Create docker registry secret if needed
    kubectl create secret docker-registry regcred \
      --docker-server=docker.io \
      --docker-username= \
      --docker-password= \
      --docker-email= \
      --dry-run=client -o yaml | kubectl apply -f -

    # Update backend and frontend charts if they exist, otherwise we'll need to create them

    # Create PostgreSQL secret
    kubectl create secret generic postgres-secrets \
      --from-literal=connectionString="postgresql://postgres:postgres@postgresql:5432/todoapp?sslmode=disable" \
      --dry-run=client -o yaml | kubectl apply -f -

    echo "✓ Images built and loaded to Minikube"

    # Install reminder worker first
    echo "Deploying reminder worker..."
    helm upgrade --install reminder-worker ./charts/reminder-worker/ --wait --timeout=600s

    echo "✓ Reminder worker deployed"

    # Here we would deploy backend and frontend if their charts exist
    # For now, deploying only the reminder worker
}

# Function to create and apply ingress
apply_ingress() {
    echo "Setting up ingress to access services..."

    # Enable ingress addon
    if ! minikube addons list | grep -q "^ingress.*enabled"; then
        minikube addons enable ingress
    fi

    echo "✓ Ingress enabled"
}

# Function to setup and show URLs
show_urls() {
    echo ""
    echo "=== Deployment Completed Successfully ==="
    echo "Services are deployed. Use the following URLs:"
    echo "- Minikube Dashboard: Run 'minikube dashboard'"
    echo "- Frontend: http://$(minikube ip):3000"  # Once frontend is set up
    echo ""
    echo "To check pod status: kubectl get pods"
    echo "To view logs: kubectl logs <pod-name>"
    echo ""
    echo "To port forward for local access:"
    echo "kubectl port-forward svc/<service-name> <local-port>:80"
    echo ""
    echo "Dapr components status: dapr components -k"
    echo "Kafka topics: kubectl get kafkatopics"
    echo "==========================="
}

# Main execution flow
main() {
    echo "Starting deployment of Todo AI Chatbot with Dapr and Kafka..."
    echo "======================================="

    check_docker
    check_prerequisites
    start_minikube
    install_dapr
    install_cert_manager
    install_kafka
    install_postgresql
    create_kafka_topics
    apply_dapr_components
    build_and_deploy_app
    apply_ingress

    sleep 20  # Give extra time for all services to start

    show_urls
    echo ""
    echo "🎉 Deployment Complete!"
}

main "$@"