# First, ping HealthChecks.io directly to show crontab is working
response1=$(curl -fsS -m 10 --retry 5 https://hc-ping.com/2f3e0adf-4c48-44ec-b01c-5aff6c45181c)
timestamp1=$(date '+%Y-%m-%d %H:%M:%S')
echo "$timestamp1 $response1" > /home/nisheetd/healthchecks_status.txt

# Then check the Django application's health endpoint
response2=$(curl -fsS -m 10 --retry 5 http://128.2.205.118:8082/status)
timestamp2=$(date '+%Y-%m-%d %H:%M:%S')
echo "$timestamp2 $response2" > /home/nisheetd/django_health_status.txt