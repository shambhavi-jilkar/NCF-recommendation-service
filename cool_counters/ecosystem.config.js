module.exports = {
  apps: [
    {
      name: 'cool_counter', // Name of your application
      script: '/home/nisheetd/group-project-s25-the_call_of_the_wild/cool_counters/manage.py', // Path to manage.py
      args: 'runserver 128.2.205.118:8082', // Command to run the Django development server
      interpreter: '/home/nisheetd/anaconda3/envs/mlip-project/bin/python3.12', // Path to the Python interpreter
      exec_mode: 'fork', // Mode to run the app (single instance)
      autorestart: true, // Automatically restart if the app crashes
      watch: false, // Disable watching for file changes in production
      max_memory_restart: '1G', // Restart if memory usage exceeds 1GB
      env: {
        DJANGO_SETTINGS_MODULE: 'cool_counters.settings', // Replace with your settings module
        PYTHONUNBUFFERED: '1',
      },
    },
  ],
};