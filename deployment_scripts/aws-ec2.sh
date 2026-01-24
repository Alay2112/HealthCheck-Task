set -euo pipefail

REPO_URL="https://github.com/Alay2112/HealthCheck-Task.git"
APP_DIR="/home/ubuntu/HealthCheck-Task"
BRANCH="main"

echo "Updating system packages"
sudo apt-get update -y

echo "Installing prerequisites"
sudo apt-get install -y git curl ca-certificates gnupg lsb-release

echo "Installing Docker & Docker Compose plugins"
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update -y
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# after installing enabling docker service
echo "Enabling Docker service..."
sudo systemctl enable docker
sudo systemctl start docker

echo "Adding current user to docker group"
sudo usermod -aG docker "$USER" || true

echo "Cloning GitHub repo to /home/ubuntu/HealthCheck-Task"
if [ -d "$APP_DIR" ]; then
  echo "App directory already exists. Pulling latest changes..."
  cd "$APP_DIR"
  git fetch origin
  git checkout main
  git pull origin main
else
  git clone -b main "$REPO_URL" "$APP_DIR"
  cd "$APP_DIR"
fi

echo "Preparing environment files"
if [ -f "./backend/.env.example" ] && [ ! -f "./backend/.env" ]; then
  sudo cp ./backend/.env.example ./backend/.env
  echo "backend/.env is created and copied content from ./backend/.env.example"
fi

if [ -f "./frontend/.env.example" ] && [ ! -f "./frontend/.env" ]; then
  sudo cp ./frontend/.env.example ./frontend/.env
  echo "frontend/.env is created and copied content from ./frontend/.env.example"
fi

if [ -f "./.env.example"] && [ ! -f "./.env"]; then
   sudo cp ./.env.example ./.env
   echo ".env is created and copied content from .env.example"

echo "Edit .env files if needed before running production traffic"

echo "using docker compose, containers are being started"
sudo docker compose down || true
sudo docker compose build
sudo docker compose up -d

echo "Checking running containers"
sudo docker compose ps

echo "Checking if backend health doesn't fail"
sleep 10
curl -f http://localhost:8000/health || {
  echo "Health check failed. Showing logs..."
  sudo docker compose logs --tail=200 backend
  exit 1
}


echo "Frontend will be available on: http://<EC2_PUBLIC_IP>:5173"
echo "Backend health check: http://<EC2_PUBLIC_IP>:8000/health"
